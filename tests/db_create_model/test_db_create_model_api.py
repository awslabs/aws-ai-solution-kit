import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin
import time

import sys
sys.path.append("extensions/aws-ai-solution-kit")
from utils import download_file_from_s3, download_folder_from_s3, download_folder_from_s3_by_tar, upload_folder_to_s3, upload_file_to_s3, upload_folder_to_s3_by_tar
start_time = time.time()

# url = "http://127.0.0.1:8080"
url = "http://0.0.0.0:8080"

payload = {
    "task": "db-create-model",  # job_id
    "db_create_model_payload": json.dumps({
        "job_id": "xxxxxx",
        "s3_output_path": ["aws-gcr-csdc-atl-exp-us-west-2/models/dreambooth/"],  # output object
        "s3_input_path": ["ws-gcr-csdc-atl-exp-us-west-2/aigc-webui-test-model/v1-5-pruned-emaonly.safetensors.tar"],
        "param": {
            "new_model_name": "db_test_4",
            "new_model_src": "v1-5-pruned-emaonly.safetensors",
            # todo: the params
        },
    }),
}

# db_create_model_params = json.loads(payload['db_create_model_payload'])['s3_input_path']
# local_model_dir = f'models/Stable-diffusion/{db_create_model_params["new_model_src"]}'
# bucket_name = db_create_model_params['bucket_name']
# s3_model_tar_path = f'aigc-webui-test-model'
# upload_folder_to_s3_by_tar(local_model_dir, bucket_name, s3_model_tar_path)


response = requests.post(url=f'{url}/invocations', json=payload)
# response = requests.post(url=f'{url}/dreambooth/createModel', json=payload)
# response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)

print(f"run time is {time.time()-start_time}")

print(f"response is {response}")

r = response.json()
