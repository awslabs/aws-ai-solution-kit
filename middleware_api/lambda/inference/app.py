import time
import logging
import logging.config
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from mangum import Mangum
from common.response_wrapper import resp_err
from common.enum import MessageEnum
from common.constant import const
from common.exception_handler import biz_exception
from fastapi_pagination import add_pagination
from datetime import datetime
from typing import List

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
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
sagemaker = boto3.client('sagemaker')
inference_table = ddb_client.Table(DDB_INFERENCE_TABLE_NAME)
endpoint_deployment_table = ddb_client.Table(DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME)

async def custom_exception_handler(request: Request, exc: HTTPException):
    headers = {
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
    }
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers
    )

app = FastAPI(
    title="API List of SageMaker Inference",
    version="0.9",
)
app.exception_handler(HTTPException)(custom_exception_handler)

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
    try:
        sagemaker = boto3.client('sagemaker')
        ddb = boto3.resource('dynamodb')
        endpoint_deployment_table = ddb.Table(DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME)

        response = endpoint_deployment_table.scan()
        logger.info(f"endpoint deployment job list response is {str(response)}")

        # Get the list of SageMaker endpoints
        list_results = sagemaker.list_endpoints()
        sagemaker_endpoints = [ep_info['EndpointName'] for ep_info in list_results['Endpoints']]
        logger.info(str(sagemaker_endpoints))

        # Filter the endpoint job list
        filtered_endpoint_jobs = []
        for job in response['Items']:
            if 'endpoint_name' in job:  
                endpoint_name = job['endpoint_name']
                deployment_job_id = job['EndpointDeploymentJobId']

                if endpoint_name in sagemaker_endpoints:
                    filtered_endpoint_jobs.append(job)
                else:
                    # Remove the job item from the DynamoDB table if the endpoint doesn't exist in SageMaker
                    endpoint_deployment_table.delete_item(Key={'EndpointDeploymentJobId': deployment_job_id})

        return filtered_endpoint_jobs

    except ClientError as e:
        print(f"An error occurred: {e}")
        return []

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

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
 
def load_json_from_s3(bucket_name, key):
    # Create an S3 client

    # Get the JSON file from the specified bucket and key
    response = s3.get_object(Bucket=bucket_name, Key=key)
    json_file = response['Body'].read().decode('utf-8')

    # Load the JSON file into a dictionary
    data = json.loads(json_file)

    return data

def json_convert_to_payload(params_dict, checkpoint_info):
    # Need to generate the payload from data_dict here:
    script_name = params_dict['script_list']
    if script_name == "None":
        script_name = ""
    script_args = []
    if script_name == 'Prompt matrix':
        put_at_start = params_dict['script_txt2txt_prompt_matrix_put_at_start']
        different_seeds = params_dict['script_txt2txt_prompt_matrix_different_seeds']
        if params_dict['script_txt2txt_prompt_matrix_prompt_type_positive']:
            prompt_type = "positive"
        else:
            prompt_type = "negative"
        if params_dict['script_txt2txt_prompt_matrix_variations_delimiter_comma']: 
            variations_delimiter = "comma"
        else:
            variations_delimiter = "space"
        margin_size = params_dict['script_txt2txt_prompt_matrix_margin_size']
        script_args = [put_at_start, different_seeds, prompt_type, variations_delimiter, margin_size]

    if script_name == 'Prompts from file or textbox':
        checkbox_iterate = params_dict['script_txt2txt_prompts_from_file_or_textbox_checkbox_iterate']
        checkbox_iterate_batch = params_dict['script_txt2txt_prompts_from_file_or_textbox_checkbox_iterate_batch']
        list_prompt_inputs = params_dict['script_txt2txt_prompts_from_file_or_textbox_prompt_txt']
        lines = [x.strip() for x in list_prompt_inputs.decode('utf8', errors='ignore').split("\n")]
        script_args = [checkbox_iterate, checkbox_iterate_batch, "\n".join(lines)]

    if script_name == 'X/Y/Z plot':
        type_dict = {'Nothing': 0,
                       'Seed': 1,
                       'Var. seed': 2,
                       'Var. strength': 3,
                       'Steps': 4,
                       'Hires stteps': 5,
                       'CFG Scale': 6,
                       'Prompt S/R': 7,
                       'Prompt order': 8,
                       'Sampler': 9,
                       'Checkpoint name': 10,
                       'Negative Guidance minimum sigma': 11,
                       'Sigma Churn': 12,
                       'Sigma min': 13,
                       'Sigma max': 14,
                       'Sigma noise': 15,
                       'Eta': 16,
                       'Clip skip': 17,
                       'Denoising': 18,
                       'Hires upscaler': 19,
                       'VAE': 20,
                       'Styles': 21,
                       'UniPC Order': 22,
                       'Face restore': 23,
                       '[ControlNet] Enabled': 24,
                       '[ControlNet] Model': 25,
                       '[ControlNet] Weight': 26,
                       '[ControlNet] Guidance Start': 27,
                       '[ControlNet] Guidance End': 28,
                       '[ControlNet] Resize Mode': 29,
                       '[ControlNet] Preprocessor': 30,
                       '[ControlNet] Pre Resolution': 31,
                       '[ControlNet] Pre Threshold A': 32,
                       '[ControlNet] Pre Threshold B': 33}
        dropdown_index = [9, 10, 19, 20, 21, 24, 25, 29, 30]
        x_type = type_dict[params_dict['script_txt2txt_xyz_plot_x_type']]
        x_values = params_dict['script_txt2txt_xyz_plot_x_values']
        x_values_dropdown = params_dict['script_txt2txt_xyz_plot_x_values']
        if x_type in dropdown_index:
            if x_type == 10:
                x_values_dropdown = params_dict['sagemaker_stable_diffusion_checkpoint']
            elif x_type == 25:
                x_values_dropdown = params_dict['sagemaker_controlnet_model']
            x_values_dropdown = x_values_dropdown.split(":")
        
        y_type = type_dict[params_dict['script_txt2txt_xyz_plot_y_type']]
        y_values = params_dict['script_txt2txt_xyz_plot_y_values']
        y_values_dropdown = params_dict['script_txt2txt_xyz_plot_y_values']
        if y_type in dropdown_index:
            if y_type == 10:
                y_values_dropdown = params_dict['sagemaker_stable_diffusion_checkpoint']
            elif y_type == 25:
                y_values_dropdown = params_dict['sagemaker_controlnet_model']
            y_values_dropdown = y_values_dropdown.split(":")
        
        z_type = type_dict[params_dict['script_txt2txt_xyz_plot_z_type']]
        z_values = params_dict['script_txt2txt_xyz_plot_z_values']
        z_values_dropdown = params_dict['script_txt2txt_xyz_plot_z_values']
        if z_type in dropdown_index:
            if z_type == 10:
                z_values_dropdown = params_dict['sagemaker_stable_diffusion_checkpoint']
            elif z_type == 25:
                z_values_dropdown = params_dict['sagemaker_controlnet_model']
            z_values_dropdown = z_values_dropdown.split(":")
        
        draw_legend = params_dict['script_txt2txt_xyz_plot_draw_legend']
        include_lone_images = params_dict['script_txt2txt_xyz_plot_include_lone_images']
        include_sub_grids = params_dict['script_txt2txt_xyz_plot_include_sub_grids']
        no_fixed_seeds = params_dict['script_txt2txt_xyz_plot_no_fixed_seeds']
        margin_size = int(params_dict['script_txt2txt_xyz_plot_margin_size'])
        script_args = [x_type, x_values, x_values_dropdown, y_type, y_values, y_values_dropdown, z_type, z_values, z_values_dropdown, draw_legend, include_lone_images, include_sub_grids, no_fixed_seeds, margin_size]

    # get all parameters from ui-config.json
    prompt = params_dict['txt2img_prompt'] #'chinese, beautiful woman' # 'a busy city street in a modern city | illustration | cinematic lighting' #
    negative_prompt = params_dict['txt2img_neg_prompt']#: "", 
    enable_hr = params_dict['txt2img_enable_hr'] #: "False", 
    denoising_strength = float(params_dict['txt2img_denoising_strength']) #: 0.7, 
    hr_scale = float(params_dict['txt2img_hr_scale'])
    hr_upscaler = params_dict['txt2img_hr_upscaler'] #hr_upscaler,
    hr_second_pass_steps = int(params_dict['txt2img_hires_steps']) #hr_second_pass_steps,
    firstphase_width = int(params_dict['txt2img_hr_resize_x'])#: 0, 
    firstphase_height = int(params_dict['txt2img_hr_resize_y'])#: 0, 
    styles = params_dict['txt2img_styles']#: ["None", "None"], 
    if styles == "":
        styles = []
    seed = float(params_dict['txt2img_seed'])#: -1.0, 
    subseed = float(params_dict['txt2img_subseed'])#: -1.0, 
    subseed_strength = float(params_dict['txt2img_subseed_strength'])#: 0, 
    seed_resize_from_h = int(params_dict['txt2img_seed_resize_from_h'])#: 0, 
    seed_resize_from_w = int(params_dict['txt2img_seed_resize_from_w'])#: 0, 
    sampler_index = params_dict['txt2img_sampling_method']#: "Euler a", 
    batch_size = int(params_dict['txt2img_batch_size'])#: 1, 
    n_iter = int(params_dict['txt2img_batch_count'])
    steps = int(params_dict['txt2img_steps'])#: 20, 
    cfg_scale = int(params_dict['txt2img_cfg_scale'])#: 7, 
    width = int(params_dict['txt2img_width'])#: 512, 
    height = int(params_dict['txt2img_height'])#: 512, 
    restore_faces = params_dict['txt2img_restore_faces']#: "False", 
    tiling = params_dict['txt2img_tiling']#: "False", 
    override_settings = {}
    eta = 1
    s_churn = 0
    s_tmax = 1
    s_tmin = 0
    s_noise = 1 

    selected_sd_model = params_dict['sagemaker_stable_diffusion_checkpoint'] #'my_girl_311.safetensors'my_style_132.safetensors my_style_132.safetensors
    selected_cn_model = params_dict['sagemaker_controlnet_model']#['control_openpose-fp16.safetensors']#
    selected_hypernets = params_dict['sagemaker_hypernetwork_model']#['mjv4Hypernetwork_v1.pt']#'LuisapKawaii_v1.pt'
    selected_loras = params_dict['sagemaker_lora_model']#['hanfu_v30Song.safetensors']# 'cuteGirlMix4_v10.safetensors'
    selected_embeddings = params_dict['sagemaker_texual_inversion_model']#['pureerosface_v1.pt']#'corneo_marin_kitagawa.pt''pureerosface_v1.pt'
    
    if selected_sd_model == "":
        selected_sd_model = ['v1-5-pruned-emaonly.safetensors']
    else:
        selected_sd_model = selected_sd_model.split(":")
    if selected_cn_model == "":
        selected_cn_model = []
    else:
        selected_cn_model = selected_cn_model.split(":")
    if selected_hypernets == "":
        selected_hypernets = []
    else:
        selected_hypernets = selected_hypernets.split(":")
    if selected_loras == "":
        selected_loras = []
    else:
        selected_loras = selected_loras.split(":")
    if selected_embeddings == "":
        selected_embeddings = []
    else:
        selected_embeddings = selected_embeddings.split(":")
    
    for embedding in selected_embeddings:
        prompt = prompt + embedding
    for hypernet in selected_hypernets:
        hypernet_name = os.path.splitext(hypernet)[0]
        prompt = prompt + f"<hypernet:{hypernet_name}:1>"
    for lora in selected_loras:
        lora_name = os.path.splitext(lora)[0]
        prompt = prompt + f"<lora:{lora_name}:1>"
    
    contronet_enable = False
    controlnet_model = None
    controlnet_module = None
    controlnet_image = None
    if contronet_enable:
        controlnet_module = params_dict['controlnet_preprocessor']
        controlnet_model = os.path.splitext(selected_cn_model[0])[0]
        controlnet_image = params_dict['txt2img_controlnet_ControlNet_input_image'] #None
        weight = params_dict['control_weight'] #1,
        resize_mode = params_dict['controlnet_resize_mode'] # "Crop and Resize",
        lowvram = params_dict['controlnet_lowVRAM_enable'] #: "False",
        processor_res = 64,
        threshold_a = 64,
        threshold_b = 64,
        guidance = 1,
        guidance_start = params_dict['controlnet_starting_control_step'] #: 0,
        guidance_end = params_dict['controlnet_ending_control_step'] #: 1,
        guessmode = params_dict['controlnet_control_mode(guess_mode)'] #: "True",
        pixel_perfect = params_dict['controlnet_pixel_perfect'] #:"False"
        allow_preview = params_dict['controlnet_allow_preview']
        loopback = params_dict['controlnet_loopback_automatically_send_generated_images_to_this_controlnet_unit']

        #with open(controlnet_image_path, "rb") as img:
        # controlnet_image = base64.b64encode(img.read())

    endpoint_name = params_dict['sagemaker_endpoint'] #"infer-endpoint-ca0e"
    
    if contronet_enable:
        print('txt2img with controlnet!!!!!!!!!!')
        payload = {
        "endpoint_name": endpoint_name,
        "task": "controlnet_txt2img", 
        "username": "test",
        "checkpoint_info":checkpoint_info,
        "models":{
            "space_free_size": 4e10,
            "Stable-diffusion": selected_sd_model,
            "ControlNet": selected_cn_model,
            "hypernetworks": selected_hypernets,
            "Lora": selected_loras,
            "embeddings": selected_embeddings
        },
        "controlnet_txt2img_payload":{ 
            "enable_hr": enable_hr, 
            "denoising_strength": denoising_strength, 
            "firstphase_width": firstphase_width, 
            "firstphase_height": firstphase_height, 
            "prompt": prompt, 
            "styles": styles, 
            "seed": seed, 
            "subseed": subseed, 
            "subseed_strength": subseed_strength, 
            "seed_resize_from_h": seed_resize_from_h, 
            "seed_resize_from_w": seed_resize_from_w, 
            "sampler_index": sampler_index, 
            "batch_size": batch_size, 
            "n_iter": n_iter, 
            "steps": steps, 
            "cfg_scale": cfg_scale, 
            "width": width, 
            "height": height, 
            "restore_faces": restore_faces, 
            "tiling": tiling, 
            "negative_prompt": negative_prompt, 
            "eta": eta, 
            "s_churn": s_churn, 
            "s_tmax": s_tmax, 
            "s_tmin": s_tmin, 
            "s_noise": s_noise, 
            "override_settings": override_settings, 
            "script_name": script_name,
            "script_args": script_args,
            "controlnet_units": [
                {
                "input_image": controlnet_image,
                "mask": "",
                "module": controlnet_module,
                "model": controlnet_model,
                "weight": weight,
                "resize_mode": resize_mode,
                "lowvram": lowvram,
                "processor_res": processor_res,
                "threshold_a": threshold_a,
                "threshold_b": threshold_b,
                "guidance": guidance,
                "guidance_start": guidance_start,
                "guidance_end": guidance_end,
                "guessmode": guessmode,
                "pixel_perfect": pixel_perfect
                }
            ]
        }, 
        }
    else:
        print('txt2img ##########')
        # construct payload
        payload = {
        "endpoint_name": endpoint_name,
        "task": "text-to-image", 
        "username": "test",
        "checkpoint_info":checkpoint_info,
        "models":{
            "space_free_size": 2e10,
            "Stable-diffusion": selected_sd_model,
            "ControlNet": [],
            "hypernetworks": selected_hypernets,
            "Lora": selected_loras,
            "embeddings": selected_embeddings
        },
        "txt2img_payload": {
            "enable_hr": enable_hr, 
            "denoising_strength": denoising_strength, 
            "firstphase_width": firstphase_width, 
            "firstphase_height": firstphase_height, 
            "prompt": prompt, 
            "styles": styles, 
            "seed": seed, 
            "subseed": subseed, 
            "subseed_strength": subseed_strength, 
            "seed_resize_from_h": seed_resize_from_h, 
            "seed_resize_from_w": seed_resize_from_w, 
            "sampler_index": sampler_index, 
            "batch_size": batch_size, 
            "n_iter": n_iter, 
            "steps": steps, 
            "cfg_scale": cfg_scale, 
            "width": width, 
            "height": height, 
            "restore_faces": restore_faces, 
            "tiling": tiling, 
            "negative_prompt": negative_prompt, 
            "eta": eta, 
            "s_churn": s_churn, 
            "s_tmax": s_tmax, 
            "s_tmin": s_tmin, 
            "s_noise": s_noise, 
            "override_settings": override_settings, 
            "script_name": script_name,
            "script_args": script_args}, 
        }
    return payload
 
# Global exception capture
# All exception handling in the code can be written as: raise BizException(code=500, message="XXXX")
# Among them, code is the business failure code, and message is the content of the failure
# biz_exception(app)
stepf_client = boto3.client('stepfunctions')

@app.get("/")
def root():
    return {"message": const.SOLUTION_NAME}

@app.post("/inference/run-sagemaker-inference")
async def run_sagemaker_inference(request: Request):
    try:
        logger.info('entering the run_sage_maker_inference function!')

        # TODO: add logic for inference id
        inference_id = get_uuid()

        payload_checkpoint_info = await request.json()
        print(f"!!!!!!!!!!input in json format {payload_checkpoint_info}")

        params_dict = load_json_from_s3(S3_BUCKET_NAME, 'config/aigc.json')

        logger.info(json.dumps(params_dict))
        payload = json_convert_to_payload(params_dict, payload_checkpoint_info)
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
                'startTime': current_time,
                'status': 'inprogress'
            })
        print(f"output_path is {output_path}")

        headers = {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        }

        response = JSONResponse(content={"inference_id": inference_id, "status": "inprogress", "endpoint_name": endpoint_name, "output_path": output_path}, headers=headers)
        #response = JSONResponse(content={"inference_id": '6fa743f0-cb7a-496f-8205-dbd67df08be2', "status": "succeed", "output_path": ""}, headers=headers)
        return response

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")

        # raise HTTPException(status_code=500, detail=f"An error occurred during processing.{str(e)}")
        headers = {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        }

        response = JSONResponse(content={"inference_id": inference_id, "status":"failure", "error": f"error info {str(e)}"}, headers=headers)
        return response

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
            'startTime': current_time,
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

@app.get("/inference/get-inference-job-param-output")
async def get_inference_job_param_output(jobID: str = None) -> List[str]:
    inference_jobId = jobID

    if inference_jobId is None or inference_jobId.strip() == "":
        logger.info(f"jobId is empty string or None, just return empty string list")
        return [] 

    logger.info(f"Entering get_inference_job_param_output function with jobId: {inference_jobId}")

    job_record = getInferenceJob(inference_jobId)

    presigned_url = ""

    json_key = f"out/{inference_jobId}/result/{inference_jobId}_param.json"
    presigned_url = generate_presigned_url(S3_BUCKET_NAME, json_key)

    return [presigned_url]

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


@app.get("/inference/generate-s3-presigned-url-for-uploading")
async def generate_s3_presigned_url_for_uploading(s3_bucket_name: str = None, key: str = None):
    s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
    if not s3_bucket_name:
        s3_bucket_name = S3_BUCKET_NAME

    if not key:
        raise HTTPException(status_code=400, detail="Key parameter is required")

    presigned_url = s3.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': s3_bucket_name,
            'Key': key,
            'ContentType': 'text/plain;charset=UTF-8'
        },
        ExpiresIn=3600,
        HttpMethod='PUT'
    )
    headers = {
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
    }

    response = JSONResponse(content=presigned_url, headers=headers)

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