import dataclasses
import os
from unittest import TestCase
import requests

os.environ.setdefault('AWS_PROFILE', 'cloudfront_ext')
os.environ.setdefault('S3_BUCKET', 'alvindaiyan-aigc-testing')
os.environ.setdefault('DYNAMODB_TABLE', 'TrainingTable')


@dataclasses.dataclass
class MockContext:
    aws_request_id: str


class UploadTest(TestCase):

    def test_upload(self):
        from handler import handler
        resp = handler({
            "model_type": "dreambooth",
            "name": "test_upload",
            "filename": "test_create_model_api.py"
        }, MockContext(aws_request_id="asdfasdf"))
        print(resp)

        def upload_with_put(url):
            with open('test_create_model_api.py', 'rb') as file:
                response = requests.put(url, data=file)
                response.raise_for_status()

        upload_with_put(resp['body'])

    def test_upload_2(self):
        url = "test_url"
        def upload_with_put(url):
            with open('test_create_model_api.py', 'rb') as file:
                response = requests.put(url, data=file)
                response.raise_for_status()

        upload_with_put(url)
