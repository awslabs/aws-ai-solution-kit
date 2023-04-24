import decimal
import json
import logging
import os

from sagemaker import Predictor
from sagemaker.predictor_async import AsyncPredictor

from common.ddb_service.client import DynamoDbUtilsService
from _types import ModelJob, CheckPoint

bucket_name = os.environ.get('S3_BUCKET')
train_table = os.environ.get('DYNAMODB_TABLE')
endpoint_name = os.environ.get('SAGEMAKER_ENDPOINT_NAME')

logger = logging.getLogger('boto3')
ddb_service = DynamoDbUtilsService(logger=logger)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        # if passed in object is instance of Decimal
        # convert it to a string
        if isinstance(obj, decimal.Decimal):
            return str(obj)

        #️ otherwise use the default behavior
        return json.JSONEncoder.default(self, obj)


def create_sagemaker_inference(job: ModelJob, checkpoint: CheckPoint):
    payload = {
        "task": "db-create-model",  # router
        "db_create_model_payload": json.dumps({
            "s3_output_path": job.output_s3_location,  # output object
            "s3_input_path": checkpoint.s3_location,
            "param": job.params,
            "job_id": job.id
        }, cls=DecimalEncoder),
    }

    from sagemaker.serializers import JSONSerializer
    from sagemaker.deserializers import JSONDeserializer

    predictor = Predictor(endpoint_name)

    predictor = AsyncPredictor(predictor, name=job.id)
    predictor.serializer = JSONSerializer()
    predictor.deserializer = JSONDeserializer()
    prediction = predictor.predict_async(data=payload, inference_id=job.id)
    output_path = prediction.output_path

    return {
        'statusCode': 200,
        'job': {
            'output_path': output_path,
            'id': job.id,
            'endpointName': endpoint_name,
            'jobStatus': job.job_status.value,
            'jobType': job.model_type
        }
    }



