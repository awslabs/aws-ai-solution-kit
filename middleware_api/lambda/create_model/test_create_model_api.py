import dataclasses
import os
from unittest import TestCase
import requests

os.environ.setdefault('AWS_PROFILE', 'playground')
os.environ.setdefault('S3_BUCKET', 'alvindaiyan-aigc-testing')
os.environ.setdefault('DYNAMODB_TABLE', 'TrainingTable')


@dataclasses.dataclass
class MockContext:
    aws_request_id: str


class ModelsApiTest(TestCase):

    def test_upload(self):
        from create_model_job_api import create_model_api
        resp = create_model_api({
            "model_type": "dreambooth",
            "name": "test_upload",
            "filenames": ["test_create_model_api.py", "test_create_model_api2.py"]
        }, MockContext(aws_request_id="asdfasdf"))
        print(resp)

        def upload_with_put(url):
            with open('test_create_model_api.py', 'rb') as file:
                response = requests.put(url, data=file)
                response.raise_for_status()

        upload_with_put(resp['s3PresignUrl'])

    def test_upload_2(self):
        url = "test_url"
        def upload_with_put(url):
            with open('test_create_model_api.py', 'rb') as file:
                response = requests.put(url, data=file)
                response.raise_for_status()

        upload_with_put(url)

    def test_model_update(self):
        from update_job_api import update_train_job_api
        update_train_job_api({
            'model_id': 'request_id',
            'status': 'Train'
        }, {})
