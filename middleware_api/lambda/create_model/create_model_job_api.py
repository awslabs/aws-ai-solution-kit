import dataclasses
import datetime
import logging
import os
from typing import Any

from botocore.exceptions import ClientError

from common.ddb_service.client import DynamoDbUtilsService
from _types import ModelJob, CreateModelStatus, CheckPoint, CheckPointStatus
from common_tools import get_s3_presign_urls

bucket_name = os.environ.get('S3_BUCKET')
model_table = os.environ.get('DYNAMODB_TABLE')
checkpoint_table = os.environ.get('CHECKPOINT_TABLE')

logger = logging.getLogger('boto3')
ddb_service = DynamoDbUtilsService(logger=logger)


@dataclasses.dataclass
class Event:
    model_type: str
    name: str
    params: dict[str, Any]
    filenames: [str]
    # todo: checkpoint_id (if checkpoint id, then using checkpoint id to do instead of filenames)

# POST /model
def create_model_api(raw_event, context):
    request_id = context.aws_request_id
    event = Event(**raw_event)
    _type = event.model_type

    try:
        # todo: check if duplicated name and new_model_name

        base_key = f'{_type}/model/{event.name}/{request_id}'
        presign_url_map = get_s3_presign_urls(bucket_name=bucket_name, base_key=base_key, filenames=event.filenames)

        checkpoint = CheckPoint(
            id=request_id,
            s3_location=f's3://{bucket_name}/{base_key}/checkpoint',  # e.g. s3://bucket/dreambooth/123-123-123
            checkpoint_names=event.filenames,
            checkpoint_status=CheckPointStatus.Initial,
            params={
                'created': str(datetime.datetime.now())
            }
        )
        ddb_service.put_items(table=checkpoint_table, entries=checkpoint.__dict__)

        model_job = ModelJob(
            id=request_id,
            name=event.name,
            output_s3_location=f's3://{bucket_name}/{base_key}/output',
            checkpoint_id=checkpoint.id,
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
            's3_base': checkpoint.s3_location,
            'model_type': model_job.model_type,
            'params': model_job.params  # not safe if not json serializable type
        },
        's3PresignUrl':  presign_url_map
    }


# GET /models
def list_all_models_api(event, context):
    resp = ddb_service.scan(table=model_table, filters={
        'job_status': CreateModelStatus.Complete,
        'model_type': 'dreambooth'
    })
    if resp is None or len(resp) == 0:
        return {
            'statusCode': 200,
            'models': []
        }

    models = []

    for r in resp:
        model = ModelJob(**(ddb_service.deserialize(r)))
        name = model.name
        models.append({
            'id': model.id,
            'model_name': name,
            'params': model.params
        })
    return {
        'statusCode': 200,
        'models': models
    }


# GET /checkpoints
def list_all_checkpoints_api(event, context):
    raw_ckpts = ddb_service.scan(table=checkpoint_table, filters={
        'checkpoint_status': CheckPointStatus.Active
    })
    if raw_ckpts is None or len(raw_ckpts) == 0:
        return {
            'statusCode': 200,
            'body': []
        }

    ckpts = []

    for r in raw_ckpts:
        ckpt = CheckPoint(**(ddb_service.deserialize(r)))
        ckpts.append({
            'id': ckpt.id,
            'name': ckpt.s3_location,
            'checkpoints': ckpt.checkpoint_names
        })

    return {
        'statusCode': 200,
        'checkpoints': ckpts
    }
