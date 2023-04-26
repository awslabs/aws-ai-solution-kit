import boto3
import os
from datetime import datetime

DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME = os.environ.get('DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME')

sagemaker = boto3.client('sagemaker')
ddb_client = boto3.resource('dynamodb')
endpoint_deployment_table = ddb_client.Table(DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME)

def lambda_handler(event, context):
    # Parse the input data
    print(f"event is {event}")
    event_payload = event["Payload"]
    stage = event_payload['stage']
    endpoint_deployment_job_id = event_payload['endpoint_deployment_id']
    endpoint_name = event_payload['endpoint_name']
    if stage == 'Training':
        print("Status check for training not implemented yet!")
    elif stage == 'Deployment':
        name = event_payload['endpoint_name']
        endpoint_details = describe_endpoint(name)
        status = endpoint_details['EndpointStatus']
        if status == 'InService':
            current_time = str(datetime.now())
            event_payload['message'] = 'Deployment completed for endpoint "{}".'.format(name)
            update_endpoint_job_table(endpoint_deployment_job_id,'endpoint_name', endpoint_name)
            update_endpoint_job_table(endpoint_deployment_job_id,'endpoint_status', status)
            update_endpoint_job_table(endpoint_deployment_job_id,'endTime', current_time)
            update_endpoint_job_table(endpoint_deployment_job_id,'status', 'success')
        elif status == 'Creating':
            update_endpoint_job_table(endpoint_deployment_job_id,'endpoint_name', endpoint_name)
            update_endpoint_job_table(endpoint_deployment_job_id,'endpoint_status', status) 
        elif status == 'Failed':
            failure_reason = endpoint_details['FailureReason']
            event_payload['message'] = 'Deployment failed for endpoint "{}". {}'.format(name, failure_reason)
            update_endpoint_job_table(endpoint_deployment_job_id,'endpoint_name', endpoint_name)
            update_endpoint_job_table(endpoint_deployment_job_id,'endpoint_status', status)
            update_endpoint_job_table(endpoint_deployment_job_id,'status', 'failed')
        elif status == 'RollingBack':
            event_payload['message'] = 'Deployment failed for endpoint "{}", rolling back to previously deployed version.'.format(name)
            update_endpoint_job_table(endpoint_deployment_job_id,'endpoint_name', endpoint_name)
            update_endpoint_job_table(endpoint_deployment_job_id,'endpoint_status', status)
    event_payload['status'] = status
    return event_payload

def update_endpoint_job_table(endpoint_deployment_job_id, key, value):
    # Update the inference DDB for the job status
    response = endpoint_deployment_table.get_item(
        Key={
            "EndpointDeploymentJobId": endpoint_deployment_job_id,
        })
    endpoint_resp = response['Item']
    if not endpoint_resp:
        raise Exception(f"Failed to get the endpoint deployment job item with endpoint deployment job id: {endpoint_deployment_job_id}")

    response = endpoint_deployment_table.update_item(
        Key={
            "EndpointDeploymentJobId": endpoint_deployment_job_id,
        },
        UpdateExpression=f"set #k = :r",
        ExpressionAttributeNames={'#k': key},
        ExpressionAttributeValues={':r': value},
        ReturnValues="UPDATED_NEW"
    )

def describe_endpoint(name):
    """ Describe SageMaker endpoint identified by input name.
    Args:
        name (string): Name of SageMaker endpoint to describe.
    Returns:
        (dict)
        Dictionary containing metadata and details about the status of the endpoint.
    """
    try:
        response = sagemaker.describe_endpoint(
            EndpointName=name
        )
    except Exception as e:
        print(e)
        print('Unable to describe endpoint.')
        raise(e)
    return response
