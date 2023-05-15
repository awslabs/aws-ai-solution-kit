import time
import pickle
import json
import threading

import sys
import os
sys.path.append('extensions/aws-ai-solution-kit')
sys.path.append("extensions/sd_dreambooth_extension")
# from utils import download_folder_from_s3_by_tar, download_file_from_s3, upload_file_to_s3, upload_folder_to_s3_by_tar

import sagemaker
sagemaker_session = sagemaker.Session()
bucket = sagemaker_session.default_bucket()

# EXECUTION_ROLE = "arn:aws:iam::683638520402:role/service-role/AmazonSageMaker-ExecutionRole-20221031T120168"
# EXECUTION_ROLE = "arn:aws:iam::648149843064:role/SdDreamBoothTrainStack-aigcutilsendpointrole0A8729-8OSFWEAGUTCU"
# EXECUTION_ROLE = "arn:aws:iam::991301791329:role/SdDreamBoothTrainStack-aigcputtrainapitrainrole6B3-NTIYQQZFBP87"
# EXECUTION_ROLE = "arn:aws:iam::991301791329:role/SdDreamBoothTrainStack-aigcutilsendpointrole0A8729-L2PGDZBLK87E"
# EXECUTION_ROLE = "arn:aws:sts::991301791329:assumed-role/SdDreamBoothTrainStack-aigcupdatemodelapirole2C5D6-FMUYQ5DEJPPI/aigc-update-model-api-update-model"
EXECUTION_ROLE = "arn:aws:iam::991301791329:role/SdDreamBoothTrainStack-aigcutilsendpointrole0A8729-DBERLNVJJEAL"
# INSTANCE_TYPE = "ml.g4dn.xlarge"
INSTANCE_TYPE = "ml.c6i.8xlarge"

import boto3
account_id = boto3.client('sts').get_caller_identity().get('Account')
region_name = boto3.session.Session().region_name
# image_uri = '{0}.dkr.ecr.{1}.amazonaws.com/aigc-webui-dreambooth-create-model:latest'.format(account_id, region_name)
# image_uri = '{0}.dkr.ecr.{1}.amazonaws.com/aigc-webui-utils:latest'.format(account_id, region_name)
image_uri = '{0}.dkr.ecr.{1}.amazonaws.com/aigc-create-model:latest'.format(account_id, region_name)
# image_uri = '{0}.dkr.ecr.{1}.amazonaws.com/aigc-cpu-test:latest'.format(account_id, region_name)
base_name = sagemaker.utils.base_name_from_image(image_uri)
sagemaker = boto3.client('sagemaker')

def create_model(name, container, model_data_url):
    """ Create SageMaker model.
    Args:
        name (string): Name to label model with
        container (string): Registry path of the Docker image that contains the model algorithm
        model_data_url (string): URL of the model artifacts created during training to download to container
    Returns:
        (None)
    """
    try:
        sagemaker.create_model(
            ModelName=name,
            PrimaryContainer={
                'Image': container,
                # 'ModelDataUrl': model_data_url
            },
            ExecutionRoleArn=EXECUTION_ROLE
        )
    except Exception as e:
        print(e)
        print('Unable to create model.')
        raise(e)

def create_endpoint_config(name):
    """ Create SageMaker endpoint configuration.
    Args:
        name (string): Name to label endpoint configuration with.
    Returns:
        (None)
    """
    try:
        sagemaker.create_endpoint_config(
            EndpointConfigName=name,
            ProductionVariants=[
                {
                    'VariantName': 'prod',
                    'ModelName': name,
                    'InitialInstanceCount': 1,
                    'InstanceType': INSTANCE_TYPE,
                    'VolumeSizeInGB': 512
                }
            ],
            AsyncInferenceConfig=
                {
                    "OutputConfig": {
                        "S3OutputPath": 's3://{0}/{1}/asyncinvoke/out/'.format(bucket, 'ask-webui-extension/create-model'),
                        "NotificationConfig": {
                            # "SuccessTopic": "arn:aws:sns:us-east-1:648149843064:successCreateModel",
                            # "ErrorTopic": "arn:aws:sns:us-east-1:648149843064:failureCreateModel"
                            "SuccessTopic": "arn:aws:sns:us-west-1:991301791329:successCreateModel",
                            "ErrorTopic": "arn:aws:sns:us-west-1:991301791329:failureCreateModel"
                        }
                    }

                },

        )
    except Exception as e:
        print(e)
        print('Unable to create endpoint configuration.')
        raise(e)

def create_endpoint(endpoint_name, config_name):
    """ Create SageMaker endpoint with input endpoint configuration.
    Args:
        endpoint_name (string): Name of endpoint to create.
        config_name (string): Name of endpoint configuration to create endpoint with.
    Returns:
        (None)
    """
    try:
        sagemaker.create_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=config_name
        )
    except Exception as e:
        print(e)
        print('Unable to create endpoint.')
        raise(e)

# The name of the endpoint. The name must be unique within an AWS Region in your AWS account.
model_name = f'db-create-model-{str(time.time()).replace(".", "-")}'
# model_name = f'aigc-utils-endpoint'
endpoint_name = model_name

# Create an endpoint config name.
endpoint_config_name = f'{base_name}_config'

# create model don't need the model data
model_data_url = "s3://xxx/xxx"
print('Creating model resource from training artifact...')
create_model(model_name, image_uri, model_data_url=model_data_url)
print('Creating endpoint configuration...')
create_endpoint_config(model_name)
print('There is no existing endpoint for this model. Creating new model endpoint...')
create_endpoint(endpoint_name, model_name)
