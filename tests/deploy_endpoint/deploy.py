import boto3

sagemaker = boto3.client('sagemaker')

try:
    list_results = sagemaker.list_endpoints()
    endpoints_info = list_results['Endpoints']
    for ep_info in endpoints_info:
        print(ep_info['EndpointName'])
    print(f"list results are {endpoints_info}")
except Exception as e:
    print(e)
    print('Unable to describe eps.')
    raise(e)
