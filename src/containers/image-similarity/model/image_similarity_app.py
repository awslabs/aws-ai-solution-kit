import base64
import json
import os
from io import BytesIO

import numpy as np
import onnxruntime
from PIL import Image
import cv2
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

model_path = os.environ['MODEL_PATH']
ort_session = onnxruntime.InferenceSession(model_path + '/image-similarity.onnx')


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
        image_string = urllib2.urlopen(uri).read()
    else:
        image_string = base64.b64decode(body['img'])

    pil_image = Image.open(BytesIO(image_string)).convert('RGB')
    img = np.array(pil_image)[:, :, :3]
    img = cv2.resize(img/255, (448,448))
    img = img.transpose((2,0,1))[np.newaxis,:].astype('float32')
    img_embedding = ort_session.run(['output'], {'input': img})[0][0].round(6).tolist()
    
    result = {'result': img_embedding}
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,GET'
        },

        'body': json.dumps(result)
    }
