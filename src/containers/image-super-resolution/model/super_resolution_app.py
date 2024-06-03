import base64
import json
import os
from io import BytesIO

import numpy as np
import onnxruntime
from PIL import Image
import base64
from aikits_utils import readimg, lambda_return
import cv2

import GPUtil
cuda_available = True if len(GPUtil.getGPUs()) else False
if cuda_available:
    print(GPUtil.getGPUs()[0].name)
    
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

def tensor2img(tensor, out_type=np.uint8, min_max=(0, 1)):
    tensor = np.transpose(tensor, (1, 2, 0))
    tensor = np.clip(tensor, *min_max)
    tensor = (tensor - min_max[0]) / (min_max[1] - min_max[0])
    img_np = (tensor * 255.0).round()
    return img_np.astype(out_type)


model_path = os.environ['MODEL_PATH']
ort_session_x2 = onnxruntime.InferenceSession(model_path + '/Real_ESRGAN_x2.onnx', providers=[("CUDAExecutionProvider", {"cudnn_conv_algo_search": "HEURISTIC"})] if cuda_available else ['CPUExecutionProvider'])
ort_session_x4 = onnxruntime.InferenceSession(model_path + '/Real_ESRGAN_x4.onnx', providers=[("CUDAExecutionProvider", {"cudnn_conv_algo_search": "HEURISTIC"})] if cuda_available else ['CPUExecutionProvider'])


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
    except:
        return lambda_return(400, 'invalid param')
    
    scale = int(body.get('scale', 2))
    if scale == 4:
        ort_session = ort_session_x4
    else:
        ort_session = ort_session_x2
    h,w,_ = img.shape
    img = cv2.resize(img, (w//scale*scale, h//scale*scale))
    in_frame = (np.ascontiguousarray(np.transpose(img, (2, 0, 1))) / 255).astype('float32')

    ort_inputs = {ort_session.get_inputs()[0].name: np.expand_dims(in_frame, 0)}
    ort_outs = ort_session.run(None, ort_inputs)
    rlt = tensor2img(ort_outs[0][0])
    rlt = cv2.resize(rlt, (w*scale, h*scale))
    imo = Image.fromarray(rlt)
    buffered = BytesIO()
    imo.save(buffered, format="png")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

    result = {'result': img_str}
    return lambda_return(200, json.dumps(result))