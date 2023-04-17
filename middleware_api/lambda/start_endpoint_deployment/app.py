import boto3
import uuid
import sagemaker
import json

import os

sagemaker = boto3.client('sagemaker')
# role = "arn:aws:iam::002224604296:role/service-role/AmazonSageMaker-ExecutionRole-20230319T081280"
EXECUTION_ROLE = sagemaker.get_excution_role()
INSTANCE_TYPE = 'ml.m4.xlarge'
# async_success_topic = 'arn:aws:sns:us-west-2:002224604296:SdAsyncInferenceStack-dev-SNSReceiveSageMakerinferencesuccess314267EE-OcvPLAvRGaNL'
ASYNC_SUCCESS_TOPIC = os.environ()
async_error_topic = 'arn:aws:sns:us-west-2:002224604296:SdAsyncInferenceStack-dev-SNSReceiveSageMakerinferenceerror26AEDEC2-a0IVYn4toIkE'
ASYNC_ERROR_TOPIC = os.environ()

def lambda_handler(event, context):
    # Parse the input data
    print(f"event is {event}")
    # best_training_job = event['best_training_job']

    str_uuid = str(uuid.uuid4())[:4] 
    sagemaker_model_name = f"infer-model-{str_uuid}"
    sagemaker_endpoint_config = f"infer-config-{str_uuid}"
    sagemaker_endpoint_name = f"infer-endpoint-{str_uuid}"

    image_url = "002224604296.dkr.ecr.us-west-2.amazonaws.com/ask-webui-api-gpu:latest"
    model_data_url = "s3://sagemaker-us-west-2-002224604296/ask-webui-extension/data/model.tar.gz"

    s3_output_path = "s3://sagemaker-us-west-2-002224604296/ask-webui-extension/asyncinvoke/out/"
    initial_instance_count = 1
    instance_type = 'ml.g4dn.2xlarge'

    print('Creating model resource ...')
    create_model(sagemaker_model_name, image_url, model_data_url)
    print('Creating endpoint configuration...')
    create_endpoint_config(sagemaker_endpoint_config, s3_output_path, sagemaker_model_name, initial_instance_count, instance_type)
    print('There is no existing endpoint for this model. Creating new model endpoint...')
    create_endpoint(sagemaker_endpoint_name, sagemaker_endpoint_config)
    event['stage'] = 'Deployment'
    event['status'] = 'Creating'
    event['endpoint_name'] = sagemaker_endpoint_name
    event['message'] = 'Started deploying endpoint "{}"'.format(sagemaker_endpoint_name)

    return event

def create_model(name, image_url, model_data_url):
    """ Create SageMaker model.
    Args:
        name (string): Name to label model with
        image_url (string): Registry path of the Docker image that contains the model algorithm
        model_data_url (string): URL of the model artifacts created during training to download to container
    Returns:
        (None)
    """
    try:
        sagemaker.create_model(
            ModelName=name,
            PrimaryContainer={
                'Image': image_url,
                'ModelDataUrl': model_data_url
            },
            ExecutionRoleArn=EXECUTION_ROLE
        )
    except Exception as e:
        print(e)
        print('Unable to create model.')
        raise(e)

def create_endpoint_config(endpoint_config_name, s3_output_path, model_name, initial_instance_count, instance_type):
    """ Create SageMaker endpoint configuration.
    Args:
        endpoint_config_name (string): Name to label endpoint configuration with.
        s3_output_path (string): S3 location to upload inference responses to.
        model_name (string): The name of model to host.
        initial_instance_count (integer): Number of instances to launch initially.
        instance_type (string): the ML compute instance type.
    Returns:
        (None)
    """
    try:
        sagemaker.create_endpoint_config(
            EndpointConfigName=endpoint_config_name,
            AsyncInferenceConfig={
                "OutputConfig": {
                    "S3OutputPath": s3_output_path,
                    "NotificationConfig": {
                        "SuccessTopic": ASYNC_SUCCESS_TOPIC,
                        "ErrorTopic": ASYNC_ERROR_TOPIC 
                    }
                }
            },
            ProductionVariants=[
                {
                    'VariantName': 'prod',
                    'ModelName': model_name,
                    'InitialInstanceCount': initial_instance_count,
                    'InstanceType': instance_type
                }
            ]
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
