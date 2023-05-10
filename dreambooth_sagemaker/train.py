import time
import pickle
import json
import threading
import base64

# import sagemaker

import sys
import os
sys.path.append("extensions/sd_dreambooth_extension")
sys.path.append("extensions/aws-ai-solution-kit")
from utils import download_folder_from_s3_by_tar, download_file_from_s3, upload_file_to_s3, upload_folder_to_s3_by_tar
from dreambooth.shared import status

# def sync_status_from_s3_in_webui(bucket_name, sagemaker_status_file_path, webui_status_file_path):
#     while True:
#         time.sleep(1)
#         print(f'status: {status.__dict__}')
#         try:
#             download_file_from_s3(bucket_name, sagemaker_status_file_path, 'sagemaker_status.pickle')
#             with open('sagemaker_status.pickle', 'rb') as sagemaker_status_file:
#                 sagemaker_status = pickle.load(sagemaker_status_file)
#                 status.job = sagemaker_status.job
#                 status.job_no = sagemaker_status.job_no
#                 status.job_count = sagemaker_status.job_count
#                 status.job_timestamp = sagemaker_status.job_timestamp
#                 status.sampling_step = sagemaker_status.sampling_step
#                 status.sampling_steps = sagemaker_status.sampling_steps
#                 status.current_latent = sagemaker_status.current_latent
#                 status.current_image = sagemaker_status.current_image
#                 status.current_image_sampling_step = sagemaker_status.current_image_sampling_step
#                 status.textinfo = sagemaker_status.textinfo
#                 status.textinfo2 = sagemaker_status.textinfo2
#         except Exception as e:
#             print('The sagemaker status file is not exists')
#             print(f'error: {e}')
#         with open('webui_status.pickle', 'wb') as webui_status_file:
#             pickle.dump(status, webui_status_file)
#         upload_file_to_s3('webui_status.pickle', bucket_name, webui_status_file_path)

def check_and_download(bucket, s3_path, local_path):
    while True:
        try:
            print(f'download {s3_path} to {local_path}')
            time.sleep(1)
            download_folder_from_s3_by_tar(bucket, s3_path, local_path)
        except Exception as e:
            print(f'{s3_path} is not exists')
            print(f'error: {e}')

def upload_assets(model_dir, use_txt2img, instance_type, job_id):
    bucket_name = "aws-gcr-csdc-atl-exp-us-west-2"
    local_model_dir = f'models/dreambooth/{model_dir}'
    s3_model_dir = f'aigc-webui-test-model/{job_id}'
    upload_folder_to_s3_by_tar(local_model_dir, bucket_name, s3_model_dir)
    model_config_file = open(f'{local_model_dir}/db_config.json')
    model_parameters = json.load(model_config_file)
    # Get data dir from the config file in the model dir.
    data_dir = model_parameters['concepts_list'][0]['instance_data_dir']
    local_data_dir = data_dir
    s3_data_dir = f'aigc-webui-test-data/{job_id}'
    upload_folder_to_s3_by_tar(local_data_dir, bucket_name, s3_data_dir)
    # Get class data dir from the config file in the model dir.
    class_data_dir = model_parameters['concepts_list'][0]['class_data_dir']
    if class_data_dir:
        local_data_dir = class_data_dir
        s3_data_dir = f'aigc-webui-test-data/{job_id}'
        upload_folder_to_s3_by_tar(local_data_dir, bucket_name, s3_data_dir)

    parameters = {
        'model_dir': model_dir,
        'data_dir': data_dir,
        'use_txt2img': use_txt2img,
        'job_id': job_id,
        'instance_type': instance_type,
        'class_data_dir': class_data_dir
        }
    sm_params_conf_file_path = 'sagemaker_parameters.json'
    sm_params_conf_file = open(sm_params_conf_file_path, 'w')
    json.dump(parameters, sm_params_conf_file)
    sm_params_conf_file.close()
    sm_params_conf_file_s3_path = f'aigc-webui-test-config/{sm_params_conf_file_path}'
    upload_file_to_s3(sm_params_conf_file_path, bucket_name, sm_params_conf_file_s3_path)


def start_sagemaker_training(params, instance_type, s3_input_path, s3_output_path):
    # job_id = time.time()
    job_id = "test"
    # upload_assets(model_dir, use_txt2img, instance_type, job_id)

    role = "arn:aws:iam::683638520402:role/service-role/AmazonSageMaker-ExecutionRole-20221031T120168"
    # role = "arn:aws:iam::648149843064:role/SdDreamBoothTrainStack-aigcutilsendpointrole0A8729-8OSFWEAGUTCU"
    # image_uri = "683638520402.dkr.ecr.us-west-2.amazonaws.com/aigc-webui-dreambooth-training:latest"
    # image_uri = "648149843064.dkr.ecr.us-east-1.amazonaws.com/aigc-webui-dreambooth-training:latest"
    # image_uri = "991301791329.dkr.ecr.us-west-1.amazonaws.com/aigc-webui-dreambooth-training"
    image_uri = "991301791329.dkr.ecr.us-west-1.amazonaws.com/aigc-train-utils:latest"
    # image_uri = "683638520402.dkr.ecr.us-west-2.amazonaws.com/aigc-5:latest"

    # JSON encode hyperparameters
    def json_encode_hyperparameters(hyperparameters):
        new_params = {}
        for k, v in hyperparameters.items():
            json_v = json.dumps(v)
            v_bytes = json_v.encode('ascii')
            base64_bytes = base64.b64encode(v_bytes)
            base64_v = base64_bytes.decode('ascii')
            new_params[k] = base64_v
        return new_params

    hyperparameters = json_encode_hyperparameters({
            "sagemaker_program": "extensions/sd-webui-sagemaker/sagemaker_entrypoint_json.py",
            "params": params,
            "s3-input-path": s3_input_path,
            "s3-output-path": s3_output_path
    })
    # status.begin()
    est = sagemaker.estimator.Estimator(
        image_uri,
        role,
        instance_count=1,
        instance_type=instance_type,
        volume_size=125,
        base_job_name="dreambooth-sagemaker-train",
        hyperparameters=hyperparameters,
        job_id=job_id,
    )
    status.textinfo = "Starting SageMaker training"
    print(status.textinfo)
    est.fit(wait=False)
    while not est._current_job_name:
        time.sleep(1)
    job_url_prefix = 'https://us-west-2.console.aws.amazon.com/sagemaker/home?region=us-west-2#/jobs/'
    job_url = f'{job_url_prefix}{est._current_job_name}'
    status.textinfo = f'SageMaker job link <a href={job_url}>{job_url}</a><br>'
    # bucket_name = "aws-gcr-csdc-atl-exp-us-west-2"
    # download_thread = threading.Thread(target=check_and_download, args=(bucket_name, f'aigc-webui-test-samples/{job_id}/samples.tar', 'samples.tar'))
    # download_thread.start()
    # # download_folder_from_s3_by_tar('aws-gcr-csdc-atl-exp-us-west-2', 'aigc-webui-test-samples/samples.tar', 'samples.tar')
    # sync_status_thread = threading.Thread(target=sync_status_from_s3_in_webui,
    #                                     args=(bucket_name, f'aigc-webui-test-status/{job_id}/sagemaker_status.pickle',
    #                                           f'aigc-webui-test-status/{job_id}/webui_status.pickle'))
    # sync_status_thread.start()

    import boto3
    boto3_sagemaker = boto3.client('sagemaker')
    # est.latest_training_job.name
    resp = boto3_sagemaker.describe_training_job(
        TrainingJobName=est.latest_training_job.name
    )




    # from sagemaker.estimator import Estimator
    # attached_estimator = Estimator.attach(est._current_job_name)
    # attached_estimator.logs()
    # return status


def test_func():
    import boto3
    boto3_sagemaker = boto3.client('sagemaker')
    # est.latest_training_job.name
    resp = boto3_sagemaker.describe_training_job(
        TrainingJobName='dreambooth-sagemaker-train-2023-04-19-07-32-32-218'
    )
    print(resp['TrainingJobStatus'])
    print(resp['FailureReason'])

if __name__ == "__main__":
    # instance_type = "ml.g5.16xlarge"
    # os.environ.setdefault('AWS_PROFILE', 'cloudfront_ext')
    # test_func()
    """
        "params": params,
        "s3_input_path": "s3://bucket/dreambooth/requestid/input/",
        "s3_output_path": "s3://bucket/dreambooth/requestid/output/"
        "instance_type": "ml.g5.xlarge"
    """
    with open("models/dreambooth/db-training-test-1/db_config.json.bak", "r") as db_config_file:
        db_config = json.load(db_config_file)
    params = {
        "s3_input_path": "s3://alvindaiyan-aigc-testing-playground/dreambooth/train/db-training-test-1/819d981e-a30e-4944-9668-8ad03264f0fe/input",
        "s3_output_path": "s3://alvindaiyan-aigc-testing-playground/dreambooth/train/db-training-test-1/e223988b-faa1-442e-b00b-030ee01b4357/output",
        "params": {
            "training_params": {
                "s3_model_path": "s3://alvindaiyan-aigc-testing-playground/dreambooth/model/db-training-test-1/51b8d59b-ba48-4f79-964f-05f2190f5bc3/output/",
                "model_name": "db-training-test-1",
                "data_tar": "data_images.tar",
                "class_data_tar": "class_data_images.tar",
            }
        }
    }
    instance_type = "local_gpu"
    s3_input_path = params["s3_input_path"]
    s3_output_path = params["s3_output_path"]
    start_sagemaker_training(params["params"], instance_type, s3_input_path, s3_output_path)
