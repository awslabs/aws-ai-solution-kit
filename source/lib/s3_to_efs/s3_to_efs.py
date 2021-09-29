import json

import requests


def download_file(url, path):
    local_filename = path + '/' + url.split('/')[-1]
    print('downloading', url, local_filename)
    r = requests.get(url)
    f = open(local_filename, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024):
        if chunk:
            f.write(chunk)
    f.close()
    return


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
        if 'CREATE' in request_type:
            path = event['ResourceProperties']['MountPath']

            for url in event['ResourceProperties']['Objects']:
                download_file(url, path)

            result = {
                'StatusCode': '200',
                'Body': {'message': 'success'}
            }
            return json.dumps(result)
        elif 'DELETE' in request_type:
            resourceId = event['PhysicalResourceId'] if 'PhysicalResourceId' in event else event['LogicalResourceId']

    except Exception as e:
        print("EXCEPTION", e)
        resourceId = event['PhysicalResourceId'] if 'PhysicalResourceId' in event else event['LogicalResourceId']
        send_response(event, context, 'FAILED', resourceId, e)
