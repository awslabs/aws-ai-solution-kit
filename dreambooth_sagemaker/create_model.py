import time
import pickle
import json
import threading

import sagemaker

import sys
import os
sys.path.append('extensions/aws-ai-solution-kit')
sys.path.append("extensions/sd_dreambooth_extension")
# from utils import download_folder_from_s3_by_tar, download_file_from_s3, upload_file_to_s3, upload_folder_to_s3_by_tar

import sagemaker
sagemaker_session = sagemaker.Session()
bucket = sagemaker_session.default_bucket()

role = "arn:aws:iam::683638520402:role/service-role/AmazonSageMaker-ExecutionRole-20221031T120168"

import boto3
account_id = boto3.client('sts').get_caller_identity().get('Account')
region_name = boto3.session.Session().region_name
image_uri = '{0}.dkr.ecr.{1}.amazonaws.com/aigc-webui-extension:latest'.format(account_id, region_name)
base_name = sagemaker.utils.base_name_from_image(image_uri)

from sagemaker.model import Model
from sagemaker.predictor import Predictor

model_name = None
model_data = None

model = Model(
    name=model_name,
    model_data=model_data,
    role=role,
    image_uri=image_uri,
    # env=model_environment,
    predictor_cls=Predictor
)

from sagemaker.async_inference import AsyncInferenceConfig
instance_type = 'ml.g4dn.2xlarge'
instance_count = 1
async_config = AsyncInferenceConfig(output_path='s3://{0}/{1}/asyncinvoke/out/'.format(bucket, 'ask-webui-extension/create-model'))
predictor = model.deploy(
    instance_type=instance_type, 
    initial_instance_count=instance_count,
    async_inference_config=async_config
)

from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer

predictor.serializer = JSONSerializer()
predictor.deserializer = JSONDeserializer()

inputs = {}
prediction = predictor.predict_async(inputs)

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

prediction.get_result(config)

print(f"Time taken: {time.time() - start}s")