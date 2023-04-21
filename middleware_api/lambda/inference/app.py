import time
import logging
import logging.config
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mangum import Mangum
from common.response_wrapper import resp_err
from common.enum import MessageEnum
from common.constant import const
from common.exception_handler import biz_exception
from fastapi_pagination import add_pagination
from datetime import datetime
from typing import List

import boto3
import json
import uuid

from sagemaker.predictor import Predictor
from sagemaker.predictor_async import AsyncPredictor
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer
from boto3.dynamodb.conditions import Attr, Key

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(const.LOGGER_API)
STEP_FUNCTION_ARN = os.environ.get('STEP_FUNCTION_ARN')

DDB_INFERENCE_TABLE_NAME = os.environ.get('DDB_INFERENCE_TABLE_NAME')
DDB_TRAINING_TABLE_NAME = os.environ.get('DDB_TRAINING_TABLE_NAME')
DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME = os.environ.get('DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET')

ddb_client = boto3.resource('dynamodb')
s3 = boto3.client('s3')
inference_table = ddb_client.Table(DDB_INFERENCE_TABLE_NAME)
endpoint_deployment_table = ddb_client.Table(DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME)

app = FastAPI(
    title="API List of SageMaker Inference",
    version="0.9",
)

def get_uuid():
    uuid_str = str(uuid.uuid4())
    return uuid_str

def updateInferenceJobTable(inference_id, status):
    #update the inference DDB for the job status
    response = inference_table.get_item(
            Key={
                "InferenceJobId": inference_id,
            })
    inference_resp = response['Item']
    if not inference_resp:
        raise Exception(f"Failed to get the inference job item with inference id:{inference_id}")

    response = inference_table.update_item(
            Key={
                "InferenceJobId": inference_id,
            },
            UpdateExpression="set status = :r",
            ExpressionAttributeValues={':r': status},
            ReturnValues="UPDATED_NEW")

def getInferenceJobList():
    response = inference_table.scan()
    logger.info(f"inference job list response is {str(response)}")
    return response['Items']

    
def getInferenceJob(inference_job_id):
    try:
        resp = inference_table.query(
            KeyConditionExpression=Key('InferenceJobId').eq(inference_job_id)
        )
        logger.info(resp)
    except Exception as e:
        logger.error(e)
    record_list = resp['Items']
    if len(record_list) == 0:
        raise Exception("There is no inference job info item for id:" + inference_job_id)
    return record_list[0]
    
def getEndpointDeploymentJobList():
    response = endpoint_deployment_table.scan()
    logger.info(f"endpoint deployment job list response is {str(response)}")
    return response['Items'] 

def getEndpointDeployJob(endpoint_deploy_job_id):
    try:
        resp = endpoint_deployment_table.query(
            KeyConditionExpression=Key('EndpointDeploymentJobId').eq(endpoint_deploy_job_id)
        )
        log.info(resp)
    except Exception as e:
        logging.error(e)
    record_list = resp['Items']
    if len(record_list) == 0:
        raise Exception("There is no endpoint deployment job info item for id:" + endpoint_deploy_job_id)
    return record_list[0]

def get_s3_objects(bucket_name, folder_name):
    # Ensure the folder name ends with a slash
    if not folder_name.endswith('/'):
        folder_name += '/'

    # List objects in the specified bucket and folder
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)

    # Extract object names from the response
    # object_names = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'] != folder_name]
    object_names = [obj['Key'][len(folder_name):] for obj in response.get('Contents', []) if obj['Key'] != folder_name]

    return object_names
 
# Global exception capture
# All exception handling in the code can be written as: raise BizException(code=500, message="XXXX")
# Among them, code is the business failure code, and message is the content of the failure
biz_exception(app)
stepf_client = boto3.client('stepfunctions')

@app.get("/")
def root():
    return {"message": const.SOLUTION_NAME}

@app.post("/inference/run-sagemaker-inference")
async def run_sagemaker_inference(request: Request):
    logger.info('entering the run_sage_maker_inference function!')

    # TODO: add logic for inference id
    inference_id = get_uuid() 

    payload = await request.json()
    print(f"input in json format {payload}")
    endpoint_name = payload["endpoint_name"]

    predictor = Predictor(endpoint_name)

    predictor = AsyncPredictor(predictor, name=endpoint_name)
    predictor.serializer = JSONSerializer()
    predictor.deserializer = JSONDeserializer()
    prediction = predictor.predict_async(data=payload, inference_id=inference_id)
    output_path = prediction.output_path

    #put the item to inference DDB for later check status
    current_time = str(datetime.now())
    response = inference_table.put_item(
        Item={
            'InferenceJobId': inference_id,
            'dateTime': current_time,
            'status': 'inprogress'
        })
    
    print(f"output_path is {output_path}")
    return {"endpoint_name": endpoint_name, "output_path": output_path}

@app.post("/inference/deploy-sagemaker-endpoint")
async def deploy_sagemaker_endpoint(request: Request):
    logger.info("entering the deploy_sagemaker_endpoint function!")
    try:
        payload = await request.json()
        endpoint_deployment_id = get_uuid()
        logger.info(f"input in json format {payload}")
        payload['endpoint_deployment_id'] = endpoint_deployment_id

        resp = stepf_client.start_execution(
            stateMachineArn=STEP_FUNCTION_ARN,
            input=json.dumps(payload)
        )

        #put the item to inference DDB for later check status
        current_time = str(datetime.now())
        response = endpoint_deployment_table.put_item(
        Item={
            'EndpointDeploymentJobId': endpoint_deployment_id,
            'dateTime': current_time,
            'status': 'inprogress'
        })

        logger.info("trigger step-function with following response")

        logger.info(f"finish trigger step function for deployment with output {resp}")
        return 0
    except Exception as e:
        logger.error(f"error calling run-sagemaker-inference with exception: {e}")
        raise e

@app.get("/inference/list-endpoint-deployment-jobs")
async def list_endpoint_deployment_jobs():
    logger.info(f"entering list_endpoint_deployment_jobs")
    return getEndpointDeploymentJobList()

@app.get("/inference/list-inference-jobs")
async def list_inference_jobs():
    logger.info(f"entering list_endpoint_deployment_jobs") 
    return getInferenceJobList()

@app.get("/inference/get-endpoint-deployment-job")
async def get_endpoint_deployment_job(jobID: str = None):
    logger.info(f"entering get_endpoint_deployment_job function ")
    # endpoint_deployment_jobId = request.query_params 
    endpoint_deployment_jobId = jobID 
    logger.info(f"endpoint_deployment_jobId is {str(endpoint_deployment_jobId)}")
    return getEndpointDeployJob(endpoint_deployment_jobId) 

@app.get("/inference/get-inference-job")
async def get_inference_job(jobID: str = None):
    inference_jobId = jobID
    logger.info(f"entering get_inference_job function with jobId: {inference_jobId}")
    return getInferenceJob(inference_jobId)

@app.get("/inference/get-inference-job-image-output")
async def get_inference_job_image_output(jobID: str = None) -> List[str]:
    inference_jobId = jobID

    if inference_jobId is None or inference_jobId.strip() == "":
        logger.info(f"jobId is empty string or None, just return empty string list")
        return []

    logger.info(f"Entering get_inference_job_image_output function with jobId: {inference_jobId}")

    job_record = getInferenceJob(inference_jobId)

    # Assuming the job_record contains a list of image names
    image_names = job_record["image_names"]

    presigned_urls = []

    for image_name in image_names:
        image_key = f"out/{inference_jobId}/result/{image_name}"
        presigned_url = generate_presigned_url(S3_BUCKET_NAME, image_key)
        presigned_urls.append(presigned_url)

    return presigned_urls

def generate_presigned_url(bucket_name: str, key: str, expiration=3600) -> str:
    try:
        response = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': key},
            ExpiresIn=expiration
        )
    except Exception as e:
        logger.error(f"Error generating presigned URL: {e}")
        raise

    return response


@app.get("/inference/get-texual-inversion-list")
async def get_texual_inversion_list():
    logger.info(f"entering get_texual_inversion_list()")
    return get_s3_objects(S3_BUCKET_NAME,'texual_inversion') 

@app.get("/inference/get-lora-list")
async def get_lora_list():
    return get_s3_objects(S3_BUCKET_NAME,'lora') 

@app.get("/inference/get-hypernetwork-list")
async def get_hypernetwork_list():
    return get_s3_objects(S3_BUCKET_NAME,'hypernetwork')

@app.get("/inference/get-controlnet-model-list")
async def get_controlnet_model_list():
    return get_s3_objects(S3_BUCKET_NAME,'controlnet')



#app.include_router(search) TODO: adding sub router for future

handler = Mangum(app)
add_pagination(app)