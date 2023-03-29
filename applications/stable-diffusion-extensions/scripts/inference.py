# Code below mainly to demonstrate the usage of inference function provided by middleware, it act as a client to 
# invoke the API URL created by middleware with API key and return the inference result.
import boto3
import requests
import os

# Input parameters for the API URL and API key
API_URL = 'https://4p5tde2bne.execute-api.us-west-2.amazonaws.com/prod/inference'
API_KEY = '12345678901234567890'
BUCKET_NAME = "<your bucket>"

# S3 client
s3 = boto3.client("s3")

# Read image bytes from local file
with open("input.jpg", "rb") as f:
    image_bytes = f.read()
    # check if input content size if larger than 6MB, if so, upload to S3 and pass the S3 bucket and prefix to the API
    # otherwise, pass the image bytes directly to the API
    if len(image_bytes) > 6000000:
        # upload the image bytes to S3
        s3.put_object(Bucket=BUCKET_NAME, Key="prefix/input.jpg", Body=image_bytes)
        input_payload = {
            "s3_bucket": BUCKET_NAME,
            "s3_prefix": "prefix/input.jpg"
        }
    else:
        input_payload = image_bytes
    
    # Invoke the SageMaker endpoint with image bytes
    response = requests.post(
        API_URL,
        headers={"x-api-key": API_KEY},
        # pass the input payload as json string
        data={
            "image_bytes": input_payload
        }
    )

    print('Response content: {}'.format(response.content))

    # Read the inference response to check if response contain s3_bucket and s3_prefix, if so, read the inference result from S3
    # otherwise, read the inference result from response body
    inference_result = response["Body"].read()
    if "s3_bucket" in inference_result and "s3_prefix" in inference_result:
        bucket = inference_result["s3_bucket"]
        output_key = inference_result["s3_prefix"]
        inference_result = s3.get_object(Bucket=bucket, Key=output_key)["Body"].read().decode("utf-8")
    else:
        inference_result = inference_result.decode("utf-8")

