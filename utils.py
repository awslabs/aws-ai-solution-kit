import os
import requests
import boto3
import botocore
import boto3.s3.transfer as s3transfer
import sys
from urllib.parse import urlparse
import requests
import json

sys.path.append(os.getcwd())
# from modules.timer import Timer
import tarfile

class ModelsRef:
    def __init__(self):
        self.models_ref = {}

    def get_models_ref_dict(self):
        return self.models_ref

    def add_models_ref(self, model_name):
        if model_name in self.models_ref:
            self.models_ref[model_name] += 1
        else:
            self.models_ref[model_name] = 0

    def remove_model_ref(self,model_name):
        if self.models_ref.get(model_name):
            del self.models_ref[model_name]

    def get_models_ref(self, model_name):
        return self.models_ref.get(model_name)

    def get_least_ref_model(self):
        sorted_models = sorted(self.models_ref.items(), key=lambda item: item[1])
        if sorted_models:
            least_ref_model, least_counter = sorted_models[0]
            return least_ref_model,least_counter
        else:
            return None,None

    def pop_least_ref_model(self):
        sorted_models = sorted(self.models_ref.items(), key=lambda item: item[1])
        if sorted_models:
            least_ref_model, least_counter = sorted_models[0]
            del self.models_ref[least_ref_model]
            return least_ref_model,least_counter
        else:
            return None,None

    def get_sorted_models(self, key_list=None):
        print('!!!!!!!!!!!', key_list)
        if key_list is None:
            return sorted(self.models_ref.items(), key=lambda item: item[1])
        else:
            models_ref_tmp = {}
            for key_value in key_list:
                if key_value not in self.models_ref.keys():
                    models_ref_tmp[key_value] = -1
                else:
                    models_ref_tmp[key_value] = self.models_ref[key_value]
            models_sorted_info = sorted(models_ref_tmp.items(), key=lambda item: item[1])
            models_sorted = []
            for model_info in models_sorted_info:
                models_sorted.append(model_info[0])
            return models_sorted

# sd_models_Ref = ModelsRef()
# cn_models_Ref = ModelsRef()
# lora_models_Ref = ModelsRef()
# hyper_models_Ref = ModelsRef()
# embedding_Ref = ModelsRef()

def upload_folder_to_s3(local_folder_path, bucket_name, s3_folder_path):
    s3_client = boto3.client('s3')
    for root, dirs, files in os.walk(local_folder_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            s3_file_path = os.path.join(s3_folder_path, local_file_path)
            s3_client.upload_file(local_file_path, bucket_name, s3_file_path)


def upload_folder_to_s3_by_tar(local_folder_path, bucket_name, s3_folder_path):
    tar_path = f"{local_folder_path}.tar"
    tar_name = os.path.basename(tar_path)
    os.system(f'tar cvf {tar_name} {local_folder_path}')
    # tar = tarfile.open(tar_path, "w:gz")
    # for root, dirs, files in os.walk(local_folder_path):
    #     for file in files:
    #         local_file_path = os.path.join(root, file)
    #         tar.add(local_file_path)
    # tar.close()
    s3_client = boto3.client('s3')
    s3_client.upload_file(tar_name, bucket_name, os.path.join(s3_folder_path, tar_name))
    os.system(f"rm {tar_name}")

def upload_file_to_s3_by_presign_url(local_path, s3_presign_url):
    response = requests.put(s3_presign_url, open(local_path, "rb"))
    response.raise_for_status()

def upload_multipart_files_to_s3_by_signed_url(local_path, signed_urls, part_size):

    with open(local_path, "rb") as f:
        parts = []
        try:
            for i, signed_url in enumerate(signed_urls):
                file_data = f.read(part_size)
                response = requests.put(signed_url, data=file_data)
                etag = response.headers['ETag']
                parts.append({
                    'ETag': etag,
                    'PartNumber': i + 1
                })
                print(f'model upload part {i+1}: {response}')
            return parts
        except Exception as e:
            print(e)


            # response = requests.put(s3_presign_url, open(local_path, "rb"))
    # response.raise_for_status()

def download_folder_from_s3(bucket_name, s3_folder_path, local_folder_path):
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=s3_folder_path):
        obj_dirname = "/".join(os.path.dirname(obj.key).split("/")[1:])
        obj_basename = os.path.basename(obj.key)
        local_sub_folder_path = os.path.join(local_folder_path, obj_dirname)
        if not os.path.exists(local_sub_folder_path):
            os.makedirs(local_sub_folder_path)
        bucket.download_file(obj.key, os.path.join(local_sub_folder_path, obj_basename))  # save to same path


def download_folder_from_s3_by_tar(bucket_name, s3_tar_path, local_tar_path):
    s3_client = boto3.client('s3')
    s3_client.download_file(bucket_name, s3_tar_path, local_tar_path)
    tar_name = os.path.basename(s3_tar_path)
    tar = tarfile.open(local_tar_path, "r")
    tar.extractall()
    tar.close()
    os.system(f"rm {local_tar_path}")


def download_file_from_s3(bucket_name, s3_file_path, local_file_path):
    s3_client = boto3.client('s3')
    s3_client.download_file(bucket_name, s3_file_path, local_file_path)

def upload_file_to_s3(local_file_path, bucket_name, s3_file_path):
    s3_client = boto3.client('s3')
    s3_client.upload_file(local_file_path, bucket_name, s3_file_path)

def get_bucket_name_from_s3_url(s3_path) -> str:
    o = urlparse(s3_path, allow_fragments=False)
    return o.netloc

def get_bucket_name_from_s3_path(s3_path) -> str:
    s3_path = s3_path.lstrip("s3://")
    return s3_path.split("/")[0]

def get_path_from_s3_path(s3_path) -> str:
    s3_path = s3_path.lstrip("s3://")
    return "/".join(s3_path.split("/")[1:])

def fast_upload(session, bucketname, s3dir, filelist, progress_func=None, workers=10):
    # timer = Timer()
    botocore_config = botocore.config.Config(max_pool_connections=workers)
    s3client = session.client('s3', config=botocore_config)
    transfer_config = s3transfer.TransferConfig(
        use_threads=True,
        max_concurrency=workers,
    )
    s3t = s3transfer.create_transfer_manager(s3client, transfer_config)
    # timer.record("init")
    for src in filelist:
        dst = os.path.join(s3dir, os.path.basename(src))
        s3t.upload(
            src, bucketname, dst,
            subscribers=[
                s3transfer.ProgressCallbackInvoker(progress_func),
            ] if progress_func else None,
        )
    s3t.shutdown()  # wait for all the upload tasks to finish
    # timer.record("upload")
    # print(timer.summary())

def save_variable_to_json(variable_name, variable_value, filename='sagemaker_ui.json'):
    data = {}

    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            data = json.load(json_file)

    data[variable_name] = variable_value

    with open(filename, 'w') as json_file:
        json.dump(data, json_file)

def get_variable_from_json(variable_name, filename='sagemaker_ui.json'):
    if not os.path.exists(filename):
        with open(filename, 'w') as json_file:
            json.dump({}, json_file)

    with open(filename, 'r') as json_file:
        data = json.load(json_file)

    variable_value = data.get(variable_name)

    return variable_value

if __name__ == '__main__':
    import sys

    # upload_file_to_s3(sys.argv[1], 'aws-gcr-csdc-atl-exp-us-west-2', sys.argv[2])
    # fast_upload(boto3.Session(), 'aws-gcr-csdc-atl-exp-us-west-2', sys.argv[2], [sys.argv[1]])
    upload_folder_to_s3_by_tar('models/dreambooth/sagemaker_test/samples', 'aws-gcr-csdc-atl-exp-us-west-2',
                               'aigc-webui-test-samples')
    download_folder_from_s3_by_tar('aws-gcr-csdc-atl-exp-us-west-2', 'aigc-webui-test-samples/samples.tar',
                                   'samples.tar')
