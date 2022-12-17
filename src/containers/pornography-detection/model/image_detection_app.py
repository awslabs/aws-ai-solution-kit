import json
import os
import cv2
import onnxruntime
import numpy as np
# import time
from PIL import Image
from aikits_utils import readimg, lambda_return

import GPUtil
cuda_available = True if len(GPUtil.getGPUs()) else False
if cuda_available:
    print(GPUtil.getGPUs()[0].name)
    
model_path = os.environ['MODEL_PATH']

ort_session = onnxruntime.InferenceSession(model_path + '/resnest50_fast_4s2x40d.onnx', providers=['CUDAExecutionProvider'] if cuda_available else ['CPUExecutionProvider'])

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

        raw_img = cv2.resize(img, (512,512))/255
    except:
        return lambda_return(400, 'invalid param')

    #raw_img = (raw_img-np.array([0.485, 0.456, 0.406]))/np.array([0.229, 0.224, 0.225])
    
    img = raw_img.transpose((2,0,1))[np.newaxis,:].astype('float32')
    y_hat = ort_session.run(['output'], {'input': img})[0][0]
    y_hat = np.exp(y_hat)/sum(np.exp(y_hat))

    res = {
        "normal":float(y_hat[0]),
        "sexy":float(y_hat[1]),
        "porn":float(y_hat[2])
    }
    return lambda_return(200, json.dumps(res))
