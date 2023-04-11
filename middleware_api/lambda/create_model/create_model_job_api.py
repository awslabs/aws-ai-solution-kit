import dataclasses
import logging
import os

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from common.ddb_service.client import DynamoDbUtilsService
from create_model._types import TrainingJob, CreateModelStatus

bucket_name = os.environ.get('S3_BUCKET')
train_table = os.environ.get('DYNAMODB_TABLE')

logger = logging.getLogger('boto3')
ddb_service = DynamoDbUtilsService(logger=logger)


@dataclasses.dataclass
class Event:
    model_type: str
    name: str
    filenames: [str]


def create_model_api(raw_event, context):
    request_id = context.aws_request_id
    event = Event(**raw_event)
    _type = event.model_type

    try:
        s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
        presign_url_map = {}
        base_key = f'{_type}/{request_id}/{event.name}'
        for filename in event.filenames:
            key = f'{base_key}/{filename}'
            url = s3.generate_presigned_url('put_object',
                                            Params={'Bucket': bucket_name,
                                                    'Key': key,
                                                    },
                                            ExpiresIn=3600 * 24 * 7)
            presign_url_map[filename] = url

        training_job = TrainingJob(
            id=request_id,
            s3_location=f's3://{bucket_name}/{base_key}',
            model_type=_type,
            job_status=CreateModelStatus.Initial
        )
        ddb_service.put_items(table=train_table, entries=training_job.__dict__)
    except ClientError as e:
        logger.error(e)
        return {
            'statusCode': 200,
            'error': str(e)
        }

    return {
        'statusCode': 200,
        'trainJob': {
            'id': training_job.id,
            'status': training_job.job_status.value,
            's3_base': training_job.s3_location,
            'model_type': training_job.model_type,
        },
        's3PresignUrl':  presign_url_map
    }
