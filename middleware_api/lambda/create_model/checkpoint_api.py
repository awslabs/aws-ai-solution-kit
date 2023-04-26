import datetime
import logging
import os
from dataclasses import dataclass
from typing import Any, Optional, Dict


from _types import CheckPoint, CheckPointStatus, MultipartFileReq
from common.ddb_service.client import DynamoDbUtilsService
from create_model.common_tools import get_base_checkpoint_s3_key, get_s3_presign_urls, \
    batch_get_s3_multipart_signed_urls, complete_mulipart_upload

checkpoint_table = os.environ.get('CHECKPOINT_TABLE')
bucket_name = os.environ.get('S3_BUCKET')

logger = logging.getLogger('boto3')
ddb_service = DynamoDbUtilsService(logger=logger)


# GET /checkpoints
def list_all_checkpoints_api(event, context):
    _filter = {}
    if 'queryStringParameters' not in event:
        return {
            'statusCode': '500',
            'error': 'query parameter status and types are needed'
        }
    parameters = event['queryStringParameters']
    if 'types' in parameters and len(parameters['types']) > 0:
        _filter['checkpoint_type'] = parameters['types']

    if 'status' in parameters and len(parameters['status']) > 0:
        _filter['checkpoint_status'] = parameters['status']

    raw_ckpts = ddb_service.scan(table=checkpoint_table, filters=_filter)
    if raw_ckpts is None or len(raw_ckpts) == 0:
        return {
            'statusCode': 200,
            'checkpoints': []
        }

    ckpts = []

    for r in raw_ckpts:
        ckpt = CheckPoint(**(ddb_service.deserialize(r)))
        ckpts.append({
            'id': ckpt.id,
            's3Location': ckpt.s3_location,
            'type': ckpt.checkpoint_type,
            'status': ckpt.checkpoint_status.value,
            'name': ckpt.checkpoint_names
        })

    return {
        'statusCode': 200,
        'checkpoints': ckpts
    }


@dataclass
class CreateCheckPointEvent:
    checkpoint_type: str
    # filenames: [str]
    filenames: [MultipartFileReq]
    params: dict[str, Any]


# POST /checkpoint
def create_checkpoint_api(raw_event, context):
    request_id = context.aws_request_id
    event = CreateCheckPointEvent(**raw_event)
    _type = event.checkpoint_type

    try:
        base_key = get_base_checkpoint_s3_key(_type, 'custom', request_id)
        presign_url_map = batch_get_s3_multipart_signed_urls(
            bucket_name=bucket_name,
            base_key=base_key,
            filenames=event.filenames
        )

        checkpoint_params = {}
        if event.params is not None and len(event.params) > 0:
            checkpoint_params = event.params

        checkpoint_params['created'] = str(datetime.datetime.now())
        checkpoint_params['multipart_upload'] = {}
        multiparts_resp = {}
        for key, val in presign_url_map.items():
            checkpoint_params['multipart_upload'][key] = {
                'upload_id': val['upload_id'],
                'bucket': val['bucket'],
                'key': val['key'],
            }
            multiparts_resp[key] = val['s3_signed_urls']

        filenames_only = []
        for f in event.filenames:
            file = MultipartFileReq(**f)
            filenames_only.append(file.filename)

        checkpoint = CheckPoint(
            id=request_id,
            checkpoint_type=_type,
            s3_location=f's3://{bucket_name}/{base_key}',
            checkpoint_names=filenames_only,
            checkpoint_status=CheckPointStatus.Initial,
            params=checkpoint_params,
        )
        ddb_service.put_items(table=checkpoint_table, entries=checkpoint.__dict__)
        return {
            'statusCode': 200,
            'checkpoint': {
                'id': request_id,
                'type': _type,
                's3_location': checkpoint.s3_location,
                'status': checkpoint.checkpoint_status.value,
                'params': checkpoint.params
            },
            's3PresignUrl': multiparts_resp
        }
    except Exception as e:
        logger.error(e)
        return {
            'statusCode': 500,
            'error': str(e)
        }


@dataclass
class UpdateCheckPointEvent:
    checkpoint_id: str
    status: str
    multi_parts_tags: Dict[str, Any]


# PUT /checkpoint
def update_checkpoint_api(raw_event, context):
    event = UpdateCheckPointEvent(**raw_event)

    try:
        raw_checkpoint = ddb_service.get_item(table=checkpoint_table, key_values={
            'id': event.checkpoint_id
        })
        if raw_checkpoint is None or len(raw_checkpoint) == 0:
            return {
                'statusCode': 500,
                'error': f'checkpoint not found with id {event.checkpoint_id}'
            }

        checkpoint = CheckPoint(**raw_checkpoint)
        new_status = CheckPointStatus[event.status]
        ddb_service.update_item(
            table=checkpoint_table,
            key={
                'id': event.checkpoint_id
            },
            field_name='checkpoint_status',
            value=new_status
        )
        complete_mulipart_upload(checkpoint, event.multi_parts_tags)
        return {
            'statusCode': 200,
            'checkpoint': {
                'id': checkpoint.id,
                'type': checkpoint.checkpoint_type,
                's3_location': checkpoint.s3_location,
                'status': checkpoint.checkpoint_status.value,
                'params': checkpoint.params
            }
        }
    except Exception as e:
        logger.error(e)
        return {
            'statusCode': 500,
            'msg': str(e)
        }
