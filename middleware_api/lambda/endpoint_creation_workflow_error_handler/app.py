import boto3
import os
import json
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME = os.environ.get('DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME')
endpoint_deployment_table = dynamodb.Table(DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME)

def update_endpoint_deployment_job_table(endpoint_deployment_job_id, key, value):
    response = endpoint_deployment_table.update_item(
        Key={
            "EndpointDeploymentJobId": endpoint_deployment_job_id,
        },
        UpdateExpression=f"set #k = :r",
        ExpressionAttributeNames={'#k': key},
        ExpressionAttributeValues={':r': value},
        ReturnValues="UPDATED_NEW"
    )
    return response

def lambda_handler(event, context):
    print(f"Received event: {event}")

    # Extract the 'endpoint_creation_job_id' from the event
    event_payload = event["Payload"]
    endpoint_creation_job_id = event_payload['endpoint_deployment_id']

    # Extract the error information
    error_info = event.get('error', 'Unknown error')
    current_time = str(datetime.now())

    # Update the DynamoDB table
    try:
        response1 = update_endpoint_deployment_job_table(endpoint_creation_job_id, 'status', 'failed')
        response2 = update_endpoint_deployment_job_table(endpoint_creation_job_id, 'endTime', current_time)
        response3 = update_endpoint_deployment_job_table(endpoint_creation_job_id, 'error', str(error_info))

        print(f"Update response 1: {response1}")
        print(f"Update response 2: {response2}")
        print(f"Update response 3: {response3}")
    except Exception as e:
        print(f"Error updating DynamoDB table: {e}")
        raise e

    return {
        'statusCode': 200,
        'body': json.dumps('Error information updated in DynamoDB table')
    }
