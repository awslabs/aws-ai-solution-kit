import json
import boto3
import os
import base64
from io import BytesIO

sagemaker = boto3.client("sagemaker-runtime")
s3 = boto3.client("s3")

BUCKET_NAME = os.environ["BUCKET_NAME"]
BUCKET_INPUT_PREFIX = os.environ["BUCKET_INPUT_PREFIX"]
BUCKET_OUTPUT_PREFIX = os.environ["BUCKET_OUTPUT_PREFIX"]
# We use image super resolution model as an example and deploy it ahead of time
ENDPOINT_NAME = os.environ.get("ENDPOINT_NAME", "super-resolution")

# context unused in this example
def lambda_handler(event, _context):

    print(f"Received event: {json.dumps(event)}")
    # check if image_bytes is present in the event, otherwise read from S3
    if "body" in event:
        input_payload = event["body"]

    elif "s3_bucket" in event and "s3_prefix" in event:
        bucket = event["s3_bucket"]
        input_key = event["s3_prefix"]
        # Read the input payload from S3
        input_payload = s3.get_object(Bucket=bucket, Key=input_key)["Body"].read().decode("utf-8")
    else:
        raise ValueError("Input payload not found in event")

    # Invoke the SageMaker endpoint with image bytes
    response = sagemaker.invoke_endpoint(
        # EndpointName=ENDPOINT_NAME,
        EndpointName = 'super-resolution',
        ContentType="application/json",
        # wrap payload in a json string for this example with specific key "img" required by the model
        Body=json.dumps({"img": input_payload})
    )
    print(f"Raw Response: {response}")

    # Read the image from the inference response and return with base64 encoding
    inference_result = json.loads(response["Body"].read().decode("utf-8"))['result']
    print(f"Inference result: {inference_result}")

    # Save the inference response to S3 if it exceeds payload size limits
    if len(inference_result) > 6*1024*1024:  # Adjust the limit based on your payload size limits (e.g., 6 MB)

        s3.put_object(Bucket=BUCKET_NAME, Key=BUCKET_OUTPUT_PREFIX, Body=BytesIO(base64.b64decode(inference_result)))
        return {
            "statusCode": 200,
            "body": json.dumps({
                "response_type": "s3",
                "s3_bucket": BUCKET_NAME,
                "s3_prefix": BUCKET_OUTPUT_PREFIX
            })
        }
    else:
        return {
            "statusCode": 200,
            "body": json.dumps({
                "response_type": "base64",
                "base64": inference_result
            })
        }