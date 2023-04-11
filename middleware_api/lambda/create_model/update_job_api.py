import logging
import os
from dataclasses import dataclass

from botocore.exceptions import ClientError

from common.ddb_service.client import DynamoDbUtilsService
from create_model._types import TrainingJob, CreateModelStatus

bucket_name = os.environ.get('S3_BUCKET')
train_table = os.environ.get('DYNAMODB_TABLE')

logger = logging.getLogger('boto3')
ddb_service = DynamoDbUtilsService(logger=logger)


@dataclass
class Event:
    model_id: str
    status: str


def update_train_job_api(raw_event, context):
    event = Event(**raw_event)

    try:
        raw_training_job = ddb_service.get_item(table=train_table, key_values={'id': event.model_id})
        if raw_training_job is None:
            return {
                'statusCode': 200,
                'error': f'training model with id {event.model_id} is not found'
            }

        train_job = TrainingJob(**raw_training_job)
        train_job_exec(train_job, CreateModelStatus[event.status])

        ddb_service.update_item(
            table=train_table,
            key={'id': event.model_id},
            field_name='job_status',
            value=event.status
        )

    except ClientError as e:
        logger.error(e)
        return {
            'statusCode': 200,
            'error': str(e)
        }

    return {
        'statusCode': 200,
        'trainJob': {
            'id': train_job.id,
            'status': train_job.job_status.value,
            's3_base': train_job.s3_location,
            'model_type': train_job.model_type,
            'sagemaker_id': train_job.sagemaker_job_id
        }
    }


def train_job_exec(train_job: TrainingJob, action: CreateModelStatus):
    if train_job.job_status == CreateModelStatus.Train and \
            (action != CreateModelStatus.Fail or action != CreateModelStatus.Complete):
        raise Exception(f'training job is currently under training, so cannot be updated')

    if action == CreateModelStatus.Train:
        # todo: start train
        return
    elif action == CreateModelStatus.Initial:
        raise Exception(f'please create a new train job for this, not allowed overwrite old training jobs')
    else:
        # todo: other action
        return
