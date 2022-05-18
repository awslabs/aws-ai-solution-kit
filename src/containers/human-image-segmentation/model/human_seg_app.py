import base64
import json
import os
from io import BytesIO

import numpy as np
import onnxruntime
from PIL import Image
from base64image import Base64Image

model_path = os.environ['MODEL_PATH']
ort_session = onnxruntime.InferenceSession(model_path + '/humanseg_720.onnx')


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
    src = np.asarray(pil_image)[:, :, :3]
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
