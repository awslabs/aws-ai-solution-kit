import copy
import itertools
import os
from pathlib import Path
import html
import boto3
import time

import json
import requests
import base64
from urllib.parse import urljoin

import gradio as gr

from modules import shared, scripts
from modules.ui import create_refresh_button
from modules.ui_components import FormRow, FormColumn, FormGroup, ToolButton, FormHTML
from utils import get_variable_from_json
from utils import upload_file_to_s3_by_presign_url, upload_multipart_files_to_s3_by_signed_url
from requests.exceptions import JSONDecodeError
from datetime import datetime
import math

inference_job_dropdown = None
sagemaker_endpoint = None

#TODO: convert to dynamically init the following variables
sagemaker_endpoints = []
txt2img_inference_job_ids = []

sd_checkpoints = []
textual_inversion_list = []
lora_list = []
hyperNetwork_list = []
ControlNet_model_list = []

# Initial checkpoints information
checkpoint_info = {}
checkpoint_type = ["Stable-diffusion", "embeddings", "Lora", "hypernetworks", "ControlNet"]
checkpoint_name = ["stable_diffusion", "embeddings", "lora", "hypernetworks", "controlnet"]
stable_diffusion_list = []
embeddings_list = []
lora_list = []
hypernetworks_list = []
controlnet_list = []
for ckpt_type, ckpt_name in zip(checkpoint_type, checkpoint_name):
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
    # print(f"response for rest api {response.json()}")
    return response

def datetime_to_short_form(datetime_str):
    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f")
    short_form = dt.strftime("%Y-%m-%d-%H-%M-%S")
    return short_form

def update_sagemaker_endpoints():
    global sagemaker_endpoints

    response = server_request('inference/list-endpoint-deployment-jobs')
    r = response.json()
    print(f"guming debug>>update_sagemaker_endpoints, {r}")
    if r:
        sagemaker_endpoints.clear()  # Clear the existing list before appending new values
        sagemaker_raw_endpoints = []
        for obj in r:
            # if "EndpointDeploymentJobId" in obj and obj.get('status') == 'success' and obj.get('endpoint_status') == "InService":
            if "EndpointDeploymentJobId" in obj :
                endpoint_name = obj["endpoint_name"]
                endpoint_status = obj["endpoint_status"]
                if "endTime" in obj: 
                    endpoint_time = obj["endTime"]
                else:
                    endpoint_time = "N/A"
                endpoint_info = f"{endpoint_name}+{endpoint_status}+{endpoint_time}"
                sagemaker_raw_endpoints.append(endpoint_info)
            # temp_list = []
            # for obj in r:
            #     complete_time = obj.get('completeTime')
            #     inference_job_id = obj.get('InferenceJobId')
            #     combined_string = f"{complete_time}-->{inference_job_id}"
            #     temp_list.append((complete_time, combined_string))

        # Sort the list based on completeTime in descending order
        sagemaker_endpoints= sorted(sagemaker_raw_endpoints, key=lambda x: x.split('+')[-1], reverse=True)

    else:
        print("The API response is empty for update_sagemaker_endpoints().")

def update_txt2img_inference_job_ids():
    global txt2img_inference_job_ids
    get_inference_job_list()

def origin_update_txt2img_inference_job_ids():
    global origin_txt2img_inference_job_ids

def get_inference_job_list():
    global txt2img_inference_job_ids
    try:
        response = server_request('inference/list-inference-jobs')
        r = response.json()
        if r:
            txt2img_inference_job_ids.clear()  # Clear the existing list before appending new values
            temp_list = []
            for obj in r:
                complete_time = obj.get('completeTime')
                inference_job_id = obj.get('InferenceJobId')
                combined_string = f"{complete_time}-->{inference_job_id}"
                temp_list.append((complete_time, combined_string))

            # Sort the list based on completeTime in descending order
            sorted_list = sorted(temp_list, key=lambda x: x[0], reverse=True)

            # Append the sorted combined strings to the txt2img_inference_job_ids list
            for item in sorted_list:
                txt2img_inference_job_ids.append(item[1])

        else:
            print("The API response is empty.")
    except Exception as e:
        print("Exception occurred when fetching inference_job_ids")



def get_inference_job(inference_job_id):
    response = server_request(f'inference/get-inference-job?jobID={inference_job_id}')
    return response.json()

def get_inference_job_image_output(inference_job_id):
    response = server_request(f'inference/get-inference-job-image-output?jobID={inference_job_id}')
    r = response.json()
    txt2img_inference_job_image_list = []
    for obj in r:
        obj_value = str(obj)
        txt2img_inference_job_image_list.append(obj_value)
    return txt2img_inference_job_image_list

def get_inference_job_param_output(inference_job_id):
    response = server_request(f'inference/get-inference-job-param-output?jobID={inference_job_id}')
    r = response.json()
    txt2img_inference_job_param_list = []
    for obj in r:
        obj_value = str(obj)
        txt2img_inference_job_param_list.append(obj_value)
    return txt2img_inference_job_param_list 

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

def get_model_list_by_type(model_type):
    if api_gateway_url is None:
        print(f"failed to get the api-gateway url, can not fetch remote data")
        return []
    url = api_gateway_url + f"checkpoints?status=Active&types={model_type}"
    response = requests.get(url=url, headers={'x-api-key': api_key})
    json_response = response.json()
    # print(f"response url json for model {model_type} is {json_response}")

    if "checkpoints" not in json_response.keys():
        return []

    checkpoint_list = []
    for ckpt in json_response["checkpoints"]:
        ckpt_type = ckpt["type"]
        for ckpt_name in ckpt["name"]:
            ckpt_s3_pos = f"{ckpt['s3Location']}/{ckpt_name}"
            checkpoint_info[ckpt_type][ckpt_name] = ckpt_s3_pos
            checkpoint_list.append(ckpt_name)

    return checkpoint_list

def update_sd_checkpoints():
    model_type = "Stable-diffusion"
    return get_model_list_by_type(model_type)
    
def get_texual_inversion_list():
    model_type = "embeddings"
    return get_model_list_by_type(model_type)

def get_lora_list():
    model_type = "Lora"
    return get_model_list_by_type(model_type)
    
def get_hypernetwork_list():
    model_type = "hypernetworks"
    return get_model_list_by_type(model_type)
    
def get_controlnet_model_list():
    model_type = "ControlNet"
    return get_model_list_by_type(model_type)

def refresh_all_models():
    print("Refresh checkpoints")
    api_gateway_url = get_variable_from_json('api_gateway_url')
    api_key = get_variable_from_json('api_token') 
    for rp, name in zip(checkpoint_type, checkpoint_name):
        url = api_gateway_url + f"checkpoints?status=Active&types={rp}"
        response = requests.get(url=url, headers={'x-api-key': api_key})
        json_response = response.json()
        # print(f"response url json for model {rp} is {json_response}")
        if "checkpoints" not in json_response.keys():
            checkpoint_info[rp] = {} 
            continue
        for ckpt in json_response["checkpoints"]:
            ckpt_type = ckpt["type"]
            checkpoint_info[ckpt_type] = {} 
            for ckpt_name in ckpt["name"]:
                ckpt_s3_pos = f"{ckpt['s3Location']}/{ckpt_name}"
                checkpoint_info[ckpt_type][ckpt_name] = ckpt_s3_pos

def sagemaker_upload_model_s3(sd_checkpoints_path, textual_inversion_path, lora_path, hypernetwork_path, controlnet_model_path):
    log = "start upload model to s3..."

    local_paths = [sd_checkpoints_path, textual_inversion_path, lora_path, hypernetwork_path, controlnet_model_path]

    print(f"Refresh checkpionts before upload to get rid of duplicate uploads...")
    refresh_all_models()

    for lp, rp in zip(local_paths, checkpoint_type):
        if lp == "":
            continue
        print(f"lp is {lp}")
        model_name = lp.split("/")[-1]

        exist_model_list = list(checkpoint_info[rp].keys())

        if model_name in exist_model_list:
            print(f"!!!skip to upload duplicate model {model_name}")
            continue

        part_size = 1000 * 1024 * 1024
        file_size = os.stat(lp)
        parts_number = math.ceil(file_size.st_size/part_size)
        print('!!!!!!!!!!', file_size, parts_number)

        #local_tar_path = f'{model_name}.tar'  
        local_tar_path = model_name      
        payload = {
            "checkpoint_type": rp,
            "filenames": [{
            "filename": local_tar_path,
            "parts_number": parts_number
            }],
            "params": {"message": "placeholder for chkpts upload test"}
        }
        print('!!!!!!api_gateway_url', api_gateway_url)
        url = api_gateway_url + "checkpoint"

        print(f"Post request for upload s3 presign url: {url}")

        response = requests.post(url=url, json=payload, headers={'x-api-key': api_key})

        try: 
            json_response = response.json()
            print(f"Response json {json_response}")
            s3_base = json_response["checkpoint"]["s3_location"]
            checkpoint_id = json_response["checkpoint"]["id"]
            print(f"Upload to S3 {s3_base}")
            print(f"Checkpoint ID: {checkpoint_id}")

            #s3_presigned_url = json_response["s3PresignUrl"][model_name]
            s3_signed_urls_resp = json_response["s3PresignUrl"][local_tar_path]
            # Upload src model to S3.
            if rp != "embeddings" :
                local_model_path_in_repo = f'models/{rp}/{model_name}'
            else:
                local_model_path_in_repo = f'{rp}/{model_name}'
            #local_tar_path = f'{model_name}.tar'
            print("Pack the model file.")
            os.system(f"cp -f {lp} {local_model_path_in_repo}")
            if rp == "Stable-diffusion":
                model_yaml_name = model_name.split('.')[0] + ".yaml"
                local_model_yaml_path = "/".join(lp.split("/")[:-1]) + f"/{model_yaml_name}"
                local_model_yaml_path_in_repo = f"models/{rp}/{model_yaml_name}"
                if os.path.isfile(local_model_yaml_path):
                    os.system(f"cp -f {local_model_yaml_path} {local_model_yaml_path_in_repo}")
                    os.system(f"tar cvf {local_tar_path} {local_model_path_in_repo} {local_model_yaml_path_in_repo}")
                else:
                    os.system(f"tar cvf {local_tar_path} {local_model_path_in_repo}")
            else:
                os.system(f"tar cvf {local_tar_path} {local_model_path_in_repo}")
            #upload_file_to_s3_by_presign_url(local_tar_path, s3_presigned_url)
            multiparts_tags = upload_multipart_files_to_s3_by_signed_url(
                local_tar_path,
                s3_signed_urls_resp,
                part_size
            )

            payload = {
                "checkpoint_id": checkpoint_id,
                "status": "Active",
                "multi_parts_tags": {local_tar_path: multiparts_tags}
            }
            # Start creating model on cloud.
            response = requests.put(url=url, json=payload, headers={'x-api-key': api_key})
            s3_input_path = s3_base
            print(response)

            log = f"\n finish upload {local_tar_path} to {s3_base}"

            os.system(f"rm {local_tar_path}")
        except Exception as e:
            print(f"fail to upload model {lp}, error: {e}")
    
    print(f"Refresh checkpionts after upload...")
    refresh_all_models()

    return plaintext_to_html(log)

def generate_on_cloud(sagemaker_endpoint):
    print(f"checkpiont_info {checkpoint_info}")
    print(f"sagemaker endpoint {sagemaker_endpoint}")
    text = "failed to check endpoint"
    return plaintext_to_html(text)

def generate_on_cloud_no_input(sagemaker_endpoint):
    print(f"chosen ep {sagemaker_endpoint}")

    if sagemaker_endpoint == '':
        image_list = []  # Return an empty list if selected_value is None
        info_text = ''
        infotexts = "Failed! Please choose the endpoint in 'InService' states "
        return image_list, info_text, plaintext_to_html(infotexts)

    sagemaker_endpoint_status = sagemaker_endpoint.split("+")[1]

    if sagemaker_endpoint_status != "InService":
        image_list = []  # Return an empty list if selected_value is None
        info_text = ''
        infotexts = "Failed! Please choose the endpoint in 'InService' states "
        return image_list, info_text, plaintext_to_html(infotexts)
    
    # stage 2: inference using endpoint_name
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    checkpoint_info['sagemaker_endpoint'] = sagemaker_endpoint.split("+")[0]
    payload = checkpoint_info
    print(f"checkpointinfo is {payload}")
    inference_url = f"{api_gateway_url}inference/run-sagemaker-inference"
    response = requests.post(inference_url, json=payload, headers=headers)
    try:
        r = response.json()
    except JSONDecodeError as e:
        print(f"Failed to decode JSON response: {e}")
        print(f"Raw server response: {response.text}")
    else:
        print(f"response for rest api {r}")
        inference_id = r.get('inference_id')  # Assuming the response contains 'inference_id' field

        # Loop until the get_inference_job status is 'succeed' or 'failed'
        while True:
            job_status = get_inference_job(inference_id)
            status = job_status['status']
            if status == 'succeed':
                break
            elif status == 'failed':
                print(f"Inference job failed: {job_status.get('error_message', 'No error message provided')}")
                break
            time.sleep(5)  # You can adjust the sleep time as needed

        # Call the fake_gan function using the inference_id only if the status is 'succeed'
        if status == 'succeed':
            return display_inference_result(inference_id)
            

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

def modelmerger_on_cloud_func(primary_model_name, secondary_model_name, tertiary_model_name):
    print(f"function not implemented, current checkpoint_info is {checkpoint_info}")

def txt2img_config_save():
    # placeholder for saving txt2img config
    pass

def fake_gan(selected_value: str ):
    print(f"selected value is {selected_value}")
    if selected_value is not None:
        delimiter = "-->"
        parts = selected_value.split(delimiter)
        # Extract the InferenceJobId value
        inference_job_id = parts[1].strip()
        images = get_inference_job_image_output(inference_job_id)
        image_list = []
        image_list = download_images(images,f"outputs/txt2img-images/{get_current_date()}/{inference_job_id}/")

        inference_pram_json_list = get_inference_job_param_output(inference_job_id)
        json_list = []
        json_list = download_images(inference_pram_json_list, f"outputs/txt2img-images/{get_current_date()}/{inference_job_id}/")

        print(f"{str(images)}")
        print(f"{str(inference_pram_json_list)}")

        json_file = f"outputs/txt2img-images/{get_current_date()}/{inference_job_id}/{inference_job_id}_param.json"

        f = open(json_file)

        log_file = json.load(f)

        info_text = log_file["info"]

        infotexts = json.loads(info_text)["infotexts"][0]
    else:
        image_list = []  # Return an empty list if selected_value is None
        json_list = []
        info_text = ''

    return image_list, info_text, plaintext_to_html(infotexts)
    
def display_inference_result(inference_id: str ):
    print(f"selected value is {inference_id}")
    if inference_id is not None:
        # Extract the InferenceJobId value
        inference_job_id = inference_id
        images = get_inference_job_image_output(inference_job_id)
        image_list = []
        image_list = download_images(images,f"outputs/txt2img-images/{get_current_date()}/{inference_job_id}/")

        inference_pram_json_list = get_inference_job_param_output(inference_job_id)
        json_list = []
        json_list = download_images(inference_pram_json_list, f"outputs/txt2img-images/{get_current_date()}/{inference_job_id}/")

        print(f"{str(images)}")
        print(f"{str(inference_pram_json_list)}")

        json_file = f"outputs/txt2img-images/{get_current_date()}/{inference_job_id}/{inference_job_id}_param.json"

        f = open(json_file)

        log_file = json.load(f)

        info_text = log_file["info"]

        infotexts = json.loads(info_text)["infotexts"][0]
    else:
        image_list = []  # Return an empty list if selected_value is None
        json_list = []
        info_text = ''

    return image_list, info_text, plaintext_to_html(infotexts)

def create_ui():
    global txt2img_gallery, txt2img_generation_info
    import modules.ui

    if get_variable_from_json('api_gateway_url') is not None:
        update_sagemaker_endpoints()
        refresh_all_models()
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
                    global sagemaker_endpoint
                    sagemaker_endpoint = gr.Dropdown(sagemaker_endpoints,
                                             label="Select Cloud SageMaker Endpoint",
                                             elem_id="sagemaker_endpoint_dropdown"
                                             )
                    modules.ui.create_refresh_button(sagemaker_endpoint, update_sagemaker_endpoints, lambda: {"choices": sagemaker_endpoints}, "refresh_sagemaker_endpoints")
                with gr.Row():
                    sd_checkpoint = gr.Dropdown(multiselect=True, label="Stable Diffusion Checkpoint", choices=sorted(update_sd_checkpoints()), elem_id="stable_diffusion_checkpoint_dropdown")
                    sd_checkpoint_refresh_button = modules.ui.create_refresh_button(sd_checkpoint, update_sd_checkpoints, lambda: {"choices": sorted(update_sd_checkpoints())}, "refresh_sd_checkpoints")
            with gr.Column():
                # generate_on_cloud_button = gr.Button(value="Button for debug controlnet", variant='primary', elem_id="generate_on_cloud_local_config_button")
                # generate_on_sagemaker_endpointcloud_button.click(
                #     fn=generate_on_cloud,
                #     inputs=[],
                #     outputs=[sagemaker_html_log]
                # )
                global generate_on_cloud_button_with_js
                generate_on_cloud_button_with_js = gr.Button(value="Generate on Cloud", variant='primary', elem_id="generate_on_cloud_with_cloud_config_button")
                # generate_on_cloud_button_with_js.click(
                #     # _js="txt2img_config_save",
                #     fn=generate_on_cloud_no_input,
                #     inputs=[sagemaker_endpoint],
                #     outputs=[]
                # )
                txt2img_config_save_button = gr.Button(value="Save Settings", variant='primary', elem_id="save_webui_component_to_cloud_button")
                txt2img_config_save_button.click(
                    _js="txt2img_config_save",
                    fn=None,
                    inputs=[],
                    outputs=[]
                )
            with gr.Row():
                global inference_job_dropdown 
                global txt2img_inference_job_ids
                inference_job_dropdown = gr.Dropdown(txt2img_inference_job_ids,
                                            label="Inference Job IDs",
                                            elem_id="txt2img_inference_job_ids_dropdown"
                                            )
                txt2img_inference_job_ids_refresh_button = modules.ui.create_refresh_button(inference_job_dropdown, update_txt2img_inference_job_ids, lambda: {"choices": txt2img_inference_job_ids}, "refresh_txt2img_inference_job_ids")
 
            with gr.Row():
                gr.HTML(value="Extra Networks for Sagemaker Endpoint")
            #     advanced_model_refresh_button = modules.ui.create_refresh_button(sd_checkpoint, update_sd_checkpoints, lambda: {"choices": sorted(sd_checkpoints)}, "refresh_sd_checkpoints")
            
            with gr.Row():
                textual_inversion_dropdown = gr.Dropdown(multiselect=True, label="Textual Inversion", choices=sorted(get_texual_inversion_list()),elem_id="sagemaker_texual_inversion_dropdown")
                create_refresh_button(
                    textual_inversion_dropdown,
                    get_texual_inversion_list,
                    lambda: {"choices": sorted(get_texual_inversion_list())},
                    "refresh_textual_inversion",
                )
                lora_dropdown = gr.Dropdown(lora_list,  multiselect=True, label="LoRA", elem_id="sagemaker_lora_list_dropdown")
                create_refresh_button(
                    lora_dropdown,
                    get_lora_list,
                    lambda: {"choices": sorted(get_lora_list())},
                    "refresh_lora",
                )
            with gr.Row():
                hyperNetwork_dropdown = gr.Dropdown(multiselect=True, label="HyperNetwork", choices=sorted(get_hypernetwork_list()), elem_id="sagemaker_hypernetwork_dropdown")
                create_refresh_button(
                    hyperNetwork_dropdown,
                    get_hypernetwork_list,
                    lambda: {"choices": sorted(get_hypernetwork_list())},
                    "refresh_hypernetworks",
                )
                controlnet_dropdown = gr.Dropdown(multiselect=True, label="ControlNet-Model", choices=sorted(get_controlnet_model_list()), elem_id="sagemaker_controlnet_model_dropdown")
                create_refresh_button(
                    controlnet_dropdown,
                    get_controlnet_model_list,
                    lambda: {"choices": sorted(get_controlnet_model_list())},
                    "refresh_controlnet",
                )

            with gr.Row():
                sd_checkpoints_path = gr.Textbox(value="", lines=1, placeholder="Please input absolute path", label="Stable Diffusion Checkpoints",elem_id="sd_checkpoints_path_textbox")
                textual_inversion_path = gr.Textbox(value="", lines=1, placeholder="Please input absolute path", label="Textual Inversion",elem_id="sd_textual_inversion_path_textbox")
                lora_path = gr.Textbox(value="", lines=1, placeholder="Please input absolute path", label="LoRA",elem_id="sd_lora_path_textbox")
                hypernetwork_path = gr.Textbox(value="", lines=1, placeholder="Please input absolute path", label="HyperNetwork",elem_id="sd_hypernetwork_path_textbox")
                controlnet_model_path = gr.Textbox(value="", lines=1, placeholder="Please input absolute path", label="ControlNet-Model",elem_id="sd_controlnet_model_path_textbox")
            
            with gr.Row():
                model_update_button = gr.Button(value="Upload models to S3", variant="primary",elem_id="sagemaker_model_update_button", size=(200, 50))
                model_update_button.click(_js="model_update",
                                        fn=sagemaker_upload_model_s3,
                                        inputs=[sd_checkpoints_path, textual_inversion_path, lora_path, hypernetwork_path, controlnet_model_path],
                                        outputs=[sagemaker_html_log])

            gr.HTML(value="Deploy New SageMaker Endpoint")
            with gr.Row():
                # instance_type_textbox = gr.Textbox(value="", lines=1, placeholder="Please enter Instance type, e.g. ml.g4dn.xlarge", label="SageMaker Instance Type",elem_id="sagemaker_inference_instance_type_textbox")
                instance_type_dropdown = gr.Dropdown(label="SageMaker Instance Type", choices=["ml.g4dn.xlarge","ml.g4dn.2xlarge","ml.g4dn.4xlarge","ml.g4dn.8xlarge","ml.g4dn.12xlarge"], elem_id="sagemaker_inference_instance_type_textbox", value="ml.g4dn.xlarge")
                # instance_count_textbox = gr.Textbox(value="", lines=1, placeholder="Please enter Instance count, e.g. 1,2", label="SageMaker Instance Count",elem_id="sagemaker_inference_instance_count_textbox", default=1)
                instance_count_dropdown = gr.Dropdown(label="Please select Instance count", choices=["1","2","3","4"], elem_id="sagemaker_inference_instance_count_textbox", value="1")

            with gr.Row():
                sagemaker_deploy_button = gr.Button(value="Deploy", variant='primary',elem_id="sagemaker_deploy_endpoint_buttion")
                sagemaker_deploy_button.click(sagemaker_deploy,
                                            _js="deploy_endpoint", \
                                            inputs = [instance_type_dropdown, instance_count_dropdown])

    with gr.Group():
        with gr.Accordion("Open for Checkpoint Merge in the Cloud!", open=False):
            sagemaker_html_log = gr.HTML(elem_id=f'html_log_sagemaker')
            with FormRow(elem_id="modelmerger_models_in_the_cloud"):
                primary_model_name = gr.Dropdown(choices=sorted(update_sd_checkpoints()), elem_id="modelmerger_primary_model_name_in_the_cloud", label="Primary model (A) in the cloud")
                create_refresh_button(primary_model_name, update_sd_checkpoints, lambda: {"choices": sorted(update_sd_checkpoints())}, "refresh_checkpoint_A_in_the_cloud")

                secondary_model_name = gr.Dropdown(choices=sorted(update_sd_checkpoints()), elem_id="modelmerger_secondary_model_name_in_the_cloud", label="Secondary model (B) in the cloud")
                create_refresh_button(secondary_model_name, update_sd_checkpoints, lambda: {"choices": sorted(update_sd_checkpoints())}, "refresh_checkpoint_B_in_the_cloud")

                tertiary_model_name = gr.Dropdown(choices=sorted(update_sd_checkpoints()), elem_id="modelmerger_tertiary_model_name_in_the_cloud", label="Tertiary model (C) in the cloud")
                create_refresh_button(tertiary_model_name, update_sd_checkpoints, lambda: {"choices": sorted(update_sd_checkpoints())}, "refresh_checkpoint_C_in_the_cloud")
            # with gr.Row():
            #     merge_job_dropdown = gr.Dropdown(merge_job_ids,
            #                                 label="Merge Job IDs",
            #                                 elem_id="merge_job_ids_dropdown"
            #                                 )
            #     txt2img_merge_job_ids_refresh_button = modules.ui.create_refresh_button(merge_job_dropdown, update_txt2img_merge_job_ids, lambda: {"choices": txt2img_merge_job_ids}, "refresh_txt2img_merge_job_ids")
            with gr.Row():
                modelmerger_merge_on_cloud = gr.Button(elem_id="modelmerger_merge_in_the_cloud", value="Merge", variant='primary')
                modelmerger_merge_on_cloud.click(
                    fn=modelmerger_on_cloud_func,
                    inputs=[
                        primary_model_name,
                        secondary_model_name,
                        tertiary_model_name,
                    ],
                    outputs=[
                    ])

    return  sagemaker_endpoint, sd_checkpoint, sd_checkpoint_refresh_button, textual_inversion_dropdown, lora_dropdown, hyperNetwork_dropdown, controlnet_dropdown, instance_type_dropdown, instance_count_dropdown, sagemaker_deploy_button, inference_job_dropdown, txt2img_inference_job_ids_refresh_button, primary_model_name, secondary_model_name, tertiary_model_name, modelmerger_merge_on_cloud
