import dataclasses
import datetime
import logging
import os
from typing import Any

from botocore.exceptions import ClientError

from common.ddb_service.client import DynamoDbUtilsService
from _types import ModelJob, CreateModelStatus, CheckPoint, CheckPointStatus, MultipartFileReq
from common_tools import get_base_model_s3_key, get_base_checkpoint_s3_key, \
    batch_get_s3_multipart_signed_urls

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
    filenames: [MultipartFileReq]


# POST /model
def create_model_api(raw_event, context):
    request_id = context.aws_request_id
    event = Event(**raw_event)
    _type = event.model_type

    try:
        # todo: check if duplicated name and new_model_name only for Completed and Model

        base_key = get_base_model_s3_key(_type, event.name, request_id)
        checkpoint_base_key = get_base_checkpoint_s3_key(_type, event.name, request_id)
        presign_url_map = batch_get_s3_multipart_signed_urls(
            bucket_name=bucket_name,
            base_key=checkpoint_base_key,
            filenames=event.filenames
        )
        filenames_only = []
        for f in event.filenames:
            file = MultipartFileReq(**f)
            filenames_only.append(file.filename)

        checkpoint_params = {'created': str(datetime.datetime.now()), 'multipart_upload': {
        }}
        multiparts_resp = {}
        for key, val in presign_url_map.items():
            checkpoint_params['multipart_upload'][key] = {
                'upload_id': val['upload_id'],
                'bucket': val['bucket'],
                'key': val['key'],
            }
            multiparts_resp[key] = val['s3_signed_urls']

        checkpoint = CheckPoint(
            id=request_id,
            checkpoint_type=event.model_type,
            s3_location=f's3://{bucket_name}/{get_base_checkpoint_s3_key(_type, event.name, request_id)}',
            checkpoint_names=filenames_only,
            checkpoint_status=CheckPointStatus.Initial,
            params=checkpoint_params
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
        's3PresignUrl':  multiparts_resp
    }


# GET /models
def list_all_models_api(event, context):
    _filter = {}
    if 'queryStringParameters' not in event:
        return {
            'statusCode': '500',
            'error': 'query parameter status and types are needed'
        }
    parameters = event['queryStringParameters']
    if 'types' in parameters and len(parameters['types']) > 0:
        _filter['model_type'] = parameters['types']

    if 'status' in parameters and len(parameters['status']) > 0:
        _filter['job_status'] = parameters['status']
    resp = ddb_service.scan(table=model_table, filters=_filter)

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
            'params': model.params,
            'status': model.job_status.value,
            'output_s3_location': model.output_s3_location
        })
    return {
        'statusCode': 200,
        'models': models
    }


