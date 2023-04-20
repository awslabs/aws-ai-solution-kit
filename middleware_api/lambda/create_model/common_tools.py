from typing import Dict

import boto3
from botocore.config import Config


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
