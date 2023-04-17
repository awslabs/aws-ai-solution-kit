import json
import logging
import os
from dataclasses import dataclass

import boto3
from botocore.exceptions import ClientError

from common.ddb_service.client import DynamoDbUtilsService
from common.stepfunction_service.client import StepFunctionUtilsService
from common.util import publish_msg
from create_model._types import ModelJob, CreateModelStatus
from create_model.create_model_async_job import create_sagemaker_inference

bucket_name = os.environ.get('S3_BUCKET')
model_table = os.environ.get('DYNAMODB_TABLE')


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


def update_train_job_api(raw_event, context):
    event = Event(**raw_event)

    try:
        raw_training_job = ddb_service.get_item(table=model_table, key_values={'id': event.model_id})
        if raw_training_job is None:
            return {
                'statusCode': 200,
                'error': f'training model with id {event.model_id} is not found'
            }

        model_job = ModelJob(**raw_training_job)
        resp = train_job_exec(model_job, CreateModelStatus[event.status])

        ddb_service.update_item(
            table=model_table,
            key={'id': event.model_id},
            field_name='job_status',
            value=event.status
        )
        return resp
    except ClientError as e:
        logger.error(e)
        return {
            'statusCode': 200,
            'error': str(e)
        }


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
            ddb_service.update_item(
                table=model_table,
                key={'id': inference_id},
                field_name='job_status',
                value=CreateModelStatus.Complete.value
            )
            params = model_job_raw['params']
            params['s3_output_location'] = f'{bucket_name}/{job.model_type}/{job.params["new_model_name"]}.tar'
            ddb_service.update_item(
                table=model_table,
                key={'id': inference_id},
                field_name='params',
                value=params
            )

            publish_msg(
                topic_arn=user_topic_arn,
                subject=f'Create Model Job {job.params["new_model_name"]} success',
                msg=f'model {job.params["new_model_name"]} is ready to use'
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
                subject=f'Create Model Job {job.params["new_model_name"]} failed',
                msg='to be done'
            )  # todo: find out msg
    return {
        'statusCode': 200,
        'msg': f'finished events {event}'
    }


def train_job_exec(model_job: ModelJob, action: CreateModelStatus):
    if model_job.job_status == CreateModelStatus.Creating and \
            (action != CreateModelStatus.Fail or action != CreateModelStatus.Complete):
        raise Exception(f'model creation job is currently under progress, so cannot be updated')

    if action == CreateModelStatus.Creating:
        model_job.job_status = action
        return create_sagemaker_inference(job=model_job)
    elif action == CreateModelStatus.Initial:
        raise Exception('please create a new model creation job for this,'
                        f' not allowed overwrite old model creation job')
    else:
        # todo: other action
        return
