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
from urllib.parse import urlparse

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
import sys
sys.path.append("extensions/aws-ai-solution-kit")
from scripts.models import *
import requests
from utils import download_file_from_s3, download_folder_from_s3, download_folder_from_s3_by_tar, upload_folder_to_s3, upload_file_to_s3, upload_folder_to_s3_by_tar

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

def get_bucket_name_from_s3_url(s3_path) -> str:
    o = urlparse(s3_path, allow_fragments=False)
    return o.netloc

def get_bucket_name_from_s3_path(s3_path) -> str:
    return s3_path.split("/")[0]

def get_path_from_s3_path(s3_path) -> str:
    return "/".join(s3_path.split("/")[1:])

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
        print(req)

        print(f"json is {json.loads(req.json())}")

        try:
            if req.task == 'text-to-image':
                response = requests.post(url=f'http://0.0.0.0:8080/sdapi/v1/txt2img', json=json.loads(req.txt2img_payload.json()))
                return response.json()
            elif req.task == 'controlnet_txt2img':
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
            elif req.task == 'db-create-model':
                r"""
                task: db-create-model
                db_create_model_payload:
                    :s3_input_path: S3 path for download src model.
                    :s3_output_path: S3 path for upload generated model.
                    :job_id: job id.
                    :param
                        :new_model_name: generated model name.
                        :new_model_src: S3 path for download src model.
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
                    s3_input_path = db_create_model_payload["s3_input_path"][0]
                    input_bucket_name = get_bucket_name_from_s3_path(s3_input_path)
                    input_path = get_path_from_s3_path(s3_input_path)
                    s3_output_path = db_create_model_payload["s3_output_path"][0]
                    output_bucket_name = get_bucket_name_from_s3_path(s3_output_path)
                    output_path = get_path_from_s3_path(s3_output_path)
                    db_create_model_params = db_create_model_payload["param"]
                    local_model_path = f'{db_create_model_params["new_model_src"]}.tar'
                    print("Check disk usage before download.")
                    os.system("df -h")
                    print("Download src model from s3.")
                    download_folder_from_s3_by_tar(input_bucket_name, input_path, local_model_path)
                    local_response = requests.post(url=f'http://0.0.0.0:8080/dreambooth/createModel',
                                            params=db_create_model_params)
                    target_local_model_dir = f'models/dreambooth/{db_create_model_params["new_model_name"]}'
                    print("Check disk usage after download.")
                    os.system("df -h")
                    print("Delete src model.")
                    os.system(f"rm -rf models/Stable-diffusion")
                    print("Upload tgt model to s3.")
                    upload_folder_to_s3_by_tar(target_local_model_dir, output_bucket_name, output_path)
                    print("Delete tgt model.")
                    os.system(f"rm -rf models/dreambooth")
                    print("Check disk usage after request.")
                    os.system("df -h")
                    message = local_response.json()
                    response = {
                        "id": job_id,
                        "statusCode": 200,
                        "message": message,
                        "outputLocation": [f'{s3_output_path}/db_create_model_params["new_model_name"]']
                    }
                    return response
                except Exception as e:
                    response = {
                        "id": job_id,
                        "statusCode": 500,
                        "message": e,
                    }
                    return response
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
    # Move model dir to /tmp
    print("Move model dir")
    os.system("mv models /tmp/")
    print("Link model dir")
    os.system("ln -s /tmp/models models")
    print("Check disk usage on app started")
    os.system("df -h")
    logger.debug("SD-Webui API layer loaded")
except:
    logger.debug("Unable to import script callbacks.")
    pass
