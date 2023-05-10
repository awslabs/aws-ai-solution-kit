import boto3
import os
import json
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME = os.environ.get('DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME')
endpoint_deployment_table = dynamodb.Table(DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME)
SNS_TOPIC_ARN = os.environ['SNS_NOTIFY_TOPIC_ARN']
sns = boto3.client('sns')

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


def send_message_to_sns(message_json):
    message = message_json
    sns_topic_arn = SNS_TOPIC_ARN


    try:
        response = sns.publish(
            TopicArn=sns_topic_arn,
            Message=json.dumps(message),
            Subject='Endpoint deployment failure occurred',
        )

        print(f"Message sent to SNS topic: {sns_topic_arn}")
        return {
            'statusCode': 200,
            'body': json.dumps('Message sent successfully')
        }

    except ClientError as e:
        print(f"Error sending message to SNS topic: {sns_topic_arn}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error sending message'),
            'error': str(e)
        }

def lambda_handler(event, context):
    print(f"Received event: {event}")

    # Extract the 'endpoint_creation_job_id' from the event
    if "Payload" in event:
        event_payload = event["Payload"]
    else:
        event_payload = event

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
        send_message_to_sns(event_payload)
    except Exception as e:
        print(f"Error updating DynamoDB table: {e}")
        raise e

    return {
        'statusCode': 200,
        'body': json.dumps('Error information updated in DynamoDB table')
    }
