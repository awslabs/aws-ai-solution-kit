import sagemaker
import time
import json
import threading
import requests
import copy
import os
import gradio as gr
import modules.scripts as scripts
from modules import shared, devices, script_callbacks, processing, masking, images
from modules.ui import create_refresh_button
from utils import upload_file_to_s3_by_presign_url
from utils import get_variable_from_json
from utils import save_variable_to_json

import sys
import pickle
import html

# TODO: Automaticly append the dependent module path.
sys.path.append("extensions/sd_dreambooth_extension")
sys.path.append("extensions/aws-ai-solution-kit")
sys.path.append("extensions/aws-ai-solution-kit/scripts")
# TODO: Do not use the dreambooth status module.
from dreambooth.shared import status
from dreambooth_sagemaker.train import start_sagemaker_training
import sagemaker_ui

db_model_name = None
db_use_txt2img = None
db_sagemaker_train = None
txt2img_show_hook = None
txt2img_gallery = None
txt2img_generation_info = None
job_link_list = []

class SageMakerUI(scripts.Script):
    def title(self):
        return "SageMaker embeddings"

    def show(self, is_txt2img):
        return scripts.AlwaysVisible

    def ui(self, is_txt2img):
        sagemaker_endpoint, sd_checkpoint, sd_checkpoint_refresh_button, generate_on_cloud_button, advanced_model_refresh_button, textual_inversion_dropdown, lora_dropdown, hyperNetwork_dropdown, controlnet_dropdown, instance_type_textbox, sagemaker_deploy_button, choose_txt2img_inference_job_id, txt2img_inference_job_ids_refresh_button, origin_choose_txt2img_inference_job_id, origin_txt2img_inference_job_ids_refresh_button= sagemaker_ui.create_ui()

        return [sagemaker_endpoint, sd_checkpoint, sd_checkpoint_refresh_button, generate_on_cloud_button, advanced_model_refresh_button, textual_inversion_dropdown, lora_dropdown, hyperNetwork_dropdown, controlnet_dropdown, instance_type_textbox, sagemaker_deploy_button, choose_txt2img_inference_job_id, txt2img_inference_job_ids_refresh_button, origin_choose_txt2img_inference_job_id, origin_txt2img_inference_job_ids_refresh_button]

    def process(self, p, sagemaker_endpoint, sd_checkpoint, sd_checkpoint_refresh_button, generate_on_cloud_button, advanced_model_refresh_button, textual_inversion_dropdown, lora_dropdown, hyperNetwork_dropdown, controlnet_dropdown, instance_type_textbox, sagemaker_deploy_button, choose_txt2img_inference_job_id, txt2img_inference_job_ids_refresh_button, origin_choose_txt2img_inference_job_id, origin_txt2img_inference_job_ids_refresh_button):
        pass
        dropdown.init_field = init_field

        dropdown.change(
            fn=select_script,
            inputs=[dropdown],
            outputs=[script.group for script in self.selectable_scripts]
        )

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
    # Hook image display logic
    # result_gallery = gr.Gallery(label='Output', show_label=False, elem_id=f"{tabname}_gallery").style(grid=4)
    # ration_info = gr.Textbox(visible=False, elem_id=f'generation_info_{tabname}')
    #                 if tabname == 'txt2img' or tabname == 'img2img':
    global txt2img_gallery, txt2img_generation_info, txt2img_show_hook 
    is_txt2img_gallery = type(component) is gr.Gallery and getattr(component, 'elem_id', None) == 'txt2img_gallery'
    is_txt2img_generation_info = type(component) is gr.HTML and getattr(component, 'elem_id', None) == 'html_info_txt2img'
    # print(f"is_txt2img_gallery is {is_txt2img_gallery}")
    # print(f"is_txt2img_generation_info is {is_txt2img_generation_info}")
    if is_txt2img_gallery:
        print("create txt2img gallery")
        txt2img_gallery = component
    if is_txt2img_generation_info:
        print("create txt2img generation info")
        txt2img_generation_info = component
    def test_func():
        from PIL import Image
        gallery = ["/home/ubuntu/py_gpu_ubuntu_ue2_workplace/csdc/aigc/aigc-webui/dataset/raw-data/superman-fly.jpg"]
        images = []
        for g in gallery:
            im = Image.open(g)
            images.append(im)

        def plaintext_to_html(text):
            text = "<p>" + "<br>\n".join([f"{html.escape(x)}" for x in text.split('\n')]) + "</p>"
            return text

        test = "just a test"
        return images, plaintext_to_html(test)
        # return test
    if sagemaker_ui.origin_inference_job_dropdown is not None and txt2img_gallery is not None and txt2img_generation_info is not None and txt2img_show_hook is None:
        print("Create inference job dropdown callback")
        txt2img_show_hook = "finish"
        sagemaker_ui.origin_inference_job_dropdown.change(
            fn=test_func,
            outputs=[txt2img_gallery, txt2img_generation_info]
        )
    # global txt2img_interface, generate_hook
    # is_txt2img_prompt_image = type(component) is gr.File and getattr(component, 'elem_id', None) == 'txt2img_prompt_image'

    # if is_txt2img_prompt_image:
    #     txt2img_interface = component.parent
    
    # if txt2img_interface is not None and sagemaker_ui.generate_on_cloud_button is not None and generate_hook is None:
    #     generate_hook = "finish"
    #     sagemaker_ui.generate_on_cloud_button.click(
    #         fn=generate_test,
    #         inputs=[component]
    #     )
    #     print(f"!!!!!!!!parent component is {type(txt2img_interface)}")


def update_connect_config(api_url, api_token):
    # function code to call update the api_url and token
    # Example usage
    save_variable_to_json('api_gateway_url', api_url)
    save_variable_to_json('api_token', api_token)
    value1 = get_variable_from_json('api_gateway_url')
    value2 = get_variable_from_json('api_token')
    print(f"Variable 1: {value1}")
    print(f"Variable 2: {value2}")
    print(f"update the api_url:{api_url} and token: {api_token}............")
    
def on_ui_tabs():
    buildin_model_list = ['Buildin model 1','Buildin model 2','Buildin model 3']
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
        with  gr.Row():
            with gr.Column(variant="panel", scale=1):
                gr.HTML(value="AWS Connect Setting")
                api_url_textbox = gr.Textbox(value=get_variable_from_json('api_gateway_url'), lines=1, placeholder="Please enter API Url", label="API Url")
                api_token_textbox = gr.Textbox(value=get_variable_from_json('api_token'), lines=1, placeholder="Please enter API Token", label="API Token")
                aws_connect_button = gr.Button(value="Update Setting", variant='primary')
                aws_connect_button.click(update_connect_config, inputs = [api_url_textbox, api_token_textbox])
            with gr.Column(variant="panel", scale=2):
                gr.HTML(value="Resource")
                gr.Dataframe(
                    headers=["Extension", "Column header", "Column Header"],
                    datatype=["str", "str", "str"],
                    row_count=5,
                    col_count=(3, "fixed"),
                    value=[['Dreambooth','Cell Value','Cell Value'],
                           ['LoRA','Cell Value','Cell Value'],
                           ['ControlNet','Cell Value','Cell Value']])
            with gr.Column(variant="panel", scale=1):
                gr.HTML(value="Model")
                model_select_dropdown = gr.Dropdown(buildin_model_list, label="Select Built-In")

    return (sagemaker_interface, "SageMaker", "sagemaker_interface"),


script_callbacks.on_after_component(on_after_component_callback)
script_callbacks.on_ui_tabs(on_ui_tabs)
# create new tabs for create Model
origin_callback = script_callbacks.ui_tabs_callback


def ui_tabs_callback():
    res = origin_callback()
    for extension_ui in res:
        if extension_ui[1] == 'Dreambooth':
            for key in list(extension_ui[0].blocks):
                val = extension_ui[0].blocks[key]
                if type(val) is gr.Tab:
                    if val.label == 'Create':
                        with extension_ui[0]:
                            with val.parent:
                                with gr.Tab('Create From Cloud'):
                                    with gr.Column():
                                        cloud_db_create_model = gr.Button(
                                            value="Create Model From Cloud", variant="primary"
                                        )
                                    cloud_db_new_model_name = gr.Textbox(label="Name")
                                    with gr.Row():
                                        cloud_db_create_from_hub = gr.Checkbox(
                                            label="Create From Hub", value=False
                                        )
                                        cloud_db_512_model = gr.Checkbox(label="512x Model", value=True)
                                    with gr.Column(visible=False) as hub_row:
                                        cloud_db_new_model_url = gr.Textbox(
                                            label="Model Path",
                                            placeholder="runwayml/stable-diffusion-v1-5",
                                        )
                                        cloud_db_new_model_token = gr.Textbox(
                                            label="HuggingFace Token", value=""
                                        )
                                    with gr.Column(visible=True) as local_row:
                                        with gr.Row():
                                            cloud_db_new_model_src = gr.Dropdown(
                                                label="Source Checkpoint",
                                                choices=sorted(get_sd_cloud_models()),
                                            )
                                            create_refresh_button(
                                                cloud_db_new_model_src,
                                                get_sd_cloud_models,
                                                lambda: {"choices": sorted(get_sd_cloud_models())},
                                                "refresh_sd_models",
                                            )
                                    cloud_db_new_model_extract_ema = gr.Checkbox(
                                        label="Extract EMA Weights", value=False
                                    )
                                    cloud_db_train_unfrozen = gr.Checkbox(label="Unfreeze Model", value=False)
                                with gr.Tab('Select From Cloud'):
                                    with gr.Row():
                                        cloud_db_model_name = gr.Dropdown(
                                            label="Model", choices=sorted(get_cloud_db_models())
                                        )
                                        create_refresh_button(
                                            cloud_db_model_name,
                                            get_cloud_db_models,
                                            lambda: {"choices": sorted(get_cloud_db_models())},
                                            "refresh_db_models",
                                        )
                                    with gr.Row():
                                        cloud_db_snapshot = gr.Dropdown(
                                            label="Cloud Snapshot to Resume",
                                            choices=sorted(get_cloud_model_snapshots()),
                                        )
                                        create_refresh_button(
                                            cloud_db_snapshot,
                                            get_cloud_model_snapshots,
                                            lambda: {"choices": sorted(get_cloud_model_snapshots())},
                                            "refresh_db_snapshots",
                                        )
                                    with gr.Row(visible=False) as lora_model_row:
                                        cloud_db_lora_model_name = gr.Dropdown(
                                            label="Lora Model", choices=get_sorted_lora_cloud_models()
                                        )
                                        create_refresh_button(
                                            cloud_db_lora_model_name,
                                            get_sorted_lora_cloud_models,
                                            lambda: {"choices": get_sorted_lora_cloud_models()},
                                            "refresh_lora_models",
                                        )
                                    with gr.Row():
                                        gr.HTML(value="Loaded Model from Cloud:")
                                        cloud_db_model_path = gr.HTML()
                                    with gr.Row():
                                        gr.HTML(value="Cloud Model Revision:")
                                        cloud_db_revision = gr.HTML(elem_id="cloud_db_revision")
                                    with gr.Row():
                                        gr.HTML(value="Cloud Model Epoch:")
                                        cloud_db_epochs = gr.HTML(elem_id="cloud_db_epochs")
                                    with gr.Row():
                                        gr.HTML(value="V2 Model From Cloud:")
                                        cloud_db_v2 = gr.HTML(elem_id="cloud_db_v2")
                                    with gr.Row():
                                        gr.HTML(value="Has EMA:")
                                        cloud_db_has_ema = gr.HTML(elem_id="cloud_db_has_ema")
                                    with gr.Row():
                                        gr.HTML(value="Source Checkpoint From Cloud:")
                                        cloud_db_src = gr.HTML()


                            cloud_db_create_model.click(
                                fn=cloud_create_model,
                                # _js=
                                inputs=[
                                    cloud_db_new_model_name,
                                    cloud_db_new_model_src,
                                    cloud_db_create_from_hub,
                                    cloud_db_new_model_url,
                                    cloud_db_new_model_token,
                                    cloud_db_new_model_extract_ema,
                                    cloud_db_train_unfrozen,
                                    cloud_db_512_model,
                                ],
                                outputs=[
                                    cloud_db_model_name,
                                    cloud_db_model_path,
                                    cloud_db_revision,
                                    cloud_db_epochs,
                                    cloud_db_src,
                                    cloud_db_has_ema,
                                    cloud_db_v2,
                                    # cloud_db_resolution,
                                    # cloud_db_status,
                                ]
                            )

                        break

    return res

script_callbacks.ui_tabs_callback = ui_tabs_callback

def get_sorted_lora_cloud_models():
    return []

def get_cloud_model_snapshots():
    return []

def get_cloud_db_models():
    return []

def get_sd_cloud_models():
    return []

def cloud_create_model(
        new_model_name: str,
        ckpt_path: str,
        from_hub=False,
        new_model_url="",
        new_model_token="",
        extract_ema=False,
        train_unfrozen=False,
        is_512=True,
):
    # Prepare for creating model on cloud.
    params = copy.deepcopy(locals())
    local_model_path = f'models/Stable-diffusion/{ckpt_path}'
    local_tar_path = f'{ckpt_path}.tar'
    print("Pack the model file.")
    os.system(f"tar cvf {local_tar_path} {local_model_path}")
    payload = {
        "model_type": "dreambooth",
        "name": "test_upload",
        "filenames": [local_tar_path],
        "params": params
    }
    url = "https://oudm9u1088.execute-api.us-east-1.amazonaws.com/prod/model"
    print("Post request for upload s3 presign url.")
    response = requests.post(url=url, json=payload,
                         headers={'x-api-key': '09876543210987654321'})
    json_response = response.json()
    s3_base = json_response["job"]["s3_base"]
    model_id = json_response["job"]["id"]
    print(f"Upload to S3 {s3_base}")
    print(f"Model ID: {model_id}")
    # Upload src model to S3.
    for local_tar_path, s3_presigned_url in response.json()["s3PresignUrl"].items():
        upload_file_to_s3_by_presign_url(local_tar_path, s3_presigned_url)
    payload = {
        "model_id": model_id,
        "status": "Train"
    }
    # Start creating model on cloud.
    response = requests.put(url=url, json=payload,
                         headers={'x-api-key': '09876543210987654321'})
    s3_input_path = s3_base
    print(response)