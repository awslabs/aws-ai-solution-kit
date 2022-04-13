import boto3
import json
import requests
import os
import time
from os import environ

stage_name = environ.get('STAGE_NAME')
api_client = boto3.client('apigateway')

def stage_exists(api_client, api_id, stage_name):
    try:
        api_client.get_stage(restApiId=api_id, stageName=stage_name)
    except Exception:
        return False
    else:
        return True


def create_api(feature_name):
    if 'REST_API_ID' in environ:
        rest_api = api_client.get_rest_api(restApiId=environ.get('REST_API_ID'))
        print('REST_API_ID found')

    api_id = rest_api['id']
    print(api_id)
    
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
    print('~~deleting~~')
    if 'REST_API_ID' in environ:
        rest_api = api_client.get_rest_api(restApiId=environ.get('REST_API_ID'))
        api_id = rest_api['id']
        print('REST_API_ID found')
        if stage_exists(api_client, api_id, stage_name):
            print('update stage')
            # path = [{
            #     'op': 'remove',
            #     'path': f"/{feature_name}/POST",
            #     'value': feature_name
            # }]
            # api_client.update_stage(restApiId=api_id, stageName=stage_name, patchOperations=path)
            api_resources = [resource for resource in api_client.get_resources(restApiId=api_id)['items'] if
                            '/' + feature_name == resource['path']]

            if len(api_resources) == 1:
                api_resource = api_resources[0]
                api_client.delete_resource(restApiId=api_id, resourceId=api_resources[0]['resource_id'])
            api_client.create_deployment(
                restApiId=api_id,
                stageName=stage_name,
            )
            print('updateD.. stage')
        # api_client.delete_rest_api(restApiId=rest_api)
    # api_id = rest_api['id']
    print('~~deleted~~')
    # print(api_id)

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
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(event)
    print(os.environ.items())
    # create_api(resource_name='image_ocr_1', image_url='295155050487.dkr.ecr.us-west-2.amazonaws.com/aikits:ocr-lite')
    # create_api(resource_name='image_ocr_2', image_url='295155050487.dkr.ecr.us-west-2.amazonaws.com/aikits:ocr-lite')
    try:
        print('====================')
        request_type = event['RequestType'].upper() if ('RequestType' in event) else ""
        # fix for update
        if 'CREATE' in request_type or 'UPDATE' in request_type:
            # path = event['ResourceProperties']['MountPath']

            create_api(feature_name=event['ResourceProperties']['featureName'])
            result = {
                'StatusCode': '200',
                'Body': {'message': 'success'}
            }
            return json.dumps(result)
        elif 'DELETE' in request_type:
            resourceId = event['PhysicalResourceId'] if 'PhysicalResourceId' in event else event['LogicalResourceId']
            delete_api(feature_name=event['ResourceProperties']['featureName'])
            if 'ResponseURL' in event:
                send_response(event, context, 'SUCCESS', resourceId, None)


            result = {
                'StatusCode': '200',
                'Body': {'message': 'success'}
            }
            return json.dumps(result)
        print(result)
        print('====================')
    except Exception as e:
        print("EXCEPTION", e)
        result = {
            'StatusCode': '500',
            'Body': {'message': str(e)}
        }
        print(result)
        resourceId = event['PhysicalResourceId'] if 'PhysicalResourceId' in event else event['LogicalResourceId']
        if 'ResponseURL' in event:
            send_response(event, context, 'FAILED', resourceId, None)
        return json.dumps(result)
