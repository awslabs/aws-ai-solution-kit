from gevent import pywsgi
import flask
import json
import base64
import json
import os
from io import BytesIO

import numpy as np
from os import environ
from PIL import Image
import cv2
from aikits_utils import readimg
import onnxruntime
import time

app = flask.Flask(__name__)

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

ort_session = onnxruntime.InferenceSession(os.environ['MODEL_PATH'] + 'chroma-key.onnx', providers=['CUDAExecutionProvider'])
_ = ort_session.run(None, {"input": np.zeros([1, 3, 64, 64], dtype='float32')})

print('load success')
@app.route('/ping', methods=['GET'])
def ping():
    """
    Determine if the container is working and healthy. In this sample container, we declare
    it healthy if we can load the model successfully.
    :return:
    """
    health = False
    try:
        health = ort_session is not None     # You can insert a health check here
    except:
        pass
    status = 200 if health else 404
    return flask.Response(response='\n', status=status, mimetype='application/json')

@app.route('/invocations', methods=['POST'])
def transformation():
    """
    Do an inference on a single batch of data. In this sample server, we take image data as base64 formation,
    decode it for internal use and then convert the predictions to json format
    :return:
    """
    if flask.request.content_type == 'application/json':
        request_body = flask.request.data.decode('utf-8')
        body = json.loads(request_body)
        if "body" in body:
            body = body["body"]
        if 'url' in body and 'img' in body:
            return lambda_return(400, '`url` and `img` cannot be used at the same time')
        img = read_img(body)
        if isinstance(img, str):
            return lambda_return(400, f'`parameter `{img}` illegal')
        pil_image = img
        src = np.array(img)[:, :, :3]
    else:
        return flask.Response(
            response='Object detector only supports application/json data',
            status=415, mimetype='application/json')

    output_size = 1024
    h, w = src.shape[:2]
    new_h, new_w = output_size, output_size
    img = cv2.resize(src, (new_w,new_h))/255
    img = img-0.5 
    in_frame = (np.ascontiguousarray(np.transpose(img, (2, 0, 1)))).astype('float32')
    ort_inputs = {ort_session.get_inputs()[0].name: np.expand_dims(in_frame, 0)}

    ort_outs = ort_session.run(None, ort_inputs)
    result = ort_outs[0][0][0]
    result = cv2.resize(result, (w,h))
    ma = result.max()
    mi = result.min()
    result = ((result-mi)/(ma-mi))
    result = np.clip(result, 0.02, 0.98)
    output = (result - result.min()) / (result.max() - result.min())

    im = Image.fromarray((output * 255).astype('uint8'))
    buffered = BytesIO()
    im.save(buffered, format="png")

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

server = pywsgi.WSGIServer(('0.0.0.0', 8080), app)
server.serve_forever()