import base64
import functools
import hashlib
import io
import json
import logging
import os
import shutil
import traceback
import zipfile
import time
from pathlib import Path
from typing import List, Union

import requests
from PIL import Image
from fastapi import FastAPI, Response, Query, Body, Form, Header
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from pydantic import BaseModel, Field
from starlette import status
from starlette.requests import Request

from modules.api.api import Api
from modules import sd_hijack, sd_models, sd_vae, script_loading, paths
import modules.scripts as base_scripts
from modules.hypernetworks import hypernetwork
from modules.textual_inversion import textual_inversion
import modules.shared as shared
import modules.extras
import sys
sys.path.append("extensions/aws-ai-solution-kit")
from scripts.models import *
import requests
from utils import get_bucket_name_from_s3_path, get_path_from_s3_path
from utils import download_file_from_s3, download_folder_from_s3, download_folder_from_s3_by_tar, upload_folder_to_s3, upload_file_to_s3, upload_folder_to_s3_by_tar
from utils import ModelsRef
import uuid
import boto3

sys.path.append("extensions/sd_dreambooth_extension")
from dreambooth.ui_functions import create_model

# try:
#     from dreambooth import shared
#     from dreambooth.dataclasses.db_concept import Concept
#     from dreambooth.dataclasses.db_config import from_file, DreamboothConfig
#     from dreambooth.diff_to_sd import compile_checkpoint
#     from dreambooth.secret import get_secret
#     from dreambooth.shared import DreamState
#     from dreambooth.ui_functions import create_model, generate_samples, \
#         start_training
#     from dreambooth.utils.gen_utils import generate_classifiers
#     from dreambooth.utils.image_utils import get_images
#     from dreambooth.utils.model_utils import get_db_models, get_lora_models
# except:
#     print("Exception importing api")
#     traceback.print_exc()

if os.environ.get("DEBUG_API", False):
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InstanceData(BaseModel):
    data: str = Field(title="File data", description="Base64 representation of the file or URL")
    name: str = Field(title="File name", description="File name to save image as")
    txt: str = Field(title="Prompt", description="Training prompt for image")


class ImageData:
    def __init__(self, name, prompt, data):
        self.name = name
        self.prompt = prompt
        self.data = data

    def dict(self):
        return {
            "name": self.name,
            "data": self.data,
            "txt": self.prompt
        }


class DbImagesRequest(BaseModel):
    imageList: List[InstanceData] = Field(title="Images",
                                          description="List of images to work on. Must be Base64 strings")


import asyncio

active = False


def is_running():
    return False


def run_in_background(func, *args, **kwargs):
    """
    Wrapper function to run a non-asynchronous method as a task in the event loop.
    """

    async def wrapper():
        global active
        new_func = functools.partial(func, *args, **kwargs)
        await asyncio.get_running_loop().run_in_executor(None, new_func)
        active = False

    asyncio.create_task(wrapper())


def zip_files(db_model_name, files, name_part=""):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a",
                         zipfile.ZIP_DEFLATED, False) as zip_file:
        for file in files:
            if isinstance(file, str):
                logger.debug(f"Zipping img: {file}")
                if os.path.exists(file) and os.path.isfile(file):
                    parent_path = os.path.join(Path(file).parent, Path(file).name)
                    zip_file.write(file, arcname=parent_path)
                    check_txt = os.path.join(os.path.splitext(file)[0], ".txt")
                    if os.path.exists(check_txt):
                        logger.debug(f"Zipping txt: {check_txt}")
                        parent_path = os.path.join(Path(check_txt).parent, Path(check_txt).name)
                        zip_file.write(check_txt, arcname=parent_path)
            else:
                img_byte_arr = io.BytesIO()
                file.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                file_name = hashlib.sha1(file.tobytes()).hexdigest()
                image_filename = f"{file_name}.png"
                zip_file.writestr(image_filename, img_byte_arr)
    zip_file.close()
    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={db_model_name}{name_part}_images.zip"}
    )

def base64_to_pil(im_b64) -> Image:
    im_b64 = bytes(im_b64, 'utf-8')
    im_bytes = base64.b64decode(im_b64)  # im_bytes is a binary image
    im_file = io.BytesIO(im_bytes)  # convert image to file-like object
    img = Image.open(im_file)
    return img

def decode_base64_to_image(encoding):
    if encoding.startswith("data:image/"):
        encoding = encoding.split(";")[1].split(",")[1]
    return Image.open(io.BytesIO(base64.b64decode(encoding)))

def file_to_base64(file_path) -> str:
    with open(file_path, "rb") as f:
        im_b64 = base64.b64encode(f.read())
        return str(im_b64, 'utf-8')

def get_bucket_and_key(s3uri):
        pos = s3uri.find('/', 5)
        bucket = s3uri[5 : pos]
        key = s3uri[pos + 1 : ]
        return bucket, key


models_type_list = ['sd', 'hypernetwork', 'lora', 'controlnet', 'embedding']
models_used_count = {key: ModelsRef() for key in models_type_list}
models_path = {key: None for key in models_type_list}
models_path['sd'] = 'models/Stable-diffusion'
models_path['controlnet'] = 'models/ControlNet'
models_path['hypernetwork'] = 'models/hypernetworks'
models_path['lora'] = 'models/Lora'
models_path['embedding'] = 'embeddings'
disk_path = '/dev/root'

def checkspace_and_update_models(selected_models):
    bucket = selected_models['bucket']
    s3_base_dir = selected_models['base_dir']
    models_num = len(models_type_list)
    for type_id in range(models_num):
        model_type = models_type_list[type_id]
        selected_models_name = selected_models[model_type]
        local_models = os.listdir(models_path[model_type])
        for selected_model_name in selected_models_name:
            models_used_count[model_type].add_models_ref(selected_model_name)
            if selected_model_name in local_models:
                continue
            else:
                total, used, free = shutil.disk_usage(disk_path)
                print('!!!!!!!!!!!!current free space is', free)
                if free < 2e10:
                    #### delete least used model to get more space ########
                    space_check_succese = False
                    for i in range(models_num):
                        type_id_check = (type_id + i)%models_num
                        type_check = models_type_list[type_id_check]
                        selected_models_name_check = selected_models[type_check]
                        local_models_check = os.listdir(models_path[type_check])
                        if len(local_models_check) == 0:
                            continue
                        sorted_local_modles, sorted_count = models_used_count[type_check].get_sorted_models(local_models_check)
                        for local_model in sorted_local_modles:
                            if local_model in selected_models_name_check:
                                continue
                            else:
                                os.remove(os.path.join(models_path[type_check], local_model))
                                models_used_count[type_check].remove_model_ref(local_model)
                                total, used, free = shutil.disk_usage(disk_path)
                                if free > 2e10:
                                    space_check_succese = True
                                    break
                        if space_check_succese:
                            break
                    if not space_check_succese:
                        print('can not get enough space to download models!!!!!!')
                        return
                ####down load models######
                download_and_update(model_type, selected_model_name, bucket, s3_base_dir)
    
    shared.opts.sd_model_checkpoint = selected_models['sd'][0]
    sd_models.reload_model_weights()
    sd_vae.reload_vae_weights()


def download_and_update(model_type, model_name, bucket,s3_base_dir):
    if model_type == 'sd':
        #download from s3
        config_file = os.path.splitext(model_name)[0] + '.yaml'
        config_path = "s3://{0}/{1}/{2}/{3}".format(bucket, s3_base_dir, models_path[model_type], config_file)
        os.system(f'./tools/s5cmd cp {config_path} {models_path[model_type]}')       
        model_data = "s3://{0}/{1}/{2}/{3}".format(bucket, s3_base_dir, models_path[model_type], model_name)
        os.system(f'./tools/s5cmd cp {model_data} {models_path[model_type]}')
        sd_models.list_models()
    else:
        model_data = "s3://{0}/{1}/{2}/{3}".format(bucket, s3_base_dir, models_path[model_type], model_name)
        os.system(f'./tools/s5cmd cp {model_data} {models_path[model_type]}')
        if model_type == 'hypernetwork':
            shared.reload_hypernetworks()
        if model_type == 'embedding':
            sd_hijack.model_hijack.embedding_db.load_textual_inversion_embeddings(force_reload=True)
        if model_type == 'controlnet':
            controlnet_script_path = './extensions/sd-webui-controlnet/scripts/controlnet.py'
            sys.path.append("extensions/sd-webui-controlnet")
            base_scripts.current_basedir = './extensions/sd-webui-controlnet/'
            script_loading.load_module(controlnet_script_path)
            sys.path.remove("extensions/sd-webui-controlnet")
            base_scripts.current_basedir = paths.script_path

def post_invocations(selected_models, b64images):
    #generated_images_s3uri = os.environ.get('generated_images_s3uri', None)
    bucket = selected_models['bucket']
    s3_base_dir = selected_models['base_dir']
    output_folder = selected_models['output']
    generated_images_s3uri = os.path.join(bucket,s3_base_dir,output_folder)
    s3_client = boto3.client('s3')
    if generated_images_s3uri:
        #generated_images_s3uri = f'{generated_images_s3uri}{username}/'
        bucket, key = get_bucket_and_key(generated_images_s3uri)
        for b64image in b64images:
            image = decode_base64_to_image(b64image)
            output = io.BytesIO()
            image.save(output, format='JPEG')
            image_id = str(uuid.uuid4())
            s3_client.put_object(
                Body=output.getvalue(),
                Bucket=bucket,
                Key=f'{key}/{image_id}.png')

def sagemaker_api(_, app: FastAPI):
    logger.debug("Loading Sagemaker API Endpoints.")
    # @app.exception_handler(RequestValidationError)
    # async def validation_exception_handler(request: Request, exc: RequestValidationError):
    #     return JSONResponse(
    #         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #         content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    #     )
            

    @app.post("/invocations")
    def invocations(req: InvocationsRequest):
        """
        Check the current state of Dreambooth processes.
        @return:
        """
        print('-------invocation------')
        #print(req)
        #print(f"json is {json.loads(req.json())}")

        if req.task == 'text-to-image' or req.task == 'controlnet_txt2img':
            selected_models = req.models
            checkspace_and_update_models(selected_models)

        try:
            if req.task == 'text-to-image':
                response = requests.post(url=f'http://0.0.0.0:8080/sdapi/v1/txt2img', json=json.loads(req.txt2img_payload.json()))
                #response_info = response.json()
                #print(response_info.keys())
                return response.json()
            elif req.task == 'controlnet_txt2img':  
                response = requests.post(url=f'http://0.0.0.0:8080/controlnet/txt2img', json=json.loads(req.controlnet_txt2img_payload.json()))
                #response_info = response.json()
                #print(response_info.keys())
                #post_invocations(selected_models, response_info['images'])
                return response.json()
            elif req.task == 'image-to-image':
                # response = self.img2imgapi(req.img2img_payload)
                # shared.opts.data = default_options
                response = None
                return response
            elif req.task == 'extras-single-image':
                # response = self.extras_single_image_api(req.extras_single_payload)
                # shared.opts.data = default_options
                response = None
                return response
            elif req.task == 'extras-batch-images':
                # response = self.extras_batch_images_api(req.extras_batch_payload)
                # shared.opts.data = default_options
                response = None
                return response                
            # elif req.task == 'sd-models':
            #     return self.get_sd_models()
            elif req.task == 'db-create-model':
                r"""
                task: db-create-model
                db_create_model_payload:
                    :s3_input_path: S3 path for download src model.
                    :s3_output_path: S3 path for upload generated model.
                    :job_id: job id.
                    :param
                        :new_model_name: generated model name.
                        :ckpt_path: S3 path for download src model.
                        :from_hub=False,
                        :new_model_url="",
                        :new_model_token="",
                        :extract_ema=False,
                        :train_unfrozen=False,
                        :is_512=True,
                """
                try:
                    db_create_model_payload = json.loads(req.db_create_model_payload)
                    job_id = db_create_model_payload["job_id"]
                    s3_input_path = db_create_model_payload["s3_input_path"]
                    input_bucket_name = get_bucket_name_from_s3_path(s3_input_path)
                    s3_output_path = db_create_model_payload["s3_output_path"]
                    output_bucket_name = get_bucket_name_from_s3_path(s3_output_path)
                    output_path = get_path_from_s3_path(s3_output_path)
                    db_create_model_params = db_create_model_payload["param"]["create_model_params"]
                    local_model_path = f'{db_create_model_params["ckpt_path"]}.tar'
                    input_path = os.path.join(get_path_from_s3_path(s3_input_path), local_model_path)
                    print("Check disk usage before download.")
                    os.system("df -h")
                    logger.info(f"Download src model from s3 {input_bucket_name} {input_path} {local_model_path}")
                    download_folder_from_s3_by_tar(input_bucket_name, input_path, local_model_path)
                    logger.info("Check disk usage after download.")
                    os.system("df -h")
                    print("Start creating model.")
                    # local_response = requests.post(url=f'http://0.0.0.0:8080/dreambooth/createModel',
                    #                         params=db_create_model_params)
                    create_model_func_args = copy.deepcopy(db_create_model_params)
                    # ckpt_path = create_model_func_args.pop("new_model_src")
                    # create_model_func_args["ckpt_path"] = ckpt_path
                    local_response = create_model(**create_model_func_args)
                    target_local_model_dir = f'models/dreambooth/{db_create_model_params["new_model_name"]}'
                    print("Upload tgt model to s3.")
                    upload_folder_to_s3_by_tar(target_local_model_dir, output_bucket_name, output_path)
                    config_file = os.path.join(target_local_model_dir, "db_config.json")
                    with open(config_file, 'r') as openfile:
                        config_dict = json.load(openfile)
                    message = {
                        "response": local_response,
                        "config_dict": config_dict
                    }
                    response = {
                        "id": job_id,
                        "statusCode": 200,
                        "message": message,
                        "outputLocation": [f'{s3_output_path}/db_create_model_params["new_model_name"]']
                    }
                    # Clean up
                    print("Delete tgt model.")
                    os.system(f"rm -rf models/dreambooth")
                    print("Check disk usage after request.")
                    os.system("df -h")
                    return response
                except Exception as e:
                    response = {
                        "id": job_id,
                        "statusCode": 500,
                        "message": e,
                    }
                    logger.error(e)
                    return response
        #     elif req.task == 'merge-checkpoint':
        #         r"""
        #         task: merge checkpoint
        #         db_create_model_payload:
        #             :s3_input_path: S3 path for download src model.
        #             :s3_output_path: S3 path for upload generated model.
        #             :job_id: job id.
        #             :param
        #                 :new_model_name: generated model name.
        #                 :new_model_src: S3 path for download src model.
        #                 :from_hub=False,
        #                 :new_model_url="",
        #                 :new_model_token="",
        #                 :extract_ema=False,
        #                 :train_unfrozen=False,
        #                 :is_512=True,
        #         """
        #         try:
        #             merge_checkpoint_payload = json.loads(req.merge_checkpoint_paylod)
        #             def modelmerger(*args):
        #                 try:
        #                     results = modules.extras.run_modelmerger(*args)
        #                 except Exception as e:
        #                     print("Error loading/saving model file:", file=sys.stderr)
        #                     print(traceback.format_exc(), file=sys.stderr)
        #                     modules.sd_models.list_models()  # to remove the potentially missing models from the list
        #                     return [*[gr.Dropdown.update(choices=modules.sd_models.checkpoint_tiles()) for _ in range(4)], f"Error merging checkpoints: {e}"]
        #                 return results
        #         primary_model_name, secondary_model_name, tertiary_model_name,
        #         component_dict['sd_model_checkpoint'],
        #         modelmerger_result,
        # modelmerger_merge.click(
        #     fn=wrap_gradio_gpu_call(modelmerger, extra_outputs=lambda: [gr.update() for _ in range(4)]),
        #     _js='modelmerger',
        #     inputs=[
        #         dummy_component,
        #         primary_model_name,
        #         secondary_model_name,
        #         tertiary_model_name,
        #         interp_method,
        #         interp_amount,
        #         save_as_half,
        #         custom_name,
        #         checkpoint_format,
        #         config_source,
        #         bake_in_vae,
        #         discard_weights,
        #     ],
        #     outputs=[
        #         primary_model_name,
        #         secondary_model_name,
        #         tertiary_model_name,
        #         component_dict['sd_model_checkpoint'],
        #         modelmerger_result,
        #     ]
        # )
            else:
                raise NotImplementedError
        except Exception as e:
            traceback.print_exc()

    @app.get("/ping")
    def ping():
        print('-------ping------')
        return {'status': 'Healthy'}

def move_model_to_tmp(_, app: FastAPI):
    # os.system("rm -rf models")
    # Create model dir
    # print("Create model dir")
    # os.system("mkdir models")
    # Move model dir to /tmp
    model_tmp_dir = f"models_{time.time()}"
    os.system(f"cp -rL models /tmp/{model_tmp_dir}")
    os.system(f"rm -rf models")
    # Delete tmp model dir
    # print("Delete tmp model dir")
    # os.system("rm -rf /tmp/models")

try:
    import modules.script_callbacks as script_callbacks

    script_callbacks.on_app_started(sagemaker_api)
    script_callbacks.on_app_started(move_model_to_tmp)
    logger.debug("SD-Webui API layer loaded")
except Exception as e:
    print(e)
    logger.debug("Unable to import script callbacks.")
    pass
