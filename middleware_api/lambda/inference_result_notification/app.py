import json
import io
import boto3
from PIL import Image
import base64

s3_resource = boto3.resource('s3')
s3_client = boto3.client('s3')

def get_bucket_and_key(s3uri):
    pos = s3uri.find('/', 5)
    bucket = s3uri[5 : pos]
    key = s3uri[pos + 1 : ]
    return bucket, key

def decode_base64_to_image(encoding):
    if encoding.startswith("data:image/"):
        encoding = encoding.split(";")[1].split(",")[1]
    return Image.open(io.BytesIO(base64.b64decode(encoding)))

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    message = event['Records'][0]['Sns']['Message']
    print("From SNS: " + message)
    invocation_status = message["invocationStatus"]
    if invocation_status == "Completed":
        print(f"Complete invocation!")
        endpoint_name = message["requestParameters"]["endpointName"]
        inference_id = message["inferenceId"]
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
            # TODO put to s3 bucket
            # s3_client.put_object(
            #     Body=output.getvalue(),
            #     Bucket=bucket,
            #     Key=f"{inference_id}_{count}.jpg"
            # )

        # save parameters
        inference_parameters = {}
        inference_parameters["parameters"] = json_body["parameters"]
        inference_parameters["info"] = json_body["info"]
        inference_parameters["endpont_name"] = endpoint_name
        inference_parameters["inference_id"] = inference_id
        inference_parameters["sns_info"] = message
        with open(f"{inference_id}_param.json", "w") as outfile:
            json.dump(inference_parameters, outfile)
        # TODO put to s3 bucket
        
        print(f"Complete inference parameters {inference_parameters}")
    else:
        print(f"Not complete invocation!")
    return message