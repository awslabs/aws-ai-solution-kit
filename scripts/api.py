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
from modules import sd_hijack, sd_models, script_loading
from modules.hypernetworks import hypernetwork
from modules.textual_inversion import textual_inversion
import modules.shared as shared
import sys
sys.path.append("extensions/sd-webui-sagemaker")
from scripts.models import *
import requests

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


def file_to_base64(file_path) -> str:
    with open(file_path, "rb") as f:
        im_b64 = base64.b64encode(f.read())
        return str(im_b64, 'utf-8')


script_path = 'stable-diffusion-webui'
s3_model_path = 'stable-diffusion-webui/models'
local_model_path = 'models'
bucket = 'sagemaker-us-west-2-725399406069'
sd_model_folder = 'Stable-diffusion'
controlnet_model_folder = 'ControlNet'
hypernetwork_model_folder = 'hypernetworks'
lora_model_folder = 'Lora'
embedding_model_folder = 'embeddings'

def update_models(selected_models):
    #sd model update
    selected_sd_model = selected_models['stablediffusion'][0]
    sd_model_list = os.listdir(os.path.join(local_model_path, sd_model_folder))
    if selected_sd_model not in sd_model_list:
    #download from s3
        config_file = os.path.splitext(selected_sd_model)[0] + '.yaml'
        config_path = "s3://{0}/{1}/{2}/{3}".format(bucket, s3_model_path, sd_model_folder, config_file)
        os.system(f'./tools/s5cmd cp {config_path} ./models/Stable-diffusion/')       
        model_data = "s3://{0}/{1}/{2}/{3}".format(bucket, s3_model_path, sd_model_folder, selected_sd_model)
        os.system(f'./tools/s5cmd cp {model_data} ./models/Stable-diffusion/')
        sd_models.list_models()
    shared.opts.sd_model_checkpoint = selected_sd_model
    sd_models.reload_model_weights()  
    
    #hypernetworks update
    selected_hypernet_models = selected_models['hypernetwork']
    hypernet_model_list = os.listdir(os.path.join(local_model_path, hypernetwork_model_folder))
    for selected_hypernet_model in selected_hypernet_models:
        if selected_hypernet_model not in hypernet_model_list:
        #download from s3
            model_data = "s3://{0}/{1}/{2}/{3}".format(bucket, s3_model_path, hypernetwork_model_folder, selected_hypernet_model)
            os.system(f'./tools/s5cmd cp {model_data} ./models/hypernetworks/')
    #hypernetwork.load_hypernetworks(selected_hypernet_models)

    selected_lora_models = selected_models['lora']
    lora_model_list = os.listdir(os.path.join(local_model_path, lora_model_folder))
    for selected_lora_model in selected_lora_models:
        if selected_lora_model not in lora_model_list:
        #download from s3
            model_data = "s3://{0}/{1}/{2}/{3}".format(bucket, s3_model_path, lora_model_folder, selected_lora_model)
            os.system(f'./tools/s5cmd cp {model_data} ./models/Lora/')
    
    selected_embeddings = selected_models['textualinversion']
    embedding_list = os.listdir(embedding_model_folder)
    reload_embedding = False
    for selected_embedding in selected_embeddings:
        if selected_embedding not in embedding_list:
        #download from s3
            model_data = "s3://{0}/{1}/{2}/{3}".format(bucket, script_path, embedding_model_folder, selected_embedding)
            os.system(f'./tools/s5cmd cp {model_data} ./embeddings/')
            reload_embedding = True
    if reload_embedding:
        sd_hijack.model_hijack.embedding_db.load_textual_inversion_embeddings(force_reload=True)
        
    selected_controlnets = selected_models['controlnet']
    controlnet_model_list = os.listdir(os.path.join(local_model_path, controlnet_model_folder))
    for selected_controlnet in selected_controlnets:
        if selected_controlnet not in controlnet_model_list:
            #download from s3
            model_data = "s3://{0}/{1}/{2}/{3}".format(bucket, s3_model_path, controlnet_model_folder, selected_controlnet)
            os.system(f'./tools/s5cmd cp {model_data} ./models/ControlNet/')




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

        try:
            if req.task == 'text-to-image':
                selected_sd_model = req.models
                update_models(selected_sd_model)
                response = requests.post(url=f'http://0.0.0.0:8080/sdapi/v1/txt2img', json=json.loads(req.txt2img_payload.json()))
                return response.json()
            elif req.task == 'controlnet_txt2img':
                selected_sd_model = req.models
                update_models(selected_sd_model)
                controlnet_script_path = './extensions/sd-webui-controlnet/scripts/controlnet.py'
                sys.path.append("extensions/sd-webui-controlnet")
                script_loading.load_module(controlnet_script_path)
                sys.path.remove("extensions/sd-webui-controlnet")
                controlnet_config_folder = "./extensions/sd-webui-controlnet/models/"
                target_folder = './models/'
                files = os.listdir(controlnet_config_folder)
                for file_name in files:
                    shutil.copy(controlnet_config_folder+file_name, target_folder+file_name)
                response = requests.post(url=f'http://0.0.0.0:8080/controlnet/txt2img', json=json.loads(req.controlnet_txt2img_payload.json()))
                return response.json()
            elif req.task == 'image-to-image':
                # self.download_s3files(embeddings_s3uri, os.path.join(script_path, shared.cmd_opts.embeddings_dir))
                # sd_hijack.model_hijack.embedding_db.load_textual_inversion_embeddings()
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
            else:
                raise NotImplementedError
        except Exception as e:
            traceback.print_exc()

    @app.get("/ping")
    def ping():
        print('-------ping------')
        return {'status': 'Healthy'}

try:
    import modules.script_callbacks as script_callbacks

    script_callbacks.on_app_started(sagemaker_api)
    logger.debug("SD-Webui API layer loaded")
except:
    logger.debug("Unable to import script callbacks.")
    pass
