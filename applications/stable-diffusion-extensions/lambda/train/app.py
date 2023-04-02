import json
import boto3
import os
import base64

s3 = boto3.client("s3")
dynamodb = boto3.resource('dynamodb')

# Get DynamoDB table name from environment variable
TABLE_NAME = os.environ.get("TABLE_NAME", "TrainingTable")

# context unused in this example
def lambda_handler(event, _context):
    # Store input training id into DynamoDB
    table = dynamodb.Table(TABLE_NAME)
    table.put_item(
        Item={
            'id': event['id'],
            'status': 'training'
        }
    )

    # Other logic goes here

    # Return success
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Training started"
        })
    }

    