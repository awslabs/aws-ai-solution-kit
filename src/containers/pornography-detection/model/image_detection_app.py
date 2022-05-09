import json
import os
from typing import AsyncGenerator
from openvino.inference_engine import IECore
import numpy as np
import openvino
# import time
from PIL import Image
from base64image import Base64Image

model_path = os.environ['MODEL_PATH']
ie = IECore()
model_xml = model_path + '/resnest50_fast_4s2x40d.xml'
model_bin = model_path + '/resnest50_fast_4s2x40d.bin'
net = ie.read_network(model=model_xml, weights=model_bin)
input_blob = next(iter(net.inputs))
out_blob = next(iter(net.outputs))
net.batch_size = 1

# Read and pre-process input images
n, c, h, w = net.inputs[input_blob].shape
exec_net = ie.load_network(network=net, device_name='CPU')

def handler(event, context):
    if 'body' not in event:
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*'
            }
        }
    if isinstance(event['body'], str):
        body = json.loads(event['body'])
    else:
        body = event['body']

    if 'url' in body:
        uri = body['url']
        base64_image = Base64Image.from_uri(uri)
    else:
        base64_image = Base64Image.from_base64_image_string(body['img'])

    pil_image = base64_image.get_pil_image()

    raw_img = np.array(pil_image.resize((512,512)))[:,:,:3]/255.0
    #raw_img = (raw_img-np.array([0.485, 0.456, 0.406]))/np.array([0.229, 0.224, 0.225])
    raw_img = np.squeeze(raw_img.transpose((2,0,1))).astype('float32')
    y_hat = exec_net.infer(inputs={input_blob: raw_img})
    y_hat = y_hat['output'][0]
    y_hat = np.exp(y_hat)/sum(np.exp(y_hat))

    res = {
        "normal":float(y_hat[0]),
        "sexy":float(y_hat[1]),
        "porn":float(y_hat[2])
    }
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,GET'
        },

        'body': json.dumps(res)
    }
