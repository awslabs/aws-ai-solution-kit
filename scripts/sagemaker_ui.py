import copy
import itertools
import os
from pathlib import Path
import html
import boto3

import gradio as gr

from modules import shared, scripts

#TODO: convert to dynamically init the following variables
sagemaker_endpoints = ['endpoint1', 'endpoint2']
sd_checkpoints = ['checkpoint1', 'checkpoint2']

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

def generate_on_cloud():
    print(f"Current working directory: {os.getcwd()}")

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