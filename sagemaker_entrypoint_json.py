import os
import json
import threading
import sys
import time
import pickle

import boto3
from utils import download_file_from_s3, download_folder_from_s3, download_folder_from_s3_by_tar, upload_folder_to_s3, upload_file_to_s3, upload_folder_to_s3_by_tar

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

def prepare_for_training(bucket_name):
    s3 = boto3.client('s3')

    # # Do this in the webui.
    # model_dir = 'sagemaker_test'
    # local_model_dir = f'models/dreambooth/{model_dir}'
    # s3_model_dir = f'aigc-webui-test-model'
    # upload_folder_to_s3(local_model_dir, bucket_name, s3_model_dir)
    # model_config_file = open(f'{local_model_dir}/db_config.json')
    # model_parameters = json.load(model_config_file)
    # # Get data dir from the config file in the model dir.
    # data_dir = model_parameters['concepts_list'][0]['instance_data_dir']
    # local_data_dir = data_dir
    # s3_data_dir = f'aigc-webui-test-data'
    # upload_folder_to_s3(local_data_dir, bucket_name, s3_data_dir)
    # parameters = {
    #     'model_dir': model_dir,
    #     'data_dir': data_dir,
    #     'use_txt2img': True
    #     }
    # sm_params_conf_file_path = 'sagemaker_parameters.json'
    # sm_params_conf_file = open(sm_params_conf_file_path, 'w')
    # json.dump(parameters, sm_params_conf_file)
    # sm_params_conf_file.close()
    # sm_params_conf_file_s3_path = f'aigc-webui-test-config/{sm_params_conf_file_path}'
    # upload_file_to_s3(sm_params_conf_file_path, bucket_name, sm_params_conf_file_s3_path)

    # Download config file.
    print('Download config file from s3.')
    download_file_from_s3(bucket_name, 'aigc-webui-test-config/sagemaker_parameters.json', 'sagemaker_parameters.json')
    sm_params_conf_file = open("sagemaker_parameters.json")
    parameters = json.load(sm_params_conf_file)
    print(f'parameters: {parameters}')
    job_id = parameters['job_id']

    model_dir = parameters['model_dir']
    s3_model_tar_path = f'aigc-webui-test-model/{job_id}/{model_dir}.tar'
    local_model_dir = f'{model_dir}.tar'
    print('Download model file from s3.')
    download_folder_from_s3_by_tar(bucket_name, s3_model_tar_path, local_model_dir)
    data_dir = parameters['data_dir']
    s3_data_tar_path = f'aigc-webui-test-data/{job_id}/{data_dir}.tar'
    local_data_dir = f'{data_dir}.tar'
    print('Download data file from s3.')
    download_folder_from_s3_by_tar(bucket_name, s3_data_tar_path, local_data_dir)
    class_data_dir = parameters['class_data_dir']
    if class_data_dir:
        s3_data_tar_path = f'aigc-webui-test-data/{job_id}/{class_data_dir}.tar'
        local_data_dir = f'{class_data_dir}.tar'
        print('Download class data file from s3.')
        download_folder_from_s3_by_tar(bucket_name, s3_data_tar_path, local_data_dir)
    model_dir = parameters["model_dir"]
    use_txt2img = parameters["use_txt2img"]
    return job_id, model_dir, use_txt2img

def sync_status(job_id, bucket_name, model_dir):
    local_samples_dir = f'models/dreambooth/{model_dir}/samples'
    upload_thread = threading.Thread(target=check_and_upload, args=(local_samples_dir, bucket_name, f'aigc-webui-test-samples/{job_id}'))
    upload_thread.start()
    sync_status_thread = threading.Thread(target=sync_status_from_s3_in_sagemaker,
                                        args=(bucket_name, f'aigc-webui-test-status/{job_id}/webui_status.pickle',
                                              f'aigc-webui-test-status/{job_id}/sagemaker_status.pickle'))
    sync_status_thread.start()

def main():
    bucket_name = "aws-gcr-csdc-atl-exp-us-west-2"
    job_id, model_dir, use_txt2img = prepare_for_training(bucket_name)
    sync_status(job_id, bucket_name, model_dir)
    train(model_dir)

if __name__ == "__main__":
    main()
    # local test
    # train("dreambooth_sagemaker_test")