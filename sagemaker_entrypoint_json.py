import os
import re
import json
import threading
import sys
import time
import pickle
import logging
import base64
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import boto3
from utils import download_file_from_s3, download_folder_from_s3, download_folder_from_s3_by_tar, upload_folder_to_s3, upload_file_to_s3, upload_folder_to_s3_by_tar
from utils import get_bucket_name_from_s3_path, get_path_from_s3_path

os.environ['IGNORE_CMD_ARGS_ERRORS'] = ""
sys.path.append(os.path.join(os.getcwd(), "extensions/sd_dreambooth_extension"))
from dreambooth.ui_functions import start_training
from dreambooth.shared import status

def sync_status_from_s3_json(bucket_name, webui_status_file_path, sagemaker_status_file_path):
    while True:
        time.sleep(1)
        print(f'sagemaker status: {status.__dict__}')
        try:
            download_file_from_s3(bucket_name, webui_status_file_path, 'webui_status.json')
            with open('webui_status.json') as webui_status_file:
                webui_status = json.load(webui_status_file)
            status.do_save_model = webui_status['do_save_model']
            status.do_save_samples = webui_status['do_save_samples']
            status.interrupted = webui_status['interrupted']
            status.interrupted_after_save = webui_status['interrupted_after_save']
            status.interrupted_after_epoch =  webui_status['interrupted_after_epoch']
        except Exception as e:
            print('The webui status file is not exists')
            print(e)
        with open('sagemaker_status.json', 'w') as sagemaker_status_file:
            json.dump(status.__dict__, sagemaker_status_file)
        upload_file_to_s3('sagemaker_status.json', bucket_name, sagemaker_status_file_path)

def sync_status_from_s3_in_sagemaker(bucket_name, webui_status_file_path, sagemaker_status_file_path):
    while True:
        time.sleep(1)
        print(status.__dict__)
        try:
            download_file_from_s3(bucket_name, webui_status_file_path, 'webui_status.pickle')
            with open('webui_status.pickle', 'rb') as webui_status_file:
                webui_status = pickle.load(webui_status_file)
            status.do_save_model = webui_status['do_save_model']
            status.do_save_samples = webui_status['do_save_samples']
            status.interrupted = webui_status['interrupted']
            status.interrupted_after_save = webui_status['interrupted_after_save']
            status.interrupted_after_epoch =  webui_status['interrupted_after_epoch']
        except Exception as e:
            print('The webui status file is not exists')
            print(f'error: {e}')
        with open('sagemaker_status.pickle', 'wb') as sagemaker_status_file:
            pickle.dump(status, sagemaker_status_file)
        upload_file_to_s3('sagemaker_status.pickle', bucket_name, sagemaker_status_file_path)

def train(model_dir):
    start_training(model_dir)

def check_and_upload(local_path, bucket, s3_path):
    while True:
        time.sleep(1)
        if os.path.exists(local_path):
            print(f'upload {s3_path} to {local_path}')
            upload_folder_to_s3_by_tar(local_path, bucket, s3_path)
        else:
            print(f'{local_path} is not exist')

def upload_model_to_s3(model_name, s3_output_path):
    output_bucket_name = get_bucket_name_from_s3_path(s3_output_path)
    local_path = os.path.join("models/Stable-diffusion", model_name)
    s3_output_path = get_path_from_s3_path(s3_output_path)
    logger.info(f"Upload check point to s3 {local_path} {output_bucket_name} {s3_output_path}")
    print(f"Upload check point to s3 {local_path} {output_bucket_name} {s3_output_path}")
    upload_folder_to_s3_by_tar(local_path, output_bucket_name, s3_output_path)
    return os.path.join(s3_output_path, f"{model_name}.tar")

def hack_db_config(db_config, db_config_file_path, model_name):
    for k in db_config:
        if type(db_config[k]) is str:
            if k == "model_dir":
                db_config[k] = re.sub(".+/(models/dreambooth/).+$", f"\\1{model_name}", db_config[k])
            elif k == "pretrained_model_name_or_path":
                db_config[k] = re.sub(".+/(models/dreambooth/).+(working)$", f"\\1{model_name}/\\2", db_config[k])
            elif k == "model_name":
                db_config[k] = db_config[k].replace("dummy_local_model", model_name)
            else:
                db_config[k] = db_config[k].replace("dummy_local_model", model_name)
    with open(db_config_file_path, "w") as db_config_file_w:
        json.dump(db_config, db_config_file_w)

def prepare_for_training(s3_model_path, model_name, s3_input_path, data_tar_list, class_data_tar_list):
    model_bucket_name = get_bucket_name_from_s3_path(s3_model_path)
    s3_model_path = os.path.join(get_path_from_s3_path(s3_model_path), f'{model_name}.tar')
    logger.info(f"Download src model from s3 {model_bucket_name} {s3_model_path} {model_name}.tar")
    print(f"Download src model from s3 {model_bucket_name} {s3_model_path} {model_name}.tar")
    download_folder_from_s3_by_tar(model_bucket_name, s3_model_path, f'{model_name}.tar')

    input_bucket_name = get_bucket_name_from_s3_path(s3_input_path)
    input_path = os.path.join(get_path_from_s3_path(s3_input_path), "db_config.tar")
    logger.info(f"Download db_config from s3 {input_bucket_name} {input_path} db_config.tar")
    download_folder_from_s3_by_tar(input_bucket_name, input_path, "db_config.tar")
    db_config_path = f"models/dreambooth/{model_name}/db_config.json"
    with open("models/dreambooth/dummy_local_model/db_config.json") as db_config_file:
        db_config = json.load(db_config_file)
    hack_db_config(db_config, db_config_path, model_name)

    for data_tar in data_tar_list:
        input_path = os.path.join(get_path_from_s3_path(s3_input_path), data_tar)
        logger.info(f"Download data from s3 {input_bucket_name} {input_path} {data_tar}")
        download_folder_from_s3_by_tar(input_bucket_name, input_path, data_tar)
    for class_data_tar in class_data_tar_list:
        input_path = os.path.join(get_path_from_s3_path(s3_input_path), class_data_tar)
        logger.info(f"Download class data from s3 {input_bucket_name} {input_path} {class_data_tar}")
        download_folder_from_s3_by_tar(input_bucket_name, input_path, class_data_tar)

def sync_status(job_id, bucket_name, model_dir):
    local_samples_dir = f'models/dreambooth/{model_dir}/samples'
    upload_thread = threading.Thread(target=check_and_upload, args=(local_samples_dir, bucket_name, f'aigc-webui-test-samples/{job_id}'))
    upload_thread.start()
    sync_status_thread = threading.Thread(target=sync_status_from_s3_in_sagemaker,
                                        args=(bucket_name, f'aigc-webui-test-status/{job_id}/webui_status.pickle',
                                              f'aigc-webui-test-status/{job_id}/sagemaker_status.pickle'))
    sync_status_thread.start()

def main(s3_input_path, s3_output_path, params):
    params = params["training_params"]
    model_name = params["model_name"]
    s3_model_path = params["s3_model_path"]
    data_tar_list = params["data_tar_list"]
    if "class_data_tar_list" in params:
        class_data_tar_list = params["class_data_tar_list"]
    else:
        class_data_tar_list = None
    prepare_for_training(s3_model_path, model_name, s3_input_path, data_tar_list, class_data_tar_list)
    # sync_status(job_id, bucket_name, model_dir)
    train(model_name)
    upload_model_to_s3(model_name, s3_output_path)

def test():
    model_name = "dreambooth_sagemaker_test"
    s3_model_path = "s3://aws-gcr-csdc-atl-exp-us-west-2/aigc-webui-test-model/db_test_4.tar"
    s3_input_path = "s3://aws-gcr-csdc-atl-exp-us-west-2/aigc-webui-test-data/dataset/"
    s3_output_path = "s3://aws-gcr-csdc-atl-exp-us-west-2/aigc-webui-test-output/"
    training_params = {
        "training_params": {
            "model_name": model_name,
            "s3_model_path": s3_model_path,
            "data_tar": "data_images.tar",
            "class_data_tar": "class_data_images.tar" 
        }
    }
    main(s3_input_path, s3_output_path, training_params)

def parse_params(args):
    def decode_base64(base64_message):
        base64_bytes = base64_message.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode('ascii')
        return message
    s3_input_path = json.loads(decode_base64(args.s3_input_path))
    s3_output_path = json.loads(decode_base64(args.s3_output_path))
    params = json.loads(decode_base64(args.params))
    return s3_input_path, s3_output_path, params

if __name__ == "__main__":
    # test()
    print(sys.argv)
    import argparse
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--params", type=str)
    parser.add_argument("--s3-input-path", type=str)
    parser.add_argument("--s3-output-path", type=str)
    args, _ = parser.parse_known_args()
    s3_input_path, s3_output_path, training_params = parse_params(args)
    main(s3_input_path, s3_output_path, training_params)