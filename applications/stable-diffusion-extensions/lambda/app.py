import json
import boto3
import os

sagemaker = boto3.client("sagemaker-runtime")
s3 = boto3.client("s3")

# Get endpoint name from environment variable
ENDPOINT_NAME = os.environ["ENDPOINT_NAME"]

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
    print(f"Invoking endpoint {ENDPOINT_NAME} with payload {input_payload}")

    # Invoke the SageMaker endpoint with image bytes
    response = sagemaker.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="application/json",
        # wrappayload in a json string for this example
        Body=json.dumps({"img": input_payload})
    )

    # Read the inference response
    inference_result = response["Body"].read()
    print(f"Inference result: {inference_result}")

    # Save the inference response to S3 if it exceeds payload size limits
    if len(inference_result) > 6000000:  # Adjust the limit based on your payload size limits (e.g., 6 MB)
        output_key = f"output/{input_key}"
        s3.put_object(Bucket=bucket, Key=output_key, Body=inference_result)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Inference result saved in S3",
                "s3_bucket": bucket,
                "s3_prefix": output_key
            })
        }
    else:
        return {
            "statusCode": 200,
            "body": inference_result.decode("utf-8")
        }