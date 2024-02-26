import json
import time
from os import environ

import cv2
from aikits_utils import readimg, lambda_return

from main import structure_predict

if environ["MODEL_PATH"] is None:
    environ["MODEL_PATH"] = "/opt/program/model/"

def read_img(body):
    if 'url' in body:
        inputs = readimg(body, ['url'])
        img = inputs['url']
    else:
        inputs = readimg(body, ['img'])
        img = inputs['img']
    for k, v in inputs.items():
        if v is None:
            return str(k)
    return img

def handler(event, context):
    start_time = time.time()
    if "body" not in event:
        return lambda_return(400, 'invalid param')
    try:
        if isinstance(event["body"], str):
            body = json.loads(event["body"])
        else:
            body = event["body"]
        if 'url' in body and 'img' in body:
            return lambda_return(400, '`url` and `img` cannot be used at the same time')
        img = read_img(body)
        if isinstance(img, str):
            return lambda_return(400, f'`parameter `{img}` illegal')
        img = img[:,:,::-1]
    except:
        return lambda_return(400, 'invalid param')
    lang = body.get("lang", 'ch')
    output_format = body.get("output_format", 'json')
    table_format = body.get("table_format", 'html')
    result = structure_predict(img, lang, output_format, table_format)
    if 'duration' in body and body['duration']:
        result.append({"duration": time.time() - start_time})
    return lambda_return(200, json.dumps(result))

