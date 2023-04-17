import os
import requests
import boto3
import botocore
import boto3.s3.transfer as s3transfer
import sys

sys.path.append(os.getcwd())
# from modules.timer import Timer
import tarfile


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

def upload_to_s3_by_tar_put(local_path, s3_presign_url):
    tar_name = f"{os.path.basename(local_path)}.tar"
    os.system(f'tar cvf {tar_name} {local_path}')
    response = requests.put(s3_presign_url, open(tar_name, "rb"))
    os.system(f"rm {tar_name}")
    response.raise_for_status()


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


if __name__ == '__main__':
    import sys

    # upload_file_to_s3(sys.argv[1], 'aws-gcr-csdc-atl-exp-us-west-2', sys.argv[2])
    # fast_upload(boto3.Session(), 'aws-gcr-csdc-atl-exp-us-west-2', sys.argv[2], [sys.argv[1]])
    upload_folder_to_s3_by_tar('models/dreambooth/sagemaker_test/samples', 'aws-gcr-csdc-atl-exp-us-west-2',
                               'aigc-webui-test-samples')
    download_folder_from_s3_by_tar('aws-gcr-csdc-atl-exp-us-west-2', 'aigc-webui-test-samples/samples.tar',
                                   'samples.tar')
