import boto3
import json

api_name = 'AI-Solution-Kit-API'
api_description = 'REST APIs for AI Solution Kit'
resource_name = 'image_ocr'
image_url = '295155050487.dkr.ecr.us-west-2.amazonaws.com/aikits:ocr-lite'
stage_name = 'ai-solution-kit-stage'

boto3_session = boto3.session.Session()
region = boto3_session.region_name
account_id = boto3.client('sts').get_caller_identity().get('Account')

api_client = boto3.client('apigateway')
""" :type : pyboto3.apigateway """
iam_client = boto3.client("iam")
""" :type : pyboto3.iam_client """
lambda_client = boto3.client('lambda')
""" :type : pyboto3.lambda_ """


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
    rest_apis = [api for api in api_client.get_rest_apis()['items'] if api_name == api['name']]

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
        api_client.delete_resource(restApiId=api_id, resourceId=api_resources[0]['resource_id'])
    print(api_resource)
    if api_resource.get('resourceMethods') is None or api_resource['resourceMethods'].get('POST') is None:
        # Add a post method to the rest api resource
        api_method = api_client.put_method(
            restApiId=api_id,
            resourceId=api_resource['id'],
            httpMethod='POST',
            authorizationType='NONE'
        )

        # Create role that can be assumed by Lambda
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        if not role_exists(iam_client, 'LambdaRoleToInvokeAISolutionKitAPI'):
            lambda_role = iam_client.create_role(
                RoleName=f"LambdaRoleAISolutionKit-{resource_name}",
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Role for Lambda function to invoke SageMaker endpoints",
            )
        else:
            lambda_role = iam_client.get_role(RoleName='LambdaRoleToInvokeAISolutionKitAPI')

        i = 1
        function_name = f"AISolutionKit-{resource_name}"
        while function_exists(lambda_client, function_name):
            function_name = f"AISolutionKit-{resource_name}" + '-' + str(i)
            i += 1
        print(function_name)
        lambda_config = {
            'FunctionName': function_name,
            'Role': lambda_role["Role"]["Arn"],
            'Timeout': 15,
            'Code': {'ImageUri': image_url},
            'PackageType': 'Image',  # add this parameter
            'MemorySize': 4096
        }

        lambda_function = lambda_client.create_function(**lambda_config)
        print(lambda_function['FunctionArn'])

        lambda_version = lambda_client.meta.service_model.api_version
        lambda_uri = f"arn:aws:apigateway:{region}:lambda:path/{lambda_version}/functions/arn:aws:lambda:{region}:{account_id}:function:{function_name}/invocations"
        print(lambda_uri)
        # Add integrations for mapping SageMaker and Lambda HTTP response codes to API gateway HTTP response codes
        post_integration = api_client.put_integration(
            restApiId=api_id,
            resourceId=api_resource['id'],
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=lambda_uri)
        #
        api_client.put_method_response(
            restApiId=api_id,
            resourceId=api_resource['id'],
            httpMethod='POST',
            statusCode='200',
            # responseModels={'application/json': 'Empty'}
        )
        #
        api_client.put_integration_response(
            restApiId=api_id,
            resourceId=api_resource['id'],
            httpMethod='POST',
            statusCode='200',
            responseTemplates={"application/json": ""}
        )
        #
        api_client.put_integration_response(
            restApiId=api_id,
            resourceId=api_resource['id'],
            httpMethod='POST',
            statusCode='400',
            selectionPattern='Invalid*',
            responseTemplates={"application/json": ""}
        )

        api_client.put_integration_response(
            restApiId=api_id,
            resourceId=api_resource['id'],
            httpMethod='POST',
            statusCode='500',
            selectionPattern='Internal*',
            responseTemplates={"application/json": ""}
        )

        # Add an options method to the rest api
        options_method = api_client.put_method(
            restApiId=api_id,
            resourceId=api_resource['id'],
            httpMethod='OPTIONS',
            authorizationType='NONE'
        )

        # Set the put integration of the OPTIONS method
        api_client.put_integration(
            restApiId=api_id,
            resourceId=api_resource['id'],
            httpMethod='OPTIONS',
            type='MOCK',
            requestTemplates={
                'application/json': ''
            }
        )

        # Set the put method response of the OPTIONS method
        api_client.put_method_response(
            restApiId=api_id,
            resourceId=api_resource['id'],
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': False,
                'method.response.header.Access-Control-Allow-Origin': False,
                'method.response.header.Access-Control-Allow-Methods': False
            },
            responseModels={
                'application/json': 'Empty'
            }
        )

        # Set the put integration response of the OPTIONS method
        api_client.put_integration_response(
            restApiId=api_id,
            resourceId=api_resource['id'],
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': '\'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token\'',
                'method.response.header.Access-Control-Allow-Methods': '\'POST,OPTIONS\'',
                'method.response.header.Access-Control-Allow-Origin': '\'*\''
            },
            responseTemplates={
                'application/json': ''
            }
        )

        if stage_exists(api_client, api_id, stage_name):
            deployment_id = api_client.get_deployments(restApiId=api_id)['items'][-1]['id']
            api_client.get_stage(restApiId=api_id, stageName=stage_name)
            path = [{
                'op': 'add',
                'path': f"{resource_name}",
                'value': resource_name
            }]
            # api_client.flush_stage_cache(restApiId=api_id, stageName=stage_name)
            api_client.update_stage(
                restApiId=api_id,
                stageName=stage_name,
                patchOperations=path
            )
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
            ap
            api_client.create_stage(restApiId=api_id, deploymentId=deployment_id, stageName=stage_name)
            api_client.update_stage(restApiId=api_id, stageName=stage_name)
        else:
            # Deploy to a stage
            api_client.create_deployment(
                restApiId=api_id,
                stageName=stage_name,
            )

        # API gateway needs permissions to invoke the lambda function
        lambda_api_response = lambda_client.add_permission(
            FunctionName=function_name,
            StatementId='api-gateway-invoke',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=f"arn:aws:execute-api:{region}:{account_id}:{api_id}/*/POST/{resource_name}"
        )
        #
        # CN
        api_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/{stage_name}/{resource_name}"
        #
        print("API GATEWAY URL: url = " + f"{api_url}")


def main():
    # resource_name = 'image_ocr'
    # image_url = '295155050487.dkr.ecr.us-west-2.amazonaws.com/aikits:ocr-lite'
    create_api(resource_name='image_ocr_4', image_url='295155050487.dkr.ecr.us-west-2.amazonaws.com/aikits:ocr-lite')


# https://eya34eu24g.execute-api.us-west-2.amazonaws.com/ai-solution-kit-stage/image_ocr_2
# https://eya34eu24g.execute-api.us-west-2.amazonaws.com/ai-solution-kit-stage/image_ocr_3
# https://eya34eu24g.execute-api.us-west-2.amazonaws.com/ai-solution-kit-stage/image_ocr_4

if __name__ == '__main__':
    main()
