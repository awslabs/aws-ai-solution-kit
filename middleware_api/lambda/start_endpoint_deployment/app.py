import boto3
import uuid
import os

sagemaker = boto3.client('sagemaker')
lambda_client = boto3.client("lambda")
role_response = (lambda_client.get_function_configuration(
    FunctionName = os.environ['AWS_LAMBDA_FUNCTION_NAME'])
)
EXECUTION_ROLE = role_response['Role']
ASYNC_SUCCESS_TOPIC = os.environ["SNS_INFERENCE_SUCCESS"]
ASYNC_ERROR_TOPIC = os.environ["SNS_INFERENCE_ERROR"]
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
INFERENCE_ECR_IMAGE_URL = os.environ.get("INFERENCE_ECR_IMAGE_URL")

def lambda_handler(event, context):
    # Parse the input data
    print(f"event is {event}")

    str_uuid = str(uuid.uuid4())[:4] 
    sagemaker_model_name = f"infer-model-{str_uuid}"
    sagemaker_endpoint_config = f"infer-config-{str_uuid}"
    sagemaker_endpoint_name = f"infer-endpoint-{str_uuid}"

    image_url = INFERENCE_ECR_IMAGE_URL 
    model_data_url = f"s3://{S3_BUCKET_NAME}/data/model.tar.gz"

    s3_output_path = f"s3://{S3_BUCKET_NAME}/sagemaker_output/"
    initial_instance_count = 1
    instance_type = 'ml.g4dn.xlarge'

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
