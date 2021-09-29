import base64
import json
import os
from io import BytesIO

import numpy as np
import onnxruntime
from PIL import Image
from base64image import Base64Image


def tensor2img(tensor, out_type=np.uint8, min_max=(0, 1)):
    tensor = np.transpose(tensor, (1, 2, 0))
    tensor = np.clip(tensor, *min_max)
    tensor = (tensor - min_max[0]) / (min_max[1] - min_max[0])
    img_np = (tensor * 255.0).round()
    return img_np.astype(out_type)


access_point = os.environ['ACCESS_POINT']
ort_session_x2 = onnxruntime.InferenceSession(access_point + '/Real_ESRGAN_x2.onnx')
ort_session_x4 = onnxruntime.InferenceSession(access_point + '/Real_ESRGAN_x4.onnx')


def lambda_handler(event, context):
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
    scale = int(body.get('scale', 2))
    if scale == 4:
        ort_session = ort_session_x4
    else:
        ort_session = ort_session_x2
    pil_image = base64_image.get_pil_image()
    src = np.asarray(pil_image)[:, :, :3]
    in_frame = (np.ascontiguousarray(np.transpose(src, (2, 0, 1))) / 255).astype('float32')
    ort_inputs = {ort_session.get_inputs()[0].name: np.expand_dims(in_frame, 0)}
    ort_outs = ort_session.run(None, ort_inputs)
    rlt = tensor2img(ort_outs[0][0])
    imo = Image.fromarray(rlt)
    buffered = BytesIO()
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
