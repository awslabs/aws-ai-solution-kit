import json
import logging
import os
import base64
import time
from dataclasses import dataclass

from typing import Any
import sagemaker
from botocore.config import Config

from common.ddb_service.client import DynamoDbUtilsService
from common.stepfunction_service.client import StepFunctionUtilsService
from common.util import publish_msg
from common_tools import get_s3_presign_urls, split_s3_path
from _types import TrainJob, TrainJobStatus, ModelJob, CreateModelStatus, CheckPoint, CheckPointStatus
from create_model_async_job import DecimalEncoder

bucket_name = os.environ.get('S3_BUCKET')
train_table = os.environ.get('TRAIN_TABLE')
model_table = os.environ.get('MODEL_TABLE')
checkpoint_table = os.environ.get('CHECKPOINT_TABLE')
instance_type = os.environ.get('INSTANCE_TYPE')
sagemaker_role_arn = os.environ.get('TRAIN_JOB_ROLE')
image_uri = os.environ.get('TRAIN_ECR_URL')  # e.g. "648149843064.dkr.ecr.us-east-1.amazonaws.com/dreambooth-training-repo"
training_stepfunction_arn = os.environ.get('TRAINING_SAGEMAKER_ARN')
user_topic_arn = os.environ.get('USER_EMAIL_TOPIC_ARN')

logger = logging.getLogger('boto3')
ddb_service = DynamoDbUtilsService(logger=logger)


@dataclass
class Event:
    train_type: str
    model_id: str
    params: dict[str, Any]
    filenames: [str]


# POST /train
def create_train_job_api(raw_event, context):
    request_id = context.aws_request_id
    event = Event(**raw_event)
    _type = event.train_type

    try:
        model_raw = ddb_service.get_item(table=model_table, key_values={
            'id': event.model_id
        })
        if model_raw is None:
            return {
                'statusCode': 500,
                'error': f'model with id {event.model_id} is not found'
            }

        model = ModelJob(**model_raw)
        if model.job_status != CreateModelStatus.Complete:
            return {
                'statusCode': 500,
                'error': f'model {model.id} is in {model.job_status.value} state, not valid to be used for train'
            }

        base_key = f'{_type}/train/{model.name}/{request_id}'
        input_location = f'{base_key}/input'
        presign_url_map = get_s3_presign_urls(bucket_name=bucket_name, base_key=input_location, filenames=event.filenames)

        checkpoint = CheckPoint(
            id=request_id,
            checkpoint_type=event.train_type,
            s3_location=f's3://{bucket_name}/{base_key}/output',
            checkpoint_status=CheckPointStatus.Initial
        )
        ddb_service.put_items(table=checkpoint_table, entries=checkpoint.__dict__)

        train_job = TrainJob(
            id=request_id,
            model_id=event.model_id,
            job_status=TrainJobStatus.Initial,
            params=event.params,
            train_type=event.train_type,
            input_s3_location=f's3://{bucket_name}/{input_location}',
            checkpoint_id=checkpoint.id,
        )
        ddb_service.put_items(table=train_table, entries=train_job.__dict__)

        return {
            'statusCode': 200,
            'job': {
                'id': train_job.id,
                'status': train_job.job_status.value,
                'trainType': train_job.train_type,
                'params': train_job.params
            },
            's3PresignUrl': presign_url_map
        }
    except Exception as e:
        logger.error(e)
        return {
            'statusCode': 200,
            'error': str(e)
        }


# GET /trains
def list_all_train_jobs_api(event, context):
    raise NotImplemented


# PUT /train used to kickoff a train job step function
def update_train_job_api(event, context):
    if 'status' in event and 'train_job_id' in event and event['status'] == TrainJobStatus.Training.value:
        return _start_train_job(event['train_job_id'])

    return {
        'statusCode': 200,
        'msg': f'not implemented for train job status {event["status"]}'
    }


def _start_train_job(train_job_id: str):
    raw_train_job = ddb_service.get_item(table=train_table, key_values={
        'id': train_job_id
    })
    if raw_train_job is None or len(raw_train_job) == 0:
        return {
            'statusCode': 500,
            'error': f'no such train job with id({train_job_id})'
        }

    train_job = TrainJob(**raw_train_job)

    model_raw = ddb_service.get_item(table=model_table, key_values={
        'id': train_job.model_id
    })
    if model_raw is None:
        return {
            'statusCode': 500,
            'error': f'model with id {train_job.model_id} is not found'
        }

    model = ModelJob(**model_raw)

    raw_checkpoint = ddb_service.get_item(table=checkpoint_table, key_values={
        'id': train_job.checkpoint_id
    })
    if raw_checkpoint is None:
        return {
            'statusCode': 500,
            'error': f'checkpoint with id {train_job.checkpoint_id} is not found'
        }

    checkpoint = CheckPoint(**raw_checkpoint)

    try:
        # JSON encode hyperparameters
        def json_encode_hyperparameters(hyperparameters):
            new_params = {}
            for k, v in hyperparameters.items():
                json_v = json.dumps(v, cls=DecimalEncoder)
                v_bytes = json_v.encode('ascii')
                base64_bytes = base64.b64encode(v_bytes)
                base64_v = base64_bytes.decode('ascii')
                new_params[k] = base64_v
            return new_params

        hyperparameters = json_encode_hyperparameters({
            "sagemaker_program": "extensions/sd-webui-sagemaker/sagemaker_entrypoint_json.py",
            "params": train_job.params,
            "s3-input-path": train_job.input_s3_location,
            "s3-output-path": checkpoint.s3_location,
        })

        est = sagemaker.estimator.Estimator(
            image_uri,
            sagemaker_role_arn,
            instance_count=1,
            instance_type=instance_type,
            volume_size=125,
            base_job_name=f'{model.name}',
            hyperparameters=hyperparameters,
            job_id=train_job.id,
        )
        est.fit(wait=False)

        while not est._current_job_name:
            time.sleep(1)

        train_job.sagemaker_train_name = est._current_job_name
        # trigger stepfunction
        stepfunctions_client = StepFunctionUtilsService(logger=logger)
        sfn_input = {
            'train_job_id': train_job.id,
            'train_job_name': train_job.sagemaker_train_name
        }
        sfn_arn = stepfunctions_client.invoke_step_function(training_stepfunction_arn, sfn_input)
        # todo: use batch update, this is ugly!!!
        search_key = {'id': train_job.id}
        ddb_service.update_item(
            table=train_table,
            key=search_key,
            field_name='sagemaker_train_name',
            value=est._current_job_name
        )
        train_job.job_status = TrainJobStatus.Training
        ddb_service.update_item(
            table=train_table,
            key=search_key,
            field_name='job_status',
            value=TrainJobStatus.Training.value
        )
        train_job.sagemaker_sfn_arn = sfn_arn
        ddb_service.update_item(
            table=train_table,
            key=search_key,
            field_name='sagemaker_sfn_arn',
            value=sfn_arn
        )

        return {
            'statusCode': 200,
            'job': {
                'id': train_job.id,
                'status': train_job.job_status.value,
                'trainType': train_job.train_type,
                'params': train_job.params,
                'input_location': train_job.input_s3_location
            },
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'error': str(e)
        }


# sfn
def check_train_job_status(event, context):
    import boto3
    boto3_sagemaker = boto3.client('sagemaker')
    train_job_name = event['train_job_name']
    train_job_id = event['train_job_id']

    resp = boto3_sagemaker.describe_training_job(
        TrainingJobName=train_job_name
    )

    training_job_status = resp['TrainingJobStatus']
    event['status'] = training_job_status

    raw_train_job = ddb_service.get_item(table=train_table, key_values={
        'id': train_job_id,
    })

    if raw_train_job is None or len(raw_train_job) == 0:
        event['status'] = 'Failed'
        return {
            'statusCode': 500,
            'msg': f'no such training job find in ddb id[{train_job_id}]'
        }

    training_job = TrainJob(**raw_train_job)
    if training_job_status == 'InProgress' or training_job_status == 'Stopping':
        return event

    if training_job_status == 'Failed' or training_job_status == 'Stopped':
        training_job.job_status = TrainJobStatus.Fail
        if 'FailureReason' in resp:
            err_msg = resp['FailureReason']
            training_job.params['resp'] = {
                'status': 'Failed',
                'error_msg': err_msg,
                'raw_resp': resp
            }

    if training_job_status == 'Completed':
        training_job.job_status = TrainJobStatus.Complete
        # todo: update checkpoints
        raw_checkpoint = ddb_service.get_item(table=checkpoint_table, key_values={
            'id': training_job.checkpoint_id
        })
        if raw_checkpoint is None or len(raw_checkpoint) == 0:
            # todo: or create new one
            return 'failed because no checkpoint, not normal'

        checkpoint = CheckPoint(**raw_checkpoint)
        checkpoint.checkpoint_status = CheckPointStatus.Active
        ddb_service.update_item(
            table=checkpoint_table,
            key={
                'id': checkpoint.id
            },
            field_name='checkpoint_status',
            value=checkpoint.checkpoint_status.value
        )
        s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
        bucket, key = split_s3_path(checkpoint.s3_location)
        s3_resp = s3.list_objects(
            Bucket=bucket,
            Prefix=key,
        )
        checkpoint.checkpoint_names = []
        for obj in s3_resp['Contents']:
            checkpoint.checkpoint_names.append(obj['Key'].replace(f'{key}/', ""))

        ddb_service.update_item(
            table=checkpoint_table,
            key={
                'id': checkpoint.id
            },
            field_name='checkpoint_names',
            value=checkpoint.checkpoint_names
        )

        training_job.params['resp'] = {
            'status': 'Failed',
            'raw_resp': resp
        }

    # fixme: this is ugly
    ddb_service.update_item(
        table=train_table,
        key={'id': train_job_id},
        field_name='job_status',
        value=training_job.job_status.value
    )

    ddb_service.update_item(
        table=train_table,
        key={'id': train_job_id},
        field_name='params',
        value=training_job.params
    )

    return event


# sfn
def process_train_job_result(event, context):
    train_job_id = event['train_job_id']

    raw_train_job = ddb_service.get_item(table=train_table, key_values={
        'id': train_job_id,
    })

    if raw_train_job is None or len(raw_train_job) == 0:
        return {
            'statusCode': 500,
            'msg': f'no such training job find in ddb id[{train_job_id}]'
        }

    train_job = TrainJob(**raw_train_job)

    publish_msg(
        topic_arn=user_topic_arn,
        subject=f'Create Model Job {train_job.sagemaker_train_name} {train_job.job_status}',
        msg=f'to be done with resp: \n {train_job.job_status}'
    )  # todo: find out msg

    return 'job completed'
