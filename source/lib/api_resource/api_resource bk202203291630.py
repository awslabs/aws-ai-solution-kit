import boto3
import json
import requests
import os
from os import environ

api_name = 'AI-Solution-Kit-API'
api_description = 'REST APIs for AI Solution Kit'
resource_name = 'image_ocr'
image_url = '295155050487.dkr.ecr.us-west-2.amazonaws.com/aikits:ocr-lite'
stage_name = 'ai-solution-kit-prod'

boto3_session = boto3.session.Session()
region = boto3_session.region_name
account_id = boto3.client('sts').get_caller_identity().get('Account')

api_client = boto3.client('apigateway')
iam_client = boto3.client("iam")
lambda_client = boto3.client('lambda')


def role_exists(iam, role_name):
    try:
        iam.get_role(RoleName=role_name)
    except iam.exceptions.NoSuchEntityException:
        return False
    else:
        return True


def function_exists(lambdac, function_name):
    try:
        lambdac.get_function(FunctionName=function_name)
    except Exception:
        return False
    else:
        return True


def stage_exists(api_client, api_id, stage_name):
    try:
        api_client.get_stage(restApiId=api_id, stageName=stage_name)
    except Exception:
        return False
    else:
        return True


def create_api(resource_name, image_url):
    if 'REST_API_ID' in environ:
        rest_api = api_client.get_rest_api(restApiId=environ.get('REST_API_ID'))
        print('REST_API_ID found')
    else:
        rest_apis = [api for api in api_client.get_rest_apis()['items'] if api_name == api['name']]
        print('REST_API_ID not found')
        # for api in boto3_api:
        #     print(api['id'])
        #     api_client.delete_rest_api(restApiId=api['id'])
        # for item in api_client.get_rest_apis()['items']:
        #     if 'boto3-rest-api' == item['name']:
        #         api_exists = True
        #         break
        if len(rest_apis) == 0:
            rest_api = api_client.create_rest_api(name=api_name, description=api_description)
        elif len(rest_apis) == 1:
            rest_api = rest_apis[0]
        else:
            pass

    api_id = rest_api['id']
    print(api_id)

    # Get the rest api's root id
    root_resource_id = \
        [api for api in api_client.get_resources(restApiId=api_id, limit=500)['items'] if '/' == api['path']][0]['id']

    api_resources = [resource for resource in api_client.get_resources(restApiId=api_id)['items'] if
                     '/' + resource_name == resource['path']]

    if len(api_resources) == 0:
        # Create an api resource
        api_resource = api_client.create_resource(
            restApiId=api_id,
            parentId=root_resource_id,
            pathPart=resource_name
        )
    else:
        api_resource = api_resources[0]
    print(api_resource)
    # if api_resource.get('resourceMethods') is None or api_resource['resourceMethods'].get('POST') is None:
    #     # Add a post method to the rest api resource
    #     api_method = api_client.put_method(
    #         restApiId=api_id,
    #         resourceId=api_resource['id'],
    #         httpMethod='POST',
    #         authorizationType='NONE'
    #     )

    #     # Create role that can be assumed by Lambda
    #     trust_policy = {
    #         "Version": "2012-10-17",
    #         "Statement": [
    #             {
    #                 "Effect": "Allow",
    #                 "Principal": {
    #                     "Service": "lambda.amazonaws.com"
    #                 },
    #                 "Action": "sts:AssumeRole"
    #             }
    #         ]
    #     }
    #     if not role_exists(iam_client, 'LambdaRoleToInvokeAISolutionKitAPI'):
    #         lambda_role = iam_client.create_role(
    #             RoleName=f"LambdaRoleAISolutionKit-{resource_name}",
    #             AssumeRolePolicyDocument=json.dumps(trust_policy),
    #             Description="Role for Lambda function to invoke SageMaker endpoints",
    #         )
    #     else:
    #         lambda_role = iam_client.get_role(RoleName='LambdaRoleToInvokeAISolutionKitAPI')

    #     i = 1
    #     function_name = f"AISolutionKit-{resource_name}"
    #     while function_exists(lambda_client, function_name):
    #         function_name = f"AISolutionKit-{resource_name}" + '-' + str(i)
    #         i += 1
    #     print(function_name)
    #     lambda_config = {
    #         'FunctionName': function_name,
    #         'Role': lambda_role["Role"]["Arn"],
    #         'Timeout': 15,
    #         'Code': {'ImageUri': image_url},
    #         'PackageType': 'Image',  # add this parameter
    #         'MemorySize': 4096
    #     }

    #     lambda_function = lambda_client.create_function(**lambda_config)
    #     print(lambda_function['FunctionArn'])

    #     lambda_version = lambda_client.meta.service_model.api_version
    #     lambda_uri = f"arn:aws:apigateway:{region}:lambda:path/{lambda_version}/functions/arn:aws:lambda:{region}:{account_id}:function:{function_name}/invocations"
    #     print(lambda_uri)
    #     # Add integrations for mapping SageMaker and Lambda HTTP response codes to API gateway HTTP response codes
    #     post_integration = api_client.put_integration(
    #         restApiId=api_id,
    #         resourceId=api_resource['id'],
    #         httpMethod='POST',
    #         type='AWS_PROXY',
    #         integrationHttpMethod='POST',
    #         uri=lambda_uri)
    #     #
    #     api_client.put_method_response(
    #         restApiId=api_id,
    #         resourceId=api_resource['id'],
    #         httpMethod='POST',
    #         statusCode='200',
    #         # responseModels={'application/json': 'Empty'}
    #     )
    #     #
    #     api_client.put_integration_response(
    #         restApiId=api_id,
    #         resourceId=api_resource['id'],
    #         httpMethod='POST',
    #         statusCode='200',
    #         responseTemplates={"application/json": ""}
    #     )
    #     #
    #     api_client.put_integration_response(
    #         restApiId=api_id,
    #         resourceId=api_resource['id'],
    #         httpMethod='POST',
    #         statusCode='400',
    #         selectionPattern='Invalid*',
    #         responseTemplates={"application/json": ""}
    #     )

    #     api_client.put_integration_response(
    #         restApiId=api_id,
    #         resourceId=api_resource['id'],
    #         httpMethod='POST',
    #         statusCode='500',
    #         selectionPattern='Internal*',
    #         responseTemplates={"application/json": ""}
    #     )

    #     # Add an options method to the rest api
    #     options_method = api_client.put_method(
    #         restApiId=api_id,
    #         resourceId=api_resource['id'],
    #         httpMethod='OPTIONS',
    #         authorizationType='NONE'
    #     )

    #     # Set the put integration of the OPTIONS method
    #     api_client.put_integration(
    #         restApiId=api_id,
    #         resourceId=api_resource['id'],
    #         httpMethod='OPTIONS',
    #         type='MOCK',
    #         requestTemplates={
    #             'application/json': ''
    #         }
    #     )

    #     # Set the put method response of the OPTIONS method
    #     api_client.put_method_response(
    #         restApiId=api_id,
    #         resourceId=api_resource['id'],
    #         httpMethod='OPTIONS',
    #         statusCode='200',
    #         responseParameters={
    #             'method.response.header.Access-Control-Allow-Headers': False,
    #             'method.response.header.Access-Control-Allow-Origin': False,
    #             'method.response.header.Access-Control-Allow-Methods': False
    #         },
    #         responseModels={
    #             'application/json': 'Empty'
    #         }
    #     )

    #     # Set the put integration response of the OPTIONS method
    #     api_client.put_integration_response(
    #         restApiId=api_id,
    #         resourceId=api_resource['id'],
    #         httpMethod='OPTIONS',
    #         statusCode='200',
    #         responseParameters={
    #             'method.response.header.Access-Control-Allow-Headers': '\'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token\'',
    #             'method.response.header.Access-Control-Allow-Methods': '\'POST,OPTIONS\'',
    #             'method.response.header.Access-Control-Allow-Origin': '\'*\''
    #         },
    #         responseTemplates={
    #             'application/json': ''
    #         }
    #     )

    if stage_exists(api_client, api_id, stage_name):
        deployment_id = api_client.get_deployments(restApiId=api_id)['items'][-1]['id']
        api_client.get_stage(restApiId=api_id, stageName=stage_name)
        # path = [{
        #     'op': 'add',
        #     'path': f"{resource_name}",
        #     'value': resource_name
        # }]
        # api_client.flush_stage_cache(restApiId=api_id, stageName=stage_name)
        # api_client.update_stage(
        #     restApiId=api_id,
        #     stageName=stage_name,
        #     patchOperations=path
        # )
        # api_client.create_stage(restApiId=api_id, deploymentId=deployment_id, stageName=stage_name)
        # api_client.update_deployment(
        #     restApiId=api_id,
        #     deploymentId=deployment_id,
        #     patchOperations=path
        # )
        # api_client.update_deployment(restApiId=api_id, deploymentId=deployment_id)
        api_client.create_deployment(
            restApiId=api_id,
            stageName=stage_name,
        )
    else:
        # Deploy to a stage
        api_client.create_deployment(
            restApiId=api_id,
            stageName=stage_name,
        )

    #     # API gateway needs permissions to invoke the lambda function
    #     lambda_api_response = lambda_client.add_permission(
    #         FunctionName=function_name,
    #         StatementId='api-gateway-invoke',
    #         Action='lambda:InvokeFunction',
    #         Principal='apigateway.amazonaws.com',
    #         SourceArn=f"arn:aws:execute-api:{region}:{account_id}:{api_id}/*/POST/{resource_name}"
    #     )
    #     #
    #     # CN
    #     api_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/{stage_name}/{resource_name}"
    #     #
    #     print("API GATEWAY URL: url = " + f"{api_url}")


def delete_api():
    if 'REST_API_ID' in environ:
        rest_api = api_client.get_rest_api(restApiId=environ.get('REST_API_ID'))
        print('REST_API_ID found')
    else:
        rest_apis = [api for api in api_client.get_rest_apis()['items'] if api_name == api['name']]

        if len(rest_apis) == 1:
            rest_api = rest_apis[0]
            
    api_client.delete_rest_api(restApiId=rest_api)
    api_id = rest_api['id']
    print('~~deleted~~')
    print(api_id)



    
# def download_file(url, path):
#     local_filename = path + '/' + url.split('/')[-1]
#     print('downloading', url, local_filename)
#     r = requests.get(url)
#     f = open(local_filename, 'wb')
#     for chunk in r.iter_content(chunk_size=512 * 1024):
#         if chunk:
#             f.write(chunk)
#     f.close()
#     return


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

            for feat in event['ResourceProperties']['Features']:
            #     download_file(url, path)
                create_api(resource_name=feat['resource'], image_url=feat['url'])
            # create_api(resource_name='image_ocr_8', image_url='295155050487.dkr.ecr.us-west-2.amazonaws.com/aikits:ocr-lite')
            result = {
                'StatusCode': '200',
                'Body': {'message': 'success'}
            }
            return json.dumps(result)
        elif 'DELETE' in request_type:
            resourceId = event['PhysicalResourceId'] if 'PhysicalResourceId' in event else event['LogicalResourceId']
            delete_api()
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
