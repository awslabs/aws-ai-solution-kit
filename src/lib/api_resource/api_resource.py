# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0


import boto3
import json
import requests
import os
import time
from os import environ

stage_name = environ.get('STAGE_NAME')
api_id = environ.get('REST_API_ID')
api_client = boto3.client('apigateway')

def stage_exists(api_client, api_id, stage_name):
    try:
        api_client.get_stage(restApiId=api_id, stageName=stage_name)
    except Exception:
        return False
    else:
        return True


def create_deployment(feature_name):
    if stage_exists(api_client, api_id, stage_name):
        deployment_id = api_client.get_deployments(restApiId=api_id)['items'][-1]['id']
        api_client.get_stage(restApiId=api_id, stageName=stage_name)
        api_client.create_deployment(
            restApiId=api_id,
            stageName=stage_name,
        )
        # api_client.update_stage(restApiId=api_id, stageName=stage_name)
    else:
        # Deploy to a stage
        api_client.create_deployment(
            restApiId=api_id,
            stageName=stage_name,
        )

def delete_api(feature_name):

    if stage_exists(api_client, api_id, stage_name):
        api_resources = [resource for resource in api_client.get_resources(restApiId=api_id)['items'] if
                        '/' + feature_name == resource['path']]

        if len(api_resources) == 1:
            api_resource = api_resources[0]
            api_client.delete_resource(restApiId=api_id, resourceId=api_resources[0]['resource_id'])
        api_client.create_deployment(
            restApiId=api_id,
            stageName=stage_name,
        )

def send_response(event, context, responseStatus, resourceId, reason):
    responseUrl = event['ResponseURL']
    responseBody = {}
    responseBody['Status'] = responseStatus
    responseBody['PhysicalResourceId'] = resourceId
    responseBody['StackId'] = event['StackId']
    responseBody['RequestId'] = event['RequestId']
    responseBody['LogicalResourceId'] = event['LogicalResourceId']
    responseBody['Reason'] = reason

    json_responseBody = json.dumps(responseBody)

    headers = {
        'content-type': '',
        'content-length': str(len(json_responseBody))
    }
    response = requests.put(responseUrl,
                            data=json_responseBody,
                            headers=headers)
    return response


def lambda_handler(event, context):
    try:
        request_type = event['RequestType'].upper() if ('RequestType' in event) else ""
        # fix for update
        if 'CREATE' in request_type or 'UPDATE' in request_type:
            if 'updateType' in event['ResourceProperties'] and event['ResourceProperties']['updateType'] == 'update':
                delete_api(feature_name=event['ResourceProperties']['featureName'])
            
            create_deployment(feature_name=event['ResourceProperties']['featureName'])
            result = {
                'StatusCode': '200',
                'Body': {'message': 'create success'}
            }
            return json.dumps(result)
        elif 'DELETE' in request_type:
            resourceId = event['PhysicalResourceId'] if 'PhysicalResourceId' in event else event['LogicalResourceId']
            delete_api(feature_name=event['ResourceProperties']['featureName'])
            if 'ResponseURL' in event:
                send_response(event, context, 'SUCCESS', resourceId, request_type + ' success')

            result = {
                'StatusCode': '200',
                'Body': {'message': 'delete success'}
            }
            return json.dumps(result)
    except Exception as e:
        result = {
            'StatusCode': '500',
            'Body': {'message': str(e)}
        }
        print(result)
        resourceId = event['PhysicalResourceId'] if 'PhysicalResourceId' in event else event['LogicalResourceId']
        if 'ResponseURL' in event:
            send_response(event, context, 'FAILED', resourceId, request_type + ' Failed')
        return json.dumps(result)
