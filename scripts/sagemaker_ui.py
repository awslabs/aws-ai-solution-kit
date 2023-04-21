import copy
import itertools
import os
from pathlib import Path
import html
import boto3
from urllib.parse import urljoin

import gradio as gr

from modules import shared, scripts
from utils import get_variable_from_json
from utils import upload_file_to_s3_by_presign_url

inference_job_dropdown = None

#TODO: convert to dynamically init the following variables
sagemaker_endpoints = ['endpoint1', 'endpoint2']
sd_checkpoints = ['checkpoint1', 'checkpoint2']
txt2img_inference_job_ids = ['fake1', 'fake2']

textual_inversion_list = ['textual_inversion1','textual_inversion2','textual_inversion3']
lora_list = ['lora1', 'lora2', 'lora3']
hyperNetwork_list = ['hyperNetwork1', 'hyperNetwork2', 'hyperNetwork3']
ControlNet_model_list = ['controlNet_model1', 'controlNet_model2', 'controlNet_model3']

def plaintext_to_html(text):
    text = "<p>" + "<br>\n".join([f"{html.escape(x)}" for x in text.split('\n')]) + "</p>"
    return text

def get_s3_file_names(bucket, folder):
    """Get a list of file names from an S3 bucket and folder."""
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket)
    objects = bucket.objects.filter(Prefix=folder)
    names = [obj.key for obj in objects]
    return names

def server_request(path):
    api_gateway_url = get_variable_from_json('api_gateway_url');
    api_key = get_variable_from_json('api_token') 
    
    # stage 2: inference using endpoint_name
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    # list_endpoint_url = f"{api_gateway_url}{path}"
    list_endpoint_url = urljoin(api_gateway_url, path)
    response = requests.get(list_endpoint_url, headers=headers)
    print(f"response for rest api {response.json()}")
    return response

def update_sagemaker_endpoints():
    global sagemaker_endpoints

    response = server_request('inference/list-endpoint-deployment-jobs')
    r = response.json()
    sagemaker_endpoints = []
    
    for obj in r:
        if "EndpointDeploymentJobId" in obj:
            aaa_value = obj["EndpointDeploymentJobId"]
            sagemaker_endpoints.append(aaa_value)


def update_sd_checkpoints():
    global sd_checkpoints
    # aesthetic_embeddings = {f.replace(".pt", ""): os.path.join(aesthetic_embeddings_dir, f) for f in os.listdir(aesthetic_embeddings_dir) if f.endswith(".pt")}
    # aesthetic_embeddings = OrderedDict(**{"None": None}, **aesthetic_embeddings)
    # TODO update the checkpoint code here


def update_txt2img_inference_job_ids():
    global txt2img_inference_job_ids

def origin_update_txt2img_inference_job_ids():
    global origin_txt2img_inference_job_ids

def get_texual_inversion_list():
   global textual_inversion_list
   response = server_request('inference/get-texual-inversion-list')
   r = response.json()
   textual_inversion_list = []
   for obj in r:
    aaa_value = str(obj)
    textual_inversion_list.append(aaa_value)

def get_lora_list():
   global lora_list 
   response = server_request('inference/get-lora-list')
   r = response.json()
   lora_list = []
   for obj in r:
       aaa_value = str(obj)
       lora_list.append(aaa_value)

    
def get_hypernetwork_list():
   global hyperNetwork_list 
   response = server_request('inference/get-hypernetwork-list')
   r = response.json()
   hyperNetwork_list = []
   for obj in r:
       aaa_value = str(obj)
       hyperNetwork_list.append(aaa_value)

    
def get_controlnet_model_list():
   global ControlNet_model_list 
   response = server_request('inference/get-controlnet-model-list')
   r = response.json()
   ControlNet_model_list = []
   for obj in r:
       aaa_value = str(obj)
       ControlNet_model_list.append(aaa_value)

def inference_update_func():
    root_path = "/home/ubuntu/py_gpu_ubuntu_ue2_workplace/csdc/aws-ai-solution-kit/containers/stable-diffusion-webui/extensions/aws-ai-solution-kit/tests/txt2img_inference"
    from PIL import Image
    gallery = [f"{root_path}/438cf745-d164-4eca-a1bc-52fde6e7de61_0.jpg"]
    images = []
    for g in gallery:
        im = Image.open(g)
        images.append(im)
    
    json_file = f"{root_path}/438cf745-d164-4eca-a1bc-52fde6e7de61_param.json"

    f = open(json_file)

    log_file = json.load(f)

    info_text = log_file["info"]

    infotexts = json.loads(info_text)["infotexts"][0]

    return images, info_text, plaintext_to_html(infotexts)

def sagemaker_upload_model_s3(sd_checkpoints_path, textual_inversion_path, lora_path, hypernetwork_path, controlnet_model_path):
    log = "start upload model to s3..."
    print(f"Not implemented yet!")

    local_paths = [sd_checkpoints_path, textual_inversion_path, lora_path, hypernetwork_path, controlnet_model_path]
    relative_paths = ["models/Stable-diffusion", "embeddings", "models/Lora", "models/hypernetworks", "models/ControlNet"]
    
    api_key = get_variable_from_json('api_token')

    for lp, rp in zip(local_paths, relative_paths):
        if lp == "":
            continue
        print(f"lp is {lp}")
        model_name = lp.split("/")[-1]
        local_model_path_in_repo = f'{rp}{model_name}'
        local_tar_path = f'{model_name}.tar'
        print("Pack the model file.")
        os.system(f"cp -f {lp} {local_model_path_in_repo}")
        os.system(f"tar cvf {local_tar_path} {local_model_path_in_repo}")

        payload = {
            "model_type": rp,
            "name": model_name,
            "filenames": [local_tar_path],
            "params": {"message": "placeholder for chkpts upload test"}
        }

        url = get_variable_from_json('api_gateway_url') + "model"

        print("Post request for upload s3 presign url.")

        response = requests.post(url=url, json=payload, headers={'x-api-key': api_key})

        print(f"Response is {response}")
        json_response = response.json()
        print(f"Json Response is {json_response}")
        s3_base = json_response["job"]["s3_base"]
        model_id = json_response["job"]["id"]
        print(f"Upload to S3 {s3_base}")
        print(f"Model ID: {model_id}")
        # Upload src model to S3.
        for local_tar_path, s3_presigned_url in response.json()["s3PresignUrl"].items():
            upload_file_to_s3_by_presign_url(local_tar_path, s3_presigned_url)

        payload = {
            "model_id": model_id,
            "status": "Complete"
        }
        # Start creating model on cloud.
        response = requests.put(url=url, json=payload, headers={'x-api-key': api_key})
        s3_input_path = s3_base
        print(response)

        log = f"\n finish upload {local_tar_path} to {s3_base}"

        os.system(f"rm {local_tar_path}")

    return plaintext_to_html(log)

import json
import requests
from sagemaker.predictor import Predictor
from sagemaker.predictor_async import AsyncPredictor
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer
from sagemaker.async_inference.waiter_config import WaiterConfig
from sagemaker.async_inference.async_inference_response import AsyncInferenceResponse

def generate_on_cloud():
    # print(f"Current working directory: {os.getcwd()}")
    # load json files
    # stage 1: make payload
    # use txt2imgConfig.json instead of ui-config.json
    with open("ui-config.json") as f:
        params_dict = json.load(f)
    print(f"Current parameters are {params_dict}")
    endpoint_name = "infer-endpoint-bcc9"
    # get api_gateway_url
    api_gateway_url = get_variable_from_json('api_gateway_url');
    api_key = get_variable_from_json('api_token') 

    # construct payload
    payload = {
    "endpoint_name": endpoint_name,
    "task": "text-to-image", 
    "txt2img_payload": {
        "enable_hr": "False", 
        "denoising_strength": 0.7, 
        "firstphase_width": 0, 
        "firstphase_height": 0, 
        "prompt": "girl", 
        "styles": ["None", "None"], 
        "seed": -1.0, 
        "subseed": -1.0, 
        "subseed_strength": 0, 
        "seed_resize_from_h": 0, 
        "seed_resize_from_w": 0, 
        "sampler_index": "Euler a", 
        "batch_size": 1, 
        "n_iter": 1, 
        "steps": 20, 
        "cfg_scale": 7, 
        "width": 768, 
        "height": 768, 
        "restore_faces": "False", 
        "tiling": "False", 
        "negative_prompt": "", 
        "eta": 1, 
        "s_churn": 0, 
        "s_tmax": 1, 
        "s_tmin": 0, 
        "s_noise": 1, 
        "override_settings": {}, 
        "script_args": [0, "False", "False", "False", "", 1, "", 0, "", "True", "True", "True"]}, 
        "username": ""
        }
    
    # stage 2: inference using endpoint_name
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    inference_url = f"{api_gateway_url}inference/run-sagemaker-inference"
    response = requests.post(inference_url, json=payload, headers=headers)
    r = response.json()
    print(f"response for rest api {r}")

def sagemaker_deploy(instance_type, initial_instance_count=1):
    """ Create SageMaker endpoint for GPU inference.
    Args:
        instance_type (string): the ML compute instance type.
        initial_instance_count (integer): Number of instances to launch initially.
    Returns:
        (None)
    """
    # function code to call sagemaker deploy api
    print(f"start deploying instance type: {instance_type} with count {initial_instance_count}............")

    # get api_gateway_url
    api_gateway_url = get_variable_from_json('api_gateway_url');
    api_key = get_variable_from_json('api_token') 

    payload = {
    "instance_type": instance_type,
    "initial_instance_count": initial_instance_count
    }

    deployment_url = f"{api_gateway_url}inference/deploy-sagemaker-endpoint"

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    response = requests.post(deployment_url, json=payload, headers=headers)
    r = response.json()
    print(f"response for rest api {r}")

def txt2img_config_save():
    # placeholder for saving txt2img config
    pass

def create_ui():
    global txt2img_gallery, txt2img_generation_info
    import modules.ui

    if get_variable_from_json('api_gateway_url') is not None:
        # update_sagemaker_endpoints()
        get_texual_inversion_list()
        get_lora_list()
        get_hypernetwork_list()
        get_controlnet_model_list()
    else:
        print(f"there is no api-gateway url and token in local file,")
    
    
    with gr.Group():
        with gr.Accordion("Open for SageMaker Inference!", open=False):
            sagemaker_html_log = gr.HTML(elem_id=f'html_log_sagemaker')
            with gr.Column(variant='panel'):
                with gr.Row():
                    sagemaker_endpoint = gr.Dropdown(sagemaker_endpoints,
                                             label="Select Cloud SageMaker Endpoint"
                                             )
                    modules.ui.create_refresh_button(sagemaker_endpoint, update_sagemaker_endpoints, lambda: {"choices": sagemaker_endpoints}, "refresh_sagemaker_endpoints")
                with gr.Row():
                    sd_checkpoint = gr.Dropdown(sd_checkpoints,
                                             label="Stable Diffusion Checkpoint")
                    sd_checkpoint_refresh_button = modules.ui.create_refresh_button(sd_checkpoint, update_sd_checkpoints, lambda: {"choices": sd_checkpoints}, "refresh_sd_checkpoints")
            with gr.Column():
                generate_on_cloud_button = gr.Button(value="Generate on Cloud (Please save settings before !)", variant='primary')
                generate_on_cloud_button.click(
                    fn=generate_on_cloud,
                    inputs=[],
                    outputs=[]
                )
                txt2img_config_save_button = gr.Button(value="Save Settings", variant='primary')
                txt2img_config_save_button.click(
                    _js="txt2img_config_save",
                    fn=txt2img_config_save,
                    inputs=[],
                    outputs=[]
                )
            with gr.Row():
                global inference_job_dropdown
                inference_job_dropdown = gr.Dropdown(txt2img_inference_job_ids,
                                            label="Inference Job IDs")
                txt2img_inference_job_ids_refresh_button = modules.ui.create_refresh_button(inference_job_dropdown, update_txt2img_inference_job_ids, lambda: {"choices": txt2img_inference_job_ids}, "refresh_txt2img_inference_job_ids")
            with gr.Row():
                gr.HTML(value="Extra Networks for Sagemaker Endpoint")
                advanced_model_refresh_button = modules.ui.create_refresh_button(sd_checkpoint, update_sd_checkpoints, lambda: {"choices": sorted(sd_checkpoints)}, "refresh_sd_checkpoints")
            
            with gr.Row():
                textual_inversion_dropdown = gr.Dropdown(textual_inversion_list, multiselect=True, label="Textual Inversion")
                lora_dropdown = gr.Dropdown(lora_list,  multiselect=True, label="LoRA")
            with gr.Row():
                hyperNetwork_dropdown = gr.Dropdown(hyperNetwork_list, multiselect=True, label="HyperNetwork")
                controlnet_dropdown = gr.Dropdown(ControlNet_model_list, multiselect=True, label="ControlNet-Model")

            with gr.Row():
                sd_checkpoints_path = gr.Textbox(value="", lines=1, placeholder="Please input absolute path", label="Stable Diffusion Checkpoints")
                textual_inversion_path = gr.Textbox(value="", lines=1, placeholder="Please input absolute path", label="Textual Inversion")
                lora_path = gr.Textbox(value="", lines=1, placeholder="Please input absolute path", label="LoRA")
                hypernetwork_path = gr.Textbox(value="", lines=1, placeholder="Please input absolute path", label="HyperNetwork")
                controlnet_model_path = gr.Textbox(value="", lines=1, placeholder="Please input absolute path", label="ControlNet-Model")
                model_update_button = gr.Button(value="Upload Models to S3", variant="primary")
                model_update_button.click(sagemaker_upload_model_s3, \
                                          inputs = [sd_checkpoints_path, \
                                                    textual_inversion_path, \
                                                    lora_path, \
                                                    hypernetwork_path, \
                                                    controlnet_model_path], \
                                           outputs = [sagemaker_html_log])
            
            gr.HTML(value="Deploy New SageMaker Endpoint")
            with gr.Row():
                instance_type_textbox = gr.Textbox(value="", lines=1, placeholder="Please enter Instance type", label="SageMaker Instance Type")
                sagemaker_deploy_button = gr.Button(value="Deploy", variant='primary')
                sagemaker_deploy_button.click(sagemaker_deploy, inputs = [instance_type_textbox])

    return  sagemaker_endpoint, sd_checkpoint, sd_checkpoint_refresh_button, generate_on_cloud_button, advanced_model_refresh_button, textual_inversion_dropdown, lora_dropdown, hyperNetwork_dropdown, controlnet_dropdown, instance_type_textbox, sagemaker_deploy_button, inference_job_dropdown, txt2img_inference_job_ids_refresh_button
