import json
import logging
import os

from sagemaker import Predictor
from sagemaker.async_inference import WaiterConfig
from sagemaker.predictor_async import AsyncPredictor

from common.ddb_service.client import DynamoDbUtilsService
from create_model._types import ModelJob, CreateModelStatus

bucket_name = os.environ.get('S3_BUCKET')
train_table = os.environ.get('DYNAMODB_TABLE')
endpoint_name = os.environ.get('SAGEMAKER_ENDPOINT_NAME')

logger = logging.getLogger('boto3')
ddb_service = DynamoDbUtilsService(logger=logger)


def create_sagemaker_inference(event, context):
    job_id = event['job_id']
    # todo: get job
    job = ModelJob(
        id=job_id,
        model_type='dreambooth',
        job_status=CreateModelStatus.Initial,
        s3_location='v1-5-pruned-emaonly.safetensors',
    )
    payload = {
        "task": "db-create-model",  # router
        "db_create_model_payload": json.dumps({
            # "bucket_name": "[/models/{model_type:dreambooth}]/{model_name}.tar",  # output object
            "s3_output_path": f'bucket_name/{job.model_type}/',  # output object
            "s3_input_path": job.s3_location,
            "param": job.params,
        }),
    }

    from sagemaker.serializers import JSONSerializer
    from sagemaker.deserializers import JSONDeserializer

    predictor = Predictor(endpoint_name)

    predictor = AsyncPredictor(predictor, name=job_id)
    predictor.serializer = JSONSerializer()
    predictor.deserializer = JSONDeserializer()
    prediction = predictor.predict_async(data=payload)
    output_path = prediction.output_path

    # todo: update job status
    job.job_status = CreateModelStatus.Creating

    config = WaiterConfig(
        max_attempts=100,  # number of attempts
        delay=10  # time in seconds to wait between attempts
    )

    resp = prediction.get_result(config)
    try:
        if resp['statusCode'] != 200:
            print(resp)
            # todo: update job status
            job.job_status = CreateModelStatus.Fail
            return {
                'statusCode': 200,
                'error': resp['error']
            }

        # todo: update job status
        job.job_status = CreateModelStatus.Complete

        return {
            'statusCode': 200,
            'body': {
                'output_path': output_path,
                'id': job_id,
                'endpointName': endpoint_name,
                'jobStatus': job.job_status.value,
                'jobType': job.model_type
            }
        }
    except AttributeError as e:
        logger.error(f'not expected resp format {resp}')
        return {
            'statusCode': 200,
            'error': 'not expected resp format',
        }
    except Exception as e:
        return {
            'statusCode': 200,
            'error': e,
        }
