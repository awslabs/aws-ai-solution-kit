import json
import boto3
import os
import sys
import pandas as pd
import base64
import argparse
import copy
import logging
import tempfile

from parser_factory import ParserFactory

def check_include_file_type(file_info, include_file_types):
    """
    Check if the file type is included in the include_file_types list.

    :param file_info: file info
    :param include_file_types: list of file types to include

    """
    file_type = file_info['file_type']

    if file_type in include_file_types:
        return True
    else:
        return False

def organize_table_info(table_name, result_bucket_name, original_bucket_name, file_info, columns, file_category):

    description = json.dumps(file_info, ensure_ascii=False)
    s3_location = f"s3://{result_bucket_name}/parser_results/{table_name}/"
    input_format = 'org.apache.hadoop.mapred.TextInputFormat'
    output_format = 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
    table_type = 'EXTERNAL_TABLE'
    serde_info = {'SerializationLibrary': 'org.apache.hadoop.hive.serde2.OpenCSVSerde',
                'Parameters': {'field.delim': ','}}
    parameters = {'originalFileBucketName': original_bucket_name,
                  'originalFileType': file_info['file_type'],
                  'originalFilePath': file_info['file_path'],
                  'originalFileSample': ', '.join(file_info['sample_files'][:10]),
                  'originalFileCategory': file_category,
                  'Unstructured': 'true',
                  'classification': 'csv'}
    glue_table_columns = [{'Name': 'index', 'Type': 'string'}]
    for column in columns:
        glue_table_columns.append({'Name': column, 'Type': 'string'})
    
    glue_table_info = {
        'Name': table_name,
        'Description': description,
        'StorageDescriptor': {
            'Columns': glue_table_columns,
            'Location': s3_location,
            'InputFormat': input_format,
            'OutputFormat': output_format,
            'SerdeInfo': serde_info
        },
        'PartitionKeys': [],
        'TableType': table_type,
        'Parameters': parameters
    }
    return glue_table_info

def batch_process_files(s3_client, bucket_name, file_info, file_category):
    """
    Batch process files in a folder with the same schema.

    :param bucket_name: S3 bucket name
    :param file_info: file info

    Sample file_info:
    {
        "file_type": ".jpeg",
        "file_path": "test_images/human_faces",
        "sample_files": [
            "1"
        ]
    }

    """
    file_contents = {}

    file_type = file_info['file_type']
    file_path = file_info['file_path']
    sample_files = file_info['sample_files']

    if file_category == 'detection_files':
        
        parser = ParserFactory.create_parser(file_type=file_type, s3_client=s3_client)

        for sample_file in sample_files:
            object_key = f"{file_path}/{sample_file}{file_type}"
            file_content = parser.load_content(bucket_name, object_key)
            file_contents[f"{sample_file}"] = file_content

    elif file_category == 'include_files':
        for sample_file in sample_files:
            file_contents[f"{sample_file}"] = ['This file is marked as Contains-PII.']
    
    elif file_category == 'exclude_files':
        for sample_file in sample_files:
            file_contents[f"{sample_file}"] = ['This file is marked as Non-PII.']
            
    return file_contents

def process_file(parser, bucket_name, object_key):
    """
    Process a single file.
    """
    file_content = parser.load_content(bucket_name, object_key)

    json_format_content = {}
    json_format_content[f"{object_key}"] = file_content
    
    return json_format_content

def create_glue_table(glue_client, database_name, table_name, glue_table_info):

    # Check if table exists
    try:
        response = glue_client.get_table(
            DatabaseName=database_name,
            Name=table_name
        )
        print(f"Table '{table_name}' exists in database '{database_name}'. Updating table...")
        response = glue_client.update_table(
            DatabaseName=database_name,
            TableInput=glue_table_info
        )
    except glue_client.exceptions.EntityNotFoundException:
        print(f"Table '{table_name}' does not exist in database '{database_name}'. Creating table...")
        response = glue_client.create_table(
            DatabaseName=database_name,
            TableInput=glue_table_info
        )

    print(response)

def main(param_dict):
    original_bucket_name = param_dict['SourceBucketName']
    crawler_result_bucket_name = param_dict['ResultBucketName']
    region_name = param_dict['RegionName']

    crawler_result_object_key = f"crawler_results/{original_bucket_name}_info.json"
    destination_database = f"SDPS-unstructured-{original_bucket_name}"

    s3_client = boto3.client('s3', region_name = region_name)
    glue_client = boto3.client('glue', region_name = region_name)

    # 1. Create a Glue Database
    try:
        response = glue_client.create_database(
            DatabaseInput={
                'Name': destination_database
            }
        )
    except glue_client.exceptions.AlreadyExistsException:
        print(f"Database '{destination_database}' already exists. Skipping database creation...")

    # 2. Download the crawler result from S3 and 
    with tempfile.NamedTemporaryFile(mode='w') as temp:
        temp_file_path = temp.name
        s3_client.download_file(Bucket=crawler_result_bucket_name, Key=crawler_result_object_key, Filename=temp_file_path)
        bucket_info = json.load(open(temp_file_path, 'r'))

    
    # 4. Batch process files in same folder with same type
    original_file_bucket_name = bucket_info['bucket_name']
    for file_category in ['detection_files', 'include_files', 'exclude_files']:
        files = bucket_info[file_category]
        for file_path, file_info in files.items():
            print(f"Processing {file_path}...")
            file_contents = batch_process_files(s3_client, original_file_bucket_name, file_info, file_category)

            # convert file_contents to dataframe
            df = pd.DataFrame.from_dict(file_contents, orient='index')
            df = df.transpose()
            columns = df.columns.tolist()

            # dump file_info into string and encode in base64 as filename
            table_name = file_path.replace('/', '_')
            table_name = table_name.replace('.', '_')
            table_name = original_file_bucket_name + '_' + table_name

            # save to csv and upload to s3
            with tempfile.NamedTemporaryFile(mode='w') as temp:
                csv_file_path = temp.name
                df.to_csv(csv_file_path, header=False)
                s3_client.upload_file(csv_file_path, crawler_result_bucket_name, f"parser_results/{table_name}/result.csv")

            glue_table_info = organize_table_info(table_name, crawler_result_bucket_name, original_file_bucket_name, file_info, columns, file_category)
            create_glue_table(glue_client, destination_database, table_name, glue_table_info)

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(...)
    parser.add_argument('--SourceBucketName', type=str, default='icyxu-glue-assets-member-a',
                        help='crawler_result_bucket_name')
    parser.add_argument('--ResultBucketName', type=str, default='icyxu-glue-assets-member-a',
                        help='crawler_result_bucket_name')
    parser.add_argument('--RegionName', type=str, default='us-west-2',
                        help='crawler_result_object_key')

    args, _ = parser.parse_known_args()
    param_dict = copy.copy(vars(args))
    
    main(param_dict)
