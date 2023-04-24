import dataclasses
import os
from decimal import Decimal
from unittest import TestCase
import requests



os.environ.setdefault('AWS_PROFILE', 'playground')
os.environ.setdefault('S3_BUCKET', 'alvindaiyan-aigc-testing-playground')
os.environ.setdefault('DYNAMODB_TABLE', 'ModelTable')
os.environ.setdefault('MODEL_TABLE', 'ModelTable')
os.environ.setdefault('TRAIN_TABLE', 'TrainingTable')
os.environ.setdefault('CHECKPOINT_TABLE', 'CheckpointTable')
os.environ.setdefault('SAGEMAKER_ENDPOINT_NAME', 'aigc-utils-endpoint')


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
        url = "presign s3 url"
        def upload_with_put(url):
            with open('file.tar.gz', 'rb') as file:
                response = requests.put(url, data=file)
                response.raise_for_status()

        upload_with_put(url)

    def test_model_update(self):
        from update_job_api import update_train_job_api
        update_train_job_api({
            'model_id': 'b983afd6-96ac-4481-a105-b5fa7d7dbb24',
            'status': 'Creating'
        }, {})


    def test_process(self):
        data = {} # sample data
        from create_model.update_job_api import process_result
        process_result(data, {})

    def test_convert(self):
        d = Decimal(4)
        from common.ddb_service.client import DynamoDbUtilsService
        obj = DynamoDbUtilsService._convert(d)
        print(obj)

    def test_list_all(self):
        from create_model.create_model_job_api import list_all_models_api
        resp = list_all_models_api({}, {})
        print(resp)

    def test_s3(self):
        # split s3://alvindaiyan-aigc-testing-playground/models/7a77d369-142c-4091-91e1-9278566a6a4f.out
        from create_model.update_job_api import split_s3_path
        bucket, key = split_s3_path('s3://path')
        from create_model.update_job_api import get_object
        get_object(bucket=bucket, key=key)


    def test_list_checkpoints(self):
        from create_model.checkpoint_api import list_all_checkpoints_api
        resp = list_all_checkpoints_api({}, {})
        print(resp)

    def test_update_train_job_api(self):
        from create_model.train_api import update_train_job_api
        update_train_job_api({
            "train_job_id": "0e78f0b0-1617-40eb-961c-dca5374b34ea",
            "status": "Training"
        }, {})

    def test_scan(self):
        import logging
        from common.ddb_service.client import DynamoDbUtilsService
        logger = logging.getLogger('boto3')
        ddb_service = DynamoDbUtilsService(logger=logger)
        resp = ddb_service.scan(table='ModelTable', filters={
            'model_type': 'dreambooth',
            # 'job_status': ['Initial', 'Creating', 'Complete']
        })
        print(resp)



