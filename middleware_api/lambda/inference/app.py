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

import boto3
import json
import uuid

from sagemaker.predictor import Predictor
from sagemaker.predictor_async import AsyncPredictor
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(const.LOGGER_API)
STEP_FUNCTION_ARN = os.environ.get('STEP_FUNCTION_ARN')

DDB_INFERENCE_TABLE_NAME = os.environ.get('DDB_INFERENCE_TABLE_NAME')
DDB_TRAINING_TABLE_NAME = os.environ.get('DDB_TRAINING_TABLE_NAME')
DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME = os.environ.get('DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME')

ddb_client = boto3.resource('dynamodb')
inference_table = ddb_client.Table(DDB_INFERENCE_TABLE_NAME)
endpoint_deployment_table = ddb_client.Table(DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME)

app = FastAPI(
    title="API List of SageMaker Inference",
    version="0.9",
)

def get_uuid():
    uuid_str = str(uuid.uuid4())
    return uuid_str

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

@app.get("/inference/list-endpoint-deployment-jobs/{endpoint_deployment_jobId}")
async def list_endpoint_deployment_jobs(endpoint_deployment_jobId: str):
    logger.info(f"entering list_endpoint_deployment_jobs function with jobId: {endpoint_deployment_jobdId}")
    return 0

@app.get("/inference/list-inference-jobs/{inference_jobId}")
async def list_inference_jobs(inference_jobId: str):
    logger.info(f"entering list_endpoint_deployment_jobs function with jobId: {inference_jobId}")
    return 0

#app.include_router(search) TODO: adding sub router for future

handler = Mangum(app)
add_pagination(app)