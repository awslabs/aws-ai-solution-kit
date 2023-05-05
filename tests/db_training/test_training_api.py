import sys 
import requests
import json

import os
os.environ["CHECKPOINT_TABLE"] = "CheckpointTable"
# os.environ["INSTANCE_TYPE"] = "ml.g4dn.2xlarge"
os.environ["INSTANCE_TYPE"] = "local_gpu"
os.environ["MODEL_TABLE"] = "ModelTable"
os.environ["S3_BUCKET"] = "alvindaiyan-aigc-testing-playground"
os.environ["TRAINING_SAGEMAKER_ARN"] = "arn:aws:states:us-west-1:991301791329:stateMachine:aigcputtrainapiTrainDeployStateMachine75CE4DED-QLhYA1bKKS2l"
os.environ["TRAIN_ECR_URL"] = "991301791329.dkr.ecr.us-west-1.amazonaws.com/aigc-train-utils:latest"
# os.environ["TRAIN_ECR_URL"] = "991301791329.dkr.ecr.us-west-1.amazonaws.com/aigc-webui-extension:latest"
os.environ["TRAIN_JOB_ROLE"] = "arn:aws:iam::991301791329:role/SdDreamBoothTrainStack-aigcputtrainapitrainrole6B3-NTIYQQZFBP87"
os.environ["TRAIN_TABLE"] = "TrainingTable"
os.environ["USER_EMAIL_TOPIC_ARN"] = "arn:aws:sns:us-west-1:991301791329:SdDreamBoothTrainStack-StableDiffusionSnsTopic2F55DB19-RVp9NaW8bm6H"

sys.path.append("extensions/aws-ai-solution-kit/scripts")
sys.path.append("extensions/aws-ai-solution-kit/")
sys.path.append("extensions/aws-ai-solution-kit/middleware_api/lambda/create_model")
sys.path.append("extensions/aws-ai-solution-kit/middleware_api/lambda")
sys.path.append(".")
from main import async_prepare_for_training_on_sagemaker, get_cloud_db_models
from train_api import _start_train_job
from sagemaker_entrypoint_json import main
from utils import get_variable_from_json
import logging


model_name = "db-training-test-1"
data_path_list = ["images"]
class_data_path_list = ["images"]
# cloud_create_model(new_model_name, ckpt_path)
model_list = get_cloud_db_models()
db_config_path = "models/dreambooth/dummy_local_model/db_config.json"
# db_config_path = f"models/dreambooth/{model_name}/db_config.json"
# os.system(f"cp {dummy_db_config_path} {db_config_path}")
for model in model_list:
    print(model)
    model_id = model["id"]
    model_name = model["model_name"]
    model_s3_path = model["output_s3_location"]
    if model_name == "db-training-test-1":
        response = async_prepare_for_training_on_sagemaker(
                model_id, model_name, model_s3_path, data_path_list, class_data_path_list, db_config_path)
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
        response = _start_train_job(job_id)
        print(f"Start training response:\n{response}")