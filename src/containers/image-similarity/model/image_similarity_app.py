import json
import os

import numpy as np
import onnxruntime
import cv2
from aikits_utils import readimg, lambda_return

model_path = os.environ['MODEL_PATH']
ort_session = onnxruntime.InferenceSession(model_path + '/image-similarity.onnx')

def get_cos_similar(v1, v2):
    num = float(np.dot(v1, v2))
    denom = np.linalg.norm(v1) * np.linalg.norm(v2)
    return 0.5 + 0.5 * (num / denom)
    
def get_embedding(img):
    img = cv2.resize(img/255, (448,448))
    img = img.transpose((2,0,1))[np.newaxis,:].astype('float32')
    img_embedding = ort_session.run(['output'], {'input': img})[0][0]
    return img_embedding

def handler(event, context):
    try:
        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event['body']
        if ('url_1' in body and 'img_1' in body) or ('url_2' in body and 'img_2' in body) or ('url' in body and 'img' in body):
            return lambda_return(400, '`url` and `img` cannot be used at the same time')
        if 'url_1' in body:
            task = 'multi'
            inputs = readimg(body, ['url_1', 'url_2'])
            img_1, img_2 = inputs['url_1'], inputs['url_2']
        elif 'img_1' in body:
            task = 'multi'
            inputs = readimg(body, ['img_1', 'img_2'])
            img_1, img_2 = inputs['img_1'], inputs['img_2']
        elif 'url' in body:
            task = 'single'
            inputs = readimg(body, ['url'])
            img = inputs['url']
        else:
            task = 'single'
            inputs = readimg(body, ['img'])
            img = inputs['img']
        for k, v in inputs.items():
            if v is None:
                return lambda_return(400, f'`parameter {k} is not available')
    except:
        return lambda_return(400, 'invalid param')
    
    if task == 'single':
        img_embedding = get_embedding(img).round(6).tolist()
        result = {'result': img_embedding}
    else:
        img_embedding_1 = get_embedding(img_1)
        img_embedding_2 = get_embedding(img_2)
        result = {'similarity': float(get_cos_similar(img_embedding_1, img_embedding_2).round(6))}
    return lambda_return(200, json.dumps(result))