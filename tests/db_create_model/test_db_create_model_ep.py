import json
import os

import requests
import io
import base64
from PIL import Image, PngImagePlugin
import time

import sys
sys.path.append("extensions/aws-ai-solution-kit")
from utils import download_file_from_s3, download_folder_from_s3, download_folder_from_s3_by_tar, upload_folder_to_s3, upload_file_to_s3, upload_folder_to_s3_by_tar

from sagemaker.predictor import Predictor
from sagemaker.predictor_async import AsyncPredictor


if __name__ == '__main__':

    # os.environ.setdefault('AWS_PROFILE', 'cloudfront_ext')
    start_time = time.time()

    # url = "http://127.0.0.1:8081"

    payload = {
        "job_id": "xxxxxx",
        "task": "db-create-model",  # job_id
        "inferenceId": "c0e66210-22be-4ee9-8876-ece1e0452860",
        "db_create_model_payload": json.dumps({
            # "bucket_name": "[/models/{model_type:dreambooth}]/{model_name}.tar",  # output object
            "job_id": 'c0e66210-22be-4ee9-8876-ece1e0452860',
            "bucket_name": "aws-gcr-csdc-atl-exp-us-west-2",  # output object
            "new_model_name": "db_test_4",
            "new_model_src": "v1-5-pruned-emaonly.safetensors",  # s3://{bucket}/.../{model}.tar
            "param": {
                # todo: the params
            },
        }),
    }
    payload = {
        "task": "db-create-model",  # job_id
        "db_create_model_payload": json.dumps({
            "job_id": "xxxxxx",
            "s3_output_path": ["aws-gcr-csdc-atl-exp-us-west-2/aigc-webui-test-model-v2/models/dreambooth/"],  # output object
            "s3_input_path": ["aws-gcr-csdc-atl-exp-us-west-2/aigc-webui-test-model-v2/models/Stable-diffusion/"],
            "param": {
                "new_model_name": "db_test_4",
                "new_model_src": "v1-5-pruned-emaonly.safetensors",
                # todo: the params
            },
        }),
    }

    # db_create_model_params = json.loads(payload['db_create_model_payload'])
    # local_model_dir = f'models/Stable-diffusion/{db_create_model_params["new_model_src"]}'
    # bucket_name = db_create_model_params['bucket_name']
    # s3_model_tar_path = f'aigc-webui-test-model'
    # upload_folder_to_s3_by_tar(local_model_dir, bucket_name, s3_model_tar_path)

    from sagemaker.serializers import JSONSerializer
    from sagemaker.deserializers import JSONDeserializer

    # endpoint_name = "aigc-webui-dreambooth-create-model-2023-04-13-09-21-31-981"
    # endpoint_name = "db-create-model-1681437544-456743"
    # endpoint_name = "aigc-createmodel-endpoint"
    endpoint_name = "db-create-model-1681723003-1839077"

    predictor = Predictor(endpoint_name)

    predictor = AsyncPredictor(predictor, name='c0e66210-22be-4ee9-8876-ece1e0452860')
    predictor.serializer = JSONSerializer()
    predictor.deserializer = JSONDeserializer()

    prediction = predictor.predict_async(data=payload, inference_id='c0e66210-22be-4ee9-8876-ece1e0452860')
    output_path = prediction.output_path


    from sagemaker.async_inference.waiter_config import WaiterConfig
    print(f"Response object: {prediction}")
    print(f"Response output path: {prediction.output_path}")
    print("Start Polling to get response:")

    import time

    start = time.time()

    config = WaiterConfig(
        max_attempts=100, #  number of attempts
        delay=10 #  time in seconds to wait between attempts
    )

    resp = prediction.get_result(config)

    print(f"Time taken: {time.time() - start}s")


