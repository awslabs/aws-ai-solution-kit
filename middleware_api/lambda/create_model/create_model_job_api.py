import dataclasses
import logging
import os
from typing import Any
import json

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from common.ddb_service.client import DynamoDbUtilsService
from create_model._types import ModelJob, CreateModelStatus

bucket_name = os.environ.get('S3_BUCKET')
model_table = os.environ.get('DYNAMODB_TABLE')

logger = logging.getLogger('boto3')
ddb_service = DynamoDbUtilsService(logger=logger)


@dataclasses.dataclass
class Event:
    model_type: str
    name: str
    params: dict[str, Any]
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

        model_job = ModelJob(
            id=request_id,
            s3_location=f's3://{bucket_name}/{base_key}',
            model_type=_type,
            job_status=CreateModelStatus.Initial,
            params=event.params
        )
        ddb_service.put_items(table=model_table, entries=model_job.__dict__)
    except ClientError as e:
        logger.error(e)
        return {
            'statusCode': 200,
            'error': str(e)
        }

    return {
        'statusCode': 200,
        'job': {
            'id': model_job.id,
            'status': model_job.job_status.value,
            's3_base': model_job.s3_location,
            'model_type': model_job.model_type,
            'params': model_job.params  # not safe if not json serializable type
        },
        's3PresignUrl':  presign_url_map
    }


def list_all_models_api(event, context):
    resp = ddb_service.scan(table=model_table, filters={
        'job_status': CreateModelStatus.Complete,
        'model_type': 'dreambooth'
    })
    if resp is None or len(resp) == 0:
        return {
            'statusCode': 200,
            'body': []
        }

    models = []

    for r in resp:
        model = ModelJob(**(ddb_service.deserialize(r)))
        name = model.id
        if model.params is not None and 'new_model_name' in model.params:
            name = model.params['new_model_name']

        models.append({
            'id': model.id,
            'model_name': name
        })

    return {
        'statusCode': 200,
        'models': models
    }
