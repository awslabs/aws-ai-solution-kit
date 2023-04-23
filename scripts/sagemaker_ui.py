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
from datetime import datetime

inference_job_dropdown = None

#TODO: convert to dynamically init the following variables
sagemaker_endpoints = ['endpoint1', 'endpoint2']
sd_checkpoints = ['checkpoint1', 'checkpoint2']
txt2img_inference_job_ids = ['fake1', 'fake2']

textual_inversion_list = ['textual_inversion1','textual_inversion2','textual_inversion3']
lora_list = ['lora1', 'lora2', 'lora3']
hyperNetwork_list = ['hyperNetwork1', 'hyperNetwork2', 'hyperNetwork3']
ControlNet_model_list = ['controlNet_model1', 'controlNet_model2', 'controlNet_model3']

# Initial checkpoints information
checkpoint_info = {}
checkpoint_type = ["Stable-diffusion", "embeddings", "Lora", "hypernetworks", "ControlNet"]
for ckpt_type in checkpoint_type:
    checkpoint_info[ckpt_type] = {}

# get api_gateway_url
api_gateway_url = get_variable_from_json('api_gateway_url')
api_key = get_variable_from_json('api_token') 

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

def get_current_date():
    today = datetime.today()
    formatted_date = today.strftime('%Y-%m-%d')
    return formatted_date

def server_request(path):
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
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

def get_inference_job_list():
    global txt2img_inference_job_ids
    response = server_request('inference/list-inference-jobs')
    r = response.json()
    if r:
        txt2img_inference_job_ids.clear()  # Clear the existing list before appending new values
        for obj in r:
            json_string = json.dumps(obj)
            txt2img_inference_job_ids.append(json_string)
    else:
        print("The API response is empty.")

def get_inference_job_image_output(inference_job_id):
    response = server_request(f'inference/get-inference-job-image-output?jobID={inference_job_id}')
    r = response.json()
    txt2img_inference_job_image_list = []
    for obj in r:
        aaa_value = str(obj)
        txt2img_inference_job_image_list.append(aaa_value)
    return txt2img_inference_job_image_list

def download_images(image_urls: list, local_directory: str):
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    image_list = []
    for url in image_urls:
        response = requests.get(url)
        if response.status_code == 200:
            image_name = os.path.basename(url).split('?')[0]
            local_path = os.path.join(local_directory, image_name)
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            image_list.append(local_path)
        else:
            print(f"Error downloading image {url}: {response.status_code}")
    return image_list
    
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
   hyperNetwork_list = list(checkpoint_info["hypernetworks"].keys())
#    response = server_request('inference/get-hypernetwork-list')
#    r = response.json()
#    hyperNetwork_list = []
#    for obj in r:
#        aaa_value = str(obj)
#        hyperNetwork_list.append(aaa_value)

    
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

    for lp, rp in zip(local_paths, checkpoint_type):
        if lp == "":
            continue
        print(f"lp is {lp}")
        model_name = lp.split("/")[-1]

        payload = {
            "checkpoint_type": rp,
            "filenames": [model_name],
            "params": {"message": "placeholder for chkpts upload test"}
        }

        url = api_gateway_url + "checkpoint"

        print("Post request for upload s3 presign url.")

        response = requests.post(url=url, json=payload, headers={'x-api-key': api_key})

        json_response = response.json()
        # print(f"Response json {json_response}")
        s3_base = json_response["checkpoint"]["s3_location"]
        checkpoint_id = json_response["checkpoint"]["id"]
        print(f"Upload to S3 {s3_base}")
        print(f"Checkpoint ID: {checkpoint_id}")

        s3_presigned_url = json_response["s3PresignUrl"][model_name]
        # Upload src model to S3.
        if rp != "embeddings" :
            local_model_path_in_repo = f'models/{rp}/{model_name}'
        else:
            local_model_path_in_repo = f'{rp}/{model_name}'
        local_tar_path = f'{model_name}.tar'
        print("Pack the model file.")
        os.system(f"cp -f {lp} {local_model_path_in_repo}")
        os.system(f"tar cvf {local_tar_path} {local_model_path_in_repo}")
        upload_file_to_s3_by_presign_url(local_tar_path, s3_presigned_url)

        payload = {
            "checkpoint_id": checkpoint_id,
            "status": "Active"
        }
        # Start creating model on cloud.
        response = requests.put(url=url, json=payload, headers={'x-api-key': api_key})
        s3_input_path = s3_base
        print(response)

        log = f"\n finish upload {local_tar_path} to {s3_base}"

        os.system(f"rm {local_tar_path}")
    
    print("Refresh checkpoints")
    for rp in checkpoint_type:
        url = api_gateway_url + f"checkpoints?status=Active&types={rp}"
        response = requests.get(url=url, headers={'x-api-key': api_key})
        json_response = response.json()
        print(f"response url json for model {rp} is {json_response}")
        for ckpt in json_response["checkpoints"]:
            ckpt_type = ckpt["type"]
            for ckpt_name in ckpt["name"]:
                ckpt_s3_pos = f"{ckpt['s3Location']}/{ckpt_name}"
                checkpoint_info[ckpt_type][ckpt_name] = ckpt_s3_pos
    
    print(f"current checkpoint information {checkpoint_info}")

# sd_checkpoints = ['checkpoint1', 'checkpoint2']
# txt2img_inference_job_ids = ['fake1', 'fake2']

# textual_inversion_list = ['textual_inversion1','textual_inversion2','textual_inversion3']
# lora_list = ['lora1', 'lora2', 'lora3']
# hyperNetwork_list = ['hyperNetwork1', 'hyperNetwork2', 'hyperNetwork3']
# ControlNet_model_list = ['controlNet_model1', 'controlNet_model2', 'controlNet_model3']

    return plaintext_to_html(log)

import json
import requests
from sagemaker.predictor import Predictor
from sagemaker.predictor_async import AsyncPredictor
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer
from sagemaker.async_inference.waiter_config import WaiterConfig
from sagemaker.async_inference.async_inference_response import AsyncInferenceResponse
import base64

def generate_on_cloud():
    # print(f"Current working directory: {os.getcwd()}")
    # load json files
    # stage 1: make payload
    # use txt2imgConfig.json instead of ui-config.json
    with open("ui-config.json") as f:
        params_dict = json.load(f)
    #print(f"Current parameters are {params_dict}")

    contronet_enable = params_dict['txt2img/Enable/value']
    if contronet_enable:
        controlnet_image_path = "/home/ubuntu/images_SD/shaoshuminzu/685a4b41a07c4cb42e88fcc75b95603a.jpeg"
        controlnet_module = params_dict['txt2img/Preprocessor/value']#'openpose'
        selected_cn_model = params_dict['customscript/main.py/txt2img/ControlNet-Model/value']#['control_openpose-fp16.safetensors']
        controlnet_model = os.path.splitext(selected_cn_model[0])[0]

        with open(controlnet_image_path, "rb") as img:
            image = base64.b64encode(img.read())
    
    selected_sd_model = params_dict['customscript/main.py/txt2img/Stable Diffusion Checkpoint/value']#['my_style_132.safetensors']
    selected_hypernets = params_dict['customscript/main.py/txt2img/HyperNetwork/value']#['mjv4Hypernetwork_v1.pt']
    selected_loras = params_dict['customscript/main.py/txt2img/LoRA/value'] #['cuteGirlMix4_v10.safetensors']
    selected_embeddings = params_dict['customscript/main.py/txt2img/Textual Inversion/value'] #['pureerosface_v1.pt']
    prompt = params_dict['txt2img/Prompt/value']
    for embedding in selected_embeddings:
        prompt = prompt + embedding
    for hypernet in selected_hypernets:
        hypernet_name = os.path.splitext(hypernet)[0]
        prompt = prompt + f"<hypernet:{hypernet_name}:1>"
    for lora in selected_loras:
        lora_name = os.path.splitext(lora)[0]
        prompt = prompt + f"<lora:{lora_name}:1>"


    # endpoint_name = "ask-webui-api-gpu-2023-04-10-05-53-21-649"
    endpoint_name = params_dict['customscript/main.py/txt2img/Select Cloud SageMaker Endpoint/value']#"infer-endpoint-d6bf"
    
    
    if contronet_enable:
       print('txt2img with controlnet!!!!!!!!!!')
       payload = {
        "endpoint_name": endpoint_name,
        "task": "controlnet_txt2img", 
        "username": "test",
        "models":{
            "bucket": "sagemaker-us-west-2-725399406069",
            "base_dir": "stable-diffusion-webui",
            "sd": selected_sd_model,
            "controlnet": selected_cn_model,
            "hypernetwork": selected_hypernets,
            "lora": selected_loras,
            "embedding": selected_embeddings
        },
        "controlnet_txt2img_payload":{ 
            "enable_hr": "False", 
            "denoising_strength": 0.7, 
            "firstphase_width": 0, 
            "firstphase_height": 0, 
            "prompt": prompt, 
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
            "width": 512, 
            "height": 512, 
            "restore_faces": "False", 
            "tiling": "False", 
            "negative_prompt": "", 
            "eta": 1, 
            "s_churn": 0, 
            "s_tmax": 1, 
            "s_tmin": 0, 
            "s_noise": 1, 
            "override_settings": {}, 
            "script_name": "",
            "script_args": [0, "False", "False", "False" "", 1, "", 0, "", "True", "True", "True"],
            "controlnet_units": [
                {
                "input_image": image.decode(),
                "mask": "",
                "module": controlnet_module,
                "model": controlnet_model,
                "weight": 1,
                "resize_mode": "Scale to Fit (Inner Fit)",
                "lowvram": "False",
                "processor_res": 64,
                "threshold_a": 64,
                "threshold_b": 64,
                "guidance": 1,
                "guidance_start": 0,
                "guidance_end": 1,
                "guessmode": "True"
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
        "models":{
            "bucket": "sagemaker-us-west-2-725399406069",
            "base_dir": "stable-diffusion-webui",
            "sd": selected_sd_model,
            "controlnet": [],
            "hypernetwork": selected_hypernets,
            "lora": selected_loras,
            "embedding": selected_embeddings
        },
        "txt2img_payload": {
            "enable_hr": "False", 
            "denoising_strength": 0.7, 
            "firstphase_width": 0, 
            "firstphase_height": 0, 
            "prompt": prompt, 
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
            "width": 512, 
            "height": 512, 
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

def fake_gan(selected_value: str ):
    print(f"selected value is {selected_value}")
    if selected_value is not None:
        selected_value_json = json.loads(selected_value)

        # Extract the InferenceJobId value
        inference_job_id = selected_value_json['InferenceJobId']
        images = get_inference_job_image_output(inference_job_id)
        image_list = []
        image_list = download_images(images,f"outputs/txt2img-images/{get_current_date()}/{inference_job_id}/")
        print(f"{str(images)}")
                        
    else:
        image_list = []  # Return an empty list if selected_value is None

    return image_list

def create_ui():
    global txt2img_gallery, txt2img_generation_info
    import modules.ui

    if get_variable_from_json('api_gateway_url') is not None:
        # update_sagemaker_endpoints()
        sagemaker_upload_model_s3("", "", "", "", "")
        get_texual_inversion_list()
        get_lora_list()
        get_hypernetwork_list()
        get_controlnet_model_list()
        get_inference_job_list()
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
                global txt2img_inference_job_ids
                inference_job_dropdown = gr.Dropdown(txt2img_inference_job_ids,
                                            label="Inference Job IDs"
                                            )
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
                model_update_button = gr.Button(value="Upload models to S3 and refresh list", variant="primary")
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
