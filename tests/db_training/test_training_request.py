import sys 
import requests
import json

sys.path.append("extensions/aws-ai-solution-kit/scripts")
sys.path.append("extensions/aws-ai-solution-kit/")
sys.path.append(".")
from main import async_prepare_for_training_on_sagemaker, get_cloud_db_models
from sagemaker_entrypoint_json import main 
from utils import get_variable_from_json
import logging


model_name = "testMultipart012"
data_path = "images"
class_data_path = "images"
# cloud_create_model(new_model_name, ckpt_path)
model_list = get_cloud_db_models()
for model in model_list:
    print(model)
    model_id = model["id"]
    model_name = model["model_name"]
    model_s3_path = model["output_s3_location"]
    if model_name == "testMultipart012":
        response = async_prepare_for_training_on_sagemaker(model_id, model_name, model_s3_path, data_path, class_data_path)
        job_id = response["job"]["id"]
        url = get_variable_from_json('api_gateway_url')
        api_key = get_variable_from_json('api_token')
        if url is None or api_key is None:
            logging.error("Url or API-Key is not setting.")
            break
        url += "train"
        payload = {
            "train_job_id": job_id,
            "status": "Training"
        }
        # Start creating model on cloud.
        response = requests.put(url=url, json=payload, headers={'x-api-key': api_key}).json()
        print(f"Start training response:\n{response}")