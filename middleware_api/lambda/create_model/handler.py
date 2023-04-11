import dataclasses
import logging
import os

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from common.ddb_service.client import DynamoDbUtilsService
from create_model._types import Model, CreateModelStatus

bucket_name = os.environ.get('S3_BUCKET')
train_table = os.environ.get('DYNAMODB_TABLE')

logger = logging.getLogger('boto3')
ddb_service = DynamoDbUtilsService(logger=logger)


@dataclasses.dataclass
class Event:
    model_type: str
    name: str
    filename: str


def handler(raw_event, context):
    s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
    request_id = context.aws_request_id
    event = Event(**raw_event)
    _type = event.model_type

    try:
        key = f'{_type}/{request_id}/{event.filename}'
        url = s3.generate_presigned_url('put_object',
                                        Params={'Bucket': bucket_name,
                                                'Key': key,
                                                },
                                        ExpiresIn=3600 * 24 * 7)
        model = Model(
            id=request_id,
            s3_location=f's3://{bucket_name}/{key}',
            model_type=_type,
            status=CreateModelStatus.Initial
        )
        ddb_service.put_items(table=train_table, entries=model.__dict__)
    except ClientError as e:
        print(e)
        return None

    return {
        'statusCode': 200,
        'body': url
    }
