import copy
import itertools
import os
from pathlib import Path
import html
import boto3

import gradio as gr

from modules import shared, scripts

global txt2img_inference_flash

#TODO: convert to dynamically init the following variables
sagemaker_endpoints = ['endpoint1', 'endpoint2']
sd_checkpoints = ['checkpoint1', 'checkpoint2']
txt2img_inference_job_ids = ['fake1', 'fake2']

textual_inversion_list = ['textual_inversion1','textual_inversion2','textual_inversion3']
lora_list = ['lora1', 'lora2', 'lora3']
hyperNetwork_list = ['hyperNetwork1', 'hyperNetwork2', 'hyperNetwork3']
ControlNet_model_list = ['controlNet_model1', 'controlNet_model2', 'controlNet_model3']

def get_s3_file_names(bucket, folder):
    """Get a list of file names from an S3 bucket and folder."""
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket)
    objects = bucket.objects.filter(Prefix=folder)
    names = [obj.key for obj in objects]
    return names


def update_sagemaker_endpoints():
    global sagemaker_endpoints
    # aesthetic_embeddings = {f.replace(".pt", ""): os.path.join(aesthetic_embeddings_dir, f) for f in os.listdir(aesthetic_embeddings_dir) if f.endswith(".pt")}
    # aesthetic_embeddings = OrderedDict(**{"None": None}, **aesthetic_embeddings)
    # TODO update the endpoint code here

def update_sd_checkpoints():
    global sd_checkpoints
    # aesthetic_embeddings = {f.replace(".pt", ""): os.path.join(aesthetic_embeddings_dir, f) for f in os.listdir(aesthetic_embeddings_dir) if f.endswith(".pt")}
    # aesthetic_embeddings = OrderedDict(**{"None": None}, **aesthetic_embeddings)
    # TODO update the checkpoint code here


def sagemaker_deploy(instance_type):
    # function code to call sagemaker deploy api
    print(f"start deploying instance type: {instance_type}............")

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
    with open("ui-config.json") as f:
        params_dict = json.load(f)
    print(f"Current parameters are {params_dict}")
    # construct payload
    payload = {
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
    endpoint_name = "ask-webui-api-gpu-2023-04-10-05-53-21-649"

    predictor = Predictor(endpoint_name)

    predictor = AsyncPredictor(predictor, name=endpoint_name)
    predictor.serializer = JSONSerializer()
    predictor.deserializer = JSONDeserializer()
    prediction = predictor.predict_async(data=payload)
    output_path = prediction.output_path

    # stage 3: notified by sns and get result, upload to s3 position
    new_predictor = Predictor(endpoint_name)

    new_predictor = AsyncPredictor(new_predictor, name=endpoint_name)
    new_predictor.serializer = JSONSerializer()
    new_predictor.deserializer = JSONDeserializer()
    new_prediction = AsyncInferenceResponse(new_predictor, output_path)
    config = WaiterConfig(
    max_attempts=100, #  number of attempts
    delay=10 #  time in seconds to wait between attempts
    )
    new_prediction.get_result(config)

    s3_resource = boto3.resource('s3')
    def get_bucket_and_key(s3uri):
        pos = s3uri.find('/', 5)
        bucket = s3uri[5 : pos]
        key = s3uri[pos + 1 : ]
        return bucket, key




def create_ui():
    import modules.ui

    with gr.Group():
        with gr.Accordion("Open for SageMaker Inference!", open=False):
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
                generate_on_cloud_button = gr.Button(value="Generate on Cloud", variant='primary')
                generate_on_cloud_button.click(generate_on_cloud)

            with gr.Row():
                txt2img_inference_job_id = gr.Dropdown(txt2img_inference_job_ids,
                                            label="Inference Job IDs")
                sd_checkpoint_refresh_button = modules.ui.create_refresh_button(txt2img_inference_job_id, update_txt2img_inference_job_ids, lambda: {"choices": txt2img_inference_job_ids}, "refresh_txt2img_inference_job_ids")

            with gr.Row():
                gr.HTML(value="Extra Networks")
                advanced_model_refresh_button = modules.ui.create_refresh_button(sd_checkpoint, update_sd_checkpoints, lambda: {"choices": sorted(sd_checkpoints)}, "refresh_sd_checkpoints")
            
            with gr.Row():
                textual_inversion_dropdown = gr.Dropdown(textual_inversion_list, multiselect=True, label="Textual Inversion")
                lora_dropdown = gr.Dropdown(lora_list,  multiselect=True, label="LoRA")
            with gr.Row():
                hyperNetwork_dropdown = gr.Dropdown(hyperNetwork_list, multiselect=True, label="HyperNetwork")
                controlnet_dropdown = gr.Dropdown(ControlNet_model_list, multiselect=True, label="ControlNet-Model")
            
            gr.HTML(value="Deploy New SageMaker Endpoint")
            with gr.Row():
                instance_type_textbox = gr.Textbox(value="", lines=1, placeholder="Please enter Instance type", label="SageMaker Instance Type")
                sagemaker_deploy_button = gr.Button(value="Deploy", variant='primary')
                sagemaker_deploy_button.click(sagemaker_deploy, inputs = [instance_type_textbox])

    return  sagemaker_endpoint, sd_checkpoint, sd_checkpoint_refresh_button, generate_on_cloud_button, advanced_model_refresh_button, textual_inversion_dropdown, lora_dropdown, hyperNetwork_dropdown, controlnet_dropdown, instance_type_textbox, sagemaker_deploy_button 