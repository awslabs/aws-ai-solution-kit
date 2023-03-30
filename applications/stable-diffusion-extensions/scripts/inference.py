# Code below mainly to demonstrate the usage of synchronous inference function provided by middleware, it act as a client to 
# invoke the API URL created by middleware with API key and return the inference result.
import boto3
import requests
import os
import base64
import json

# Input parameters for the API URL and API key
API_URL = "cfn output from the middleware stack"
API_KEY = '12345678901234567890'
BUCKET = 'my-bucket'

BUCKET_NAME = os.environ.get("BUCKET_NAME", "my-bucket")
BUCKET_INPUT_PREFIX = os.environ.get("BUCKET_INPUT_PREFIX", "prefix/input.jpg")
BUCKET_OUTPUT_PREFIX = os.environ.get("BUCKET_OUTPUT_PREFIX", "prefix/output.jpg")
ENDPOINT_NAME = os.environ.get("ENDPOINT_NAME", API_URL)

# S3 client
s3 = boto3.client("s3")

with open("input.jpeg", "rb") as f:
    # Read image bytes from local file and encode as base64 string
    raw = f.read()
    image_bytes = base64.b64encode(raw)

    # # decode the base64 string to bytes and write to local file
    # with open("input_base64.jpg", "wb") as f:
    #     f.write(base64.b64decode(image_bytes))

    # check if input content size if larger than 6MB, if so, upload to S3 and pass the S3 bucket and prefix to the API
    # otherwise, pass the image bytes directly to the API
    if len(image_bytes) > 6*1024*1024:
        # upload the image bytes to S3
        s3.put_object(Bucket=BUCKET_NAME, Key="prefix/input.jpg", Body=image_bytes)
        input_payload = {
            "s3_bucket": BUCKET_NAME,
            "s3_prefix": BUCKET_INPUT_PREFIX
        }
    else:
        input_payload = image_bytes.decode("utf-8")
    
    # Invoke the SageMaker endpoint with image bytes
    ret = requests.post(
        ENDPOINT_NAME,
        headers={"x-api-key": API_KEY},
        # pass the input payload as json string
        data=input_payload
    )
    response = json.loads(ret.text)

    # Read the inference response to check if response contain s3_bucket and s3_prefix, if so, read the inference result from S3
    # otherwise, read the inference result from response body
    if "response_type" in response and response["response_type"] == "s3":
        bucket = response["s3_bucket"]
        output_key = response["s3_prefix"]
        # Download image bytes from S3 and write to local file
        inference_result = s3.get_object(Bucket=bucket, Key=output_key)["Body"].read()
    else:
        inference_result = response["base64"]

    with open("output.jpg", "wb") as f:
        f.write(inference_result)
