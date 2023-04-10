import sagemaker
import time
import json
import threading
import gradio as gr
import modules.scripts as scripts
from modules import shared, devices, script_callbacks, processing, masking, images
from utils import download_folder_from_s3_by_tar, download_file_from_s3, upload_file_to_s3

import sys
import pickle
# TODO: Automaticly append the dependent module path.
sys.path.append("extensions/sd_dreambooth_extension")
sys.path.append("extensions/aws-ai-solution-kit")
# TODO: Do not use the dreambooth status module.
from dreambooth.shared import status
from dreambooth_sagemaker.train import start_sagemaker_training

db_model_name = None
db_use_txt2img = None
db_sagemaker_train = None
job_link_list = []

def on_after_component_callback(component, **_kwargs):
    global db_model_name, db_use_txt2img, db_sagemaker_train
    is_dreambooth_train = type(component) is gr.Button and getattr(component, 'elem_id', None) == 'db_train'
    is_dreambooth_model_name = type(component) is gr.Dropdown and \
            (getattr(component, 'elem_id', None) == 'model_name' or \
            (getattr(component, 'label', None) == 'Model' and getattr(component.parent.parent.parent.parent, 'elem_id', None) == 'ModelPanel'))
    is_dreambooth_use_txt2img = type(component) is gr.Checkbox and getattr(component, 'label', None) == 'Use txt2img'
    if is_dreambooth_train:
        print('Add SageMaker button')
        db_sagemaker_train = gr.Button(value="SageMaker Train", elem_id = "db_sagemaker_train", variant='primary')
    if is_dreambooth_model_name:
        print('Get model name')
        db_model_name = component
    if is_dreambooth_use_txt2img:
        print('Get use tet2img')
        db_use_txt2img = component
    # After all requiment comment is loaded, add the SageMaker training button click callback function.
    if db_model_name is not None and db_use_txt2img is not None and db_sagemaker_train is not None and \
            (is_dreambooth_train or is_dreambooth_model_name or is_dreambooth_use_txt2img):
        print('Create click callback')
        db_sagemaker_train.click(
            fn=start_sagemaker_training,
            _js="db_start_sagemaker_train",
            inputs=[
                db_model_name,
                db_use_txt2img,
            ],
            outputs=[]
        )

def on_ui_tabs():
    with gr.Blocks() as sagemaker_interface:
        with gr.Row():
            gr.HTML(value="Select a pipeline to using SageMaker.", elem_id="hint_row")
        with gr.Row().style(equal_height=False):
            with gr.Column(variant="panel", elem_id="PipelinePanel"):
                with gr.Tab("Select"):
                    with gr.Row():
                        db_model_name = gr.Dropdown(elem_id='pipeline', label='Pipeline', choices=["dreambooth_train"])
                        for job_link in job_link_list:
                            gr.HTML(value=f"<span class='hhh'>{job_link}</span>")
    return (sagemaker_interface, "SageMaker", "sagemaker_interface"),

script_callbacks.on_after_component(on_after_component_callback)
script_callbacks.on_ui_tabs(on_ui_tabs)