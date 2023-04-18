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

app = FastAPI(
    title="API List of SageMaker Inference",
    version="0.9",
)

def get_uuid():
    uuid_str = uuid.uuid4.str()
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
    
    print(f"output_path is {output_path}")
    return {"endpoint_name": endpoint_name, "output_path": output_path}

@app.post("/inference/deploy-sagemaker-endpoint")
async def deploy_sagemaker_endpoint(request: Request):
    logger.info("entering the deploy_sagemaker_endpoint function!")
    try:
        payload = await request.json()
        logger.info(f"input in json format {payload}")
        # item_id = data["item_id"]
        # q = data.get("q")

        resp = stepf_client.start_execution(
            stateMachineArn=STEP_FUNCTION_ARN,
            input=json.dumps(payload)
        )

        logger.info("trigger step-function with following response")

        logger.info(f"finish trigger step function for deployment with output {resp}")
        return 0
    except Exception as e:
        logger.error(f"error calling run-sagemaker-inference with exception: {e}")
        raise e

#app.include_router(search) TODO: adding sub router for future

handler = Mangum(app)
add_pagination(app)