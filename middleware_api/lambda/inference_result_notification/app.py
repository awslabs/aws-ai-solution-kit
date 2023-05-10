import json
import io
import boto3
import base64
import os
from PIL import Image
from datetime import datetime
from botocore.exceptions import ClientError

s3_resource = boto3.resource('s3')
s3_client = boto3.client('s3')

DDB_INFERENCE_TABLE_NAME = os.environ.get('DDB_INFERENCE_TABLE_NAME')
DDB_TRAINING_TABLE_NAME = os.environ.get('DDB_TRAINING_TABLE_NAME')
DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME = os.environ.get('DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET')
SNS_TOPIC = os.environ['NOTICE_SNS_TOPIC']

ddb_client = boto3.resource('dynamodb')
inference_table = ddb_client.Table(DDB_INFERENCE_TABLE_NAME)
endpoint_deployment_table = ddb_client.Table(DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME)
sns = boto3.client('sns')

def get_bucket_and_key(s3uri):
    pos = s3uri.find('/', 5)
    bucket = s3uri[5 : pos]
    key = s3uri[pos + 1 : ]
    return bucket, key

def decode_base64_to_image(encoding):
    if encoding.startswith("data:image/"):
        encoding = encoding.split(";")[1].split(",")[1]
    return Image.open(io.BytesIO(base64.b64decode(encoding)))


def update_inference_job_table(inference_id, key, value):
    # Update the inference DDB for the job status
    response = inference_table.get_item(
        Key={
            "InferenceJobId": inference_id,
        })
    inference_resp = response['Item']
    if not inference_resp:
        raise Exception(f"Failed to get the inference job item with inference id: {inference_id}")

    response = inference_table.update_item(
        Key={
            "InferenceJobId": inference_id,
        },
        UpdateExpression=f"set #k = :r",
        ExpressionAttributeNames={'#k': key},
        ExpressionAttributeValues={':r': value},
        ReturnValues="UPDATED_NEW"
    )

def get_curent_time():
    # Get the current time
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d-%H-%M-%S")
    return formatted_time

def upload_file_to_s3(file_name, bucket, directory=None, object_name=None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name
    
    # Add the directory to the object_name
    if directory:
        object_name = f"{directory}/{object_name}"

    # Upload the file
    try:
        s3_client.upload_file(file_name, bucket, object_name)
        print(f"File {file_name} uploaded to {bucket}/{object_name}")
    except Exception as e:
        print(f"Error occurred while uploading {file_name} to {bucket}/{object_name}: {e}")
        return False
    return True

def send_message_to_sns(message_json):
    message = json.loads(message_json)


    try:
        response = sns.publish(
            TopicArn=SNS_TOPIC,
            Message=json.dumps(message),
            Subject=f"Inference Failed(id:{message['inferenceId']}) with following sagemaker error info",
        )

        print(f"Message sent to SNS topic: {sns_topic}")
        return {
            'statusCode': 200,
            'body': json.dumps('Message sent successfully')
        }

    except ClientError as e:
        print(f"Error sending message to SNS topic: {sns_topic}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error sending message')
        }


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    message = event['Records'][0]['Sns']['Message']
    print("From SNS: " + str(message))
    message = json.loads(message)
    invocation_status = message["invocationStatus"]
    inference_id = message["inferenceId"]
    if invocation_status == "Completed":
        print(f"Complete invocation!")
        endpoint_name = message["requestParameters"]["endpointName"]
        update_inference_job_table(inference_id, 'status', 'succeed')
        update_inference_job_table(inference_id, 'completeTime', get_curent_time())
        update_inference_job_table(inference_id, 'sagemakerRaw', str(message))
        
        output_location = message["responseParameters"]["outputLocation"]

        bucket, key = get_bucket_and_key(output_location)
        obj = s3_resource.Object(bucket, key)
        body = obj.get()['Body'].read().decode('utf-8') 
        json_body = json.loads(body)

        # save images
        for count, b64image in enumerate(json_body["images"]):
            image = decode_base64_to_image(b64image).convert("RGB")
            output = io.BytesIO()
            image.save(output, format="JPEG")
            # Upload the image to the S3 bucket
            s3_client.put_object(
                Body=output.getvalue(),
                Bucket=S3_BUCKET_NAME,
                Key=f"out/{inference_id}/result/image_{count}.jpg"
            )
            # Update the DynamoDB table
            inference_table.update_item(
                Key={
                    'InferenceJobId': inference_id
                    },
                UpdateExpression='SET image_names = list_append(if_not_exists(image_names, :empty_list), :new_image)',
                ExpressionAttributeValues={
                    ':new_image': [f"image_{count}.jpg"],
                    ':empty_list': []
                }
            )

        # save parameters
        inference_parameters = {}
        inference_parameters["parameters"] = json_body["parameters"]
        inference_parameters["info"] = json_body["info"]
        inference_parameters["endpont_name"] = endpoint_name
        inference_parameters["inference_id"] = inference_id
        inference_parameters["sns_info"] = message

        json_file_name = f"/tmp/{inference_id}_param.json"

        with open(json_file_name, "w") as outfile:
            json.dump(inference_parameters, outfile)

        upload_file_to_s3(json_file_name, S3_BUCKET_NAME, f"out/{inference_id}/result",f"{inference_id}_param.json")
        update_inference_job_table(inference_id, 'inference_info_name', json_file_name)
        
        print(f"Complete inference parameters {inference_parameters}")
    else:
        update_inference_job_table(inference_id, 'status', 'failed')
        update_inference_job_table(inference_id, 'sagemakerRaw', str(message))
        print(f"Not complete invocation!")
        send_message_to_sns(message)
    return message