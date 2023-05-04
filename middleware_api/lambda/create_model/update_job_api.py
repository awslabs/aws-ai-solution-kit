import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError

from common.ddb_service.client import DynamoDbUtilsService
from common.stepfunction_service.client import StepFunctionUtilsService
from common.util import publish_msg
from _types import ModelJob, CreateModelStatus, CheckPoint, CheckPointStatus
from common_tools import complete_mulipart_upload, split_s3_path
from create_model_async_job import create_sagemaker_inference

bucket_name = os.environ.get('S3_BUCKET')
model_table = os.environ.get('DYNAMODB_TABLE')
checkpoint_table = os.environ.get('CHECKPOINT_TABLE')


success_topic_arn = os.environ.get('SUCCESS_TOPIC_ARN')
error_topic_arn = os.environ.get('ERROR_TOPIC_ARN')
user_topic_arn = os.environ.get('USER_TOPIC_ARN')

logger = logging.getLogger('boto3')
ddb_service = DynamoDbUtilsService(logger=logger)
stepfunctions_client = StepFunctionUtilsService(logger=logger)


@dataclass
class Event:
    model_id: str
    status: str
    multi_parts_tags: Dict[str, Any]


# PUT /model
def update_model_job_api(raw_event, context):
    event = Event(**raw_event)

    try:
        raw_training_job = ddb_service.get_item(table=model_table, key_values={'id': event.model_id})
        if raw_training_job is None:
            return {
                'statusCode': 200,
                'error': f'create model with id {event.model_id} is not found'
            }

        model_job = ModelJob(**raw_training_job)
        resp = train_job_exec(model_job, CreateModelStatus[event.status])
        ddb_service.update_item(
            table=model_table,
            key={'id': event.model_id},
            field_name='job_status',
            value=event.status
        )
        raw_checkpoint = ddb_service.get_item(table=checkpoint_table, key_values={
            'id': model_job.checkpoint_id
        })
        if raw_checkpoint is None:
            return {
                'status': 500,
                'error': f'create model ckpt with id {event.model_id} is not found'
            }

        ckpt = CheckPoint(**raw_checkpoint)
        complete_mulipart_upload(ckpt, event.multi_parts_tags)
        return resp
    except ClientError as e:
        logger.error(e)
        return {
            'statusCode': 200,
            'error': str(e)
        }


# SNS callback
def process_result(event, context):
    records = event['Records']
    for record in records:
        msg_str = record['Sns']['Message']
        print(msg_str)
        msg = json.loads(msg_str)
        inference_id = msg['inferenceId']

        model_job_raw = ddb_service.get_item(table=model_table, key_values={'id': inference_id})
        if model_job_raw is None:
            return {
                'statusCode': '500',
                'error': f'id with {inference_id} not found'
            }
        job = ModelJob(**model_job_raw)

        if record['Sns']['TopicArn'] == success_topic_arn:
            resp_location = msg['responseParameters']['outputLocation']
            bucket, key = split_s3_path(resp_location)
            content = get_object(bucket=bucket, key=key)
            if content['statusCode'] != 200:
                ddb_service.update_item(
                    table=model_table,
                    key={'id': inference_id},
                    field_name='job_status',
                    value=CreateModelStatus.Fail.value
                )
                publish_msg(
                    topic_arn=user_topic_arn,
                    subject=f'Create Model Job {job.name}: {job.id} failed',
                    msg='to be done'
                )  # todo: find out msg
                return

            msgs = content['message']
            job.params['resp'] = {}
            for key, val in msgs.items():
                job.params['resp'][key] = val

            ddb_service.update_item(
                table=model_table,
                key={'id': inference_id},
                field_name='job_status',
                value=CreateModelStatus.Complete.value
            )
            params = model_job_raw['params']
            params['resp']['s3_output_location'] = f'{bucket_name}/{job.model_type}/{job.name}.tar'
            ddb_service.update_item(
                table=model_table,
                key={'id': inference_id},
                field_name='params',
                value=params
            )

            publish_msg(
                topic_arn=user_topic_arn,
                subject=f'Create Model Job {job.name}: {job.id} success',
                msg=f'model {job.name}: {job.id} is ready to use'
            )  # todo: find out msg

        if record['Sns']['TopicArn'] == error_topic_arn:
            ddb_service.update_item(
                table=model_table,
                key={'id': inference_id},
                field_name='job_status',
                value=CreateModelStatus.Fail.value
            )
            publish_msg(
                topic_arn=user_topic_arn,
                subject=f'Create Model Job {job.name}: {job.id} failed',
                msg='to be done'
            )  # todo: find out msg
    return {
        'statusCode': 200,
        'msg': f'finished events {event}'
    }


def get_object(bucket: str, key: str):
    s3_client = boto3.client('s3')
    data = s3_client.get_object(Bucket=bucket, Key=key)
    content = json.load(data['Body'])
    return content





def train_job_exec(model_job: ModelJob, action: CreateModelStatus):
    if model_job.job_status == CreateModelStatus.Creating and \
            (action != CreateModelStatus.Fail or action != CreateModelStatus.Complete):
        raise Exception(f'model creation job is currently under progress, so cannot be updated')

    if action == CreateModelStatus.Creating:
        model_job.job_status = action
        raw_chkpt = ddb_service.get_item(table=checkpoint_table, key_values={'id': model_job.checkpoint_id})
        if raw_chkpt is None:
            return {
                'statusCode': 200,
                'error': f'model related checkpoint with id {model_job.checkpoint_id} is not found'
            }

        checkpoint = CheckPoint(**raw_chkpt)
        checkpoint.checkpoint_status = CheckPointStatus.Active
        ddb_service.update_item(
            table=checkpoint_table,
            key={'id': checkpoint.id},
            field_name='checkpoint_status',
            value=CheckPointStatus.Active.value
        )
        return create_sagemaker_inference(job=model_job, checkpoint=checkpoint)
    elif action == CreateModelStatus.Initial:
        raise Exception('please create a new model creation job for this,'
                        f' not allowed overwrite old model creation job')
    else:
        # todo: other action
        raise NotImplemented
