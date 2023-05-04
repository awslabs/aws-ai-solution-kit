from typing import Dict, Any

import boto3
from botocore.config import Config
from datetime import datetime
from datetime import timedelta

from _types import MultipartFileReq, CheckPoint


def get_s3_presign_urls(bucket_name, base_key, filenames) -> Dict[str, str]:
    s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
    presign_url_map = {}
    for filename in filenames:
        key = f'{base_key}/{filename}'
        url = s3.generate_presigned_url('put_object',
                                        Params={'Bucket': bucket_name,
                                                'Key': key,
                                                },
                                        ExpiresIn=3600 * 24 * 7)
        presign_url_map[filename] = url

    return presign_url_map


def batch_get_s3_multipart_signed_urls(bucket_name, base_key, filenames: [MultipartFileReq]) -> Dict[str, Any]:
    presign_url_map = {}
    for f in filenames:
        file = MultipartFileReq(**f)
        key = f'{base_key}/{file.filename}'
        signed_urls = get_s3_multipart_signed_urls(bucket_name, key, parts_number=file.parts_number)
        presign_url_map[file.filename] = signed_urls

    return presign_url_map


def get_s3_multipart_signed_urls(bucket_name, key, parts_number) -> Any:
    s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
    response = s3.create_multipart_upload(
        Bucket=bucket_name,
        Key=key,
        Expires=datetime.now() + timedelta(seconds=3600 * 24 * 7)
    )

    upload_id = response['UploadId']

    presign_urls = []

    for i in range(1, parts_number+1):
        presign_url = s3.generate_presigned_url(
            ClientMethod='upload_part',
            Params={
                'Bucket': bucket_name,
                'Key': key,
                'UploadId': upload_id,
                'PartNumber': i
            }
        )
        presign_urls.append(presign_url)
    return {
        's3_signed_urls': presign_urls,
        'upload_id': upload_id,
        'bucket': bucket_name,
        'key': key,
    }


def get_base_model_s3_key(_type: str, name: str, request_id: str) -> str:
    return f'{_type}/model/{name}/{request_id}'


def get_base_checkpoint_s3_key(_type: str, name: str, request_id: str) -> str:
    return f'{_type}/checkpoint/{name}/{request_id}'


def complete_mulipart_upload(ckpt: CheckPoint, filename_etag):
    s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
    if 'multipart_upload' in ckpt.params:
        multipart = ckpt.params['multipart_upload']
        for filename, val in multipart.items():
            # todo: can add s3 MD5 check here to see if file is upload properly
            if filename in filename_etag:
                filename_etag[filename].sort(key=lambda x: x['PartNumber'])
                response = s3.complete_multipart_upload(
                    Bucket=val['bucket'],
                    Key=val['key'],
                    MultipartUpload={'Parts': filename_etag[filename]},
                    UploadId=val['upload_id']
                )
                print(f'complete upload multipart response {response}')
                response = s3.abort_multipart_upload(
                    Bucket=val['bucket'],
                    Key=val['key'],
                    UploadId=val['upload_id']
                )
                print(f'abort upload multipart response {response}')


def split_s3_path(s3_path):
    path_parts = s3_path.replace("s3://", "").split("/")
    bucket = path_parts.pop(0)
    key = "/".join(path_parts)
    return bucket, key

