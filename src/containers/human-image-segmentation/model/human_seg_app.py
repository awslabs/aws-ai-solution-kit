import base64
import json
import os
from io import BytesIO

import numpy as np
import onnxruntime
from PIL import Image
from aikits_utils import readimg, lambda_return

import GPUtil
cuda_available = True if len(GPUtil.getGPUs()) else False
if cuda_available:
    print(GPUtil.getGPUs()[0].name)
    
model_path = os.environ['MODEL_PATH']
ort_session = onnxruntime.InferenceSession(model_path + '/humanseg_720.onnx', providers=['CUDAExecutionProvider'] if cuda_available else ['CPUExecutionProvider'])
_ = ort_session.run(None, {"input": np.zeros([1, 3, 64, 64], dtype='float32')})
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
        pil_image = img
        src = np.array(img)[:, :, :3]
    except:
        return lambda_return(400, 'invalid param')

    output_size = 720
    h, w = src.shape[:2]
    new_h, new_w = output_size, output_size * w / h
    new_h, new_w = int(new_h), int(new_w)
    img = np.array(pil_image.resize((new_w, new_h)))
    img = img / np.max(img)
    img[:, :, 0] = (img[:, :, 0] - 0.485) / 0.229
    img[:, :, 1] = (img[:, :, 1] - 0.456) / 0.224
    img[:, :, 2] = (img[:, :, 2] - 0.406) / 0.225
    in_frame = (np.ascontiguousarray(np.transpose(img, (2, 0, 1)))).astype('float32')
    ort_inputs = {ort_session.get_inputs()[0].name: np.expand_dims(in_frame, 0)}

    ort_outs = ort_session.run(None, ort_inputs)

    ma = np.max(ort_outs[0][:, 0, :, :])
    mi = np.min(ort_outs[0][:, 0, :, :])
    dn = (ort_outs[0][:, 0, :, :] - mi) / (ma - mi)
    im = Image.fromarray((dn[0] * 255).astype('uint8'))
    imo = im.resize((src.shape[1], src.shape[0]), resample=Image.BILINEAR)

    buffered = BytesIO()
    if 'type' in body and body['type'] == 'foreground':
        im_rgba = pil_image.copy()
        im_rgba.putalpha(imo)
        im_rgba.save(buffered, format="png")
    else:
        imo.save(buffered, format="png")
        
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    result = {'result': img_str}
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
