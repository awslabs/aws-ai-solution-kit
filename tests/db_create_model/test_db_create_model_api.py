import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin
import time

import sys
sys.path.append("extensions/aws-ai-solution-kit")
from utils import get_path_from_s3_path, get_bucket_name_from_s3_path, download_folder_from_s3_by_tar, upload_folder_to_s3, upload_file_to_s3, upload_folder_to_s3_by_tar
start_time = time.time()

# url = "http://127.0.0.1:8080"
url = "http://0.0.0.0:8080"

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

db_create_model_payload = json.loads(payload['db_create_model_payload'])
local_model_dir = f'models/Stable-diffusion/{db_create_model_payload["param"]["new_model_src"]}'
s3_input_path = db_create_model_payload["s3_input_path"][0]
input_bucket_name = get_bucket_name_from_s3_path(s3_input_path)
input_path = get_path_from_s3_path(s3_input_path)
# s3_model_tar_path = f'aigc-webui-test-model'
# upload_folder_to_s3_by_tar(local_model_dir, input_bucket_name, input_path)


print(payload)
response = requests.post(url=f'{url}/invocations', json=payload)
# response = requests.post(url=f'{url}/dreambooth/createModel', json=payload)
# response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)

print(f"run time is {time.time()-start_time}")

print(f"response is {response}")

r = response.json()
print(r)
