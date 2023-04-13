import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin
import time

start_time = time.time()

url = "http://127.0.0.1:8081"

payload = {
    "task": "db-create-model", 
    "db_create_model_payload": json.dumps({
        "new_model_name": "dreambooth",
        "new_model_src": "dreambooth"})
}

# response = requests.post(url=f'{url}/origin-invocations', json=payload)
response = requests.post(url=f'{url}/invocations', json=payload)
# response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)

print(f"run time is {time.time()-start_time}")

print(f"response is {response}")

r = response.json()