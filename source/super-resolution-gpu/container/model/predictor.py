from gevent import pywsgi
import os
import json
import torch
import torch.neuron
from base64image import Base64Image
import numpy as np
import cv2
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import flask

app = flask.Flask(__name__)

class SuperResolutionService(object):
    # class attributes
    def __init__(self):
        """
        Get the model object for this instance, loading it if it's not already loaded.
        :return:
        """
        self.models = [torch.jit.load('Real_ESRGAN_x2.pt'),
                      torch.jit.load('Real_ESRGAN_x4.pt')]
        self.thread_pool = ThreadPoolExecutor(max_workers=4)

    def __call__(self, img, scale):
        def do(idx_patch):
            idx, patch = idx_patch
            y_hat = model(patch)
            return (idx, y_hat)
        img_shape = img.shape
        shave = 10
        if scale == 2:
            model_shape=(144, 144)
        else:
            model_shape=(72, 72)
        input_shape = (img_shape[0]//(model_shape[0]-shave)*(model_shape[0]-shave) + model_shape[0],
                       img_shape[1]//(model_shape[1]-shave)*(model_shape[1]-shave) + model_shape[1])
        pad_top = (input_shape[0] - img_shape[0])//2
        pad_bottom = input_shape[0] - img_shape[0] - pad_top
        pad_left = (input_shape[1] - img_shape[1])//2
        pad_right = input_shape[1] - img_shape[1] - pad_left
        img = cv2.copyMakeBorder(img, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_REFLECT)
        patches = []
        for i in range(0, img_shape[0], model_shape[0]-shave):
            for j in range(0, img_shape[1], model_shape[1]-shave):
                patch = (slice(i, i+model_shape[0]), slice(j, j+model_shape[1]))
                patches.append((
                    patch[0], patch[1],
                    np.expand_dims((np.transpose(img[patch[0], patch[1],...], (2, 0, 1)))/255, 0).astype('float32')
                ))
        if scale == 4:
            model = self.models[1]
        else:
            model = self.models[0]
        temps = []
        for i, patch in enumerate(patches):
            temps.append(self.thread_pool.submit(do, (i, torch.from_numpy(patch[2]))))
        y = np.zeros((input_shape[0]*scale, input_shape[1]*scale, 3)).astype('uint16')
        weight = np.zeros(y.shape).astype('uint16')
        for task in as_completed(temps):
            i, rlt = task.result()
            rlt = self.tensor2img(rlt)
            y[slice(patches[i][0].start * scale,
                    patches[i][0].stop * scale),
              slice(patches[i][1].start * scale,
                    patches[i][1].stop * scale),...] += rlt
            weight[slice(patches[i][0].start * scale,
                         patches[i][0].stop * scale),
                   slice(patches[i][1].start * scale,
                         patches[i][1].stop * scale),...] += 1
        y = y / weight
        y = y[pad_top*scale:y.shape[0]-pad_bottom*scale,
              pad_left*scale:y.shape[1]-pad_right*scale].astype('uint8')
        return y
    def tensor2img(self, tensor, out_type=np.uint8, min_max=(0, 1)):
        tensor = tensor.squeeze().clamp_(*min_max)  # clamp
        tensor = (tensor - min_max[0]) / (min_max[1] - min_max[0])  # to range [0,1]
        img_np = tensor.numpy()
        img_np = np.transpose(img_np[:, :, :], (1, 2, 0))
        img_np = (img_np * 255.0).round()
        return img_np.astype(out_type)
model = SuperResolutionService()
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
        health = model is not None     # You can insert a health check here
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
        request_body = json.loads(request_body)
        if 'url' in request_body:
            uri = request_body['url']
            base64_image = Base64Image.from_uri(uri)
        else:
            base64_image = Base64Image.from_base64_image_string(request_body['img'])
        scale = int(request_body.get('scale', 2))
    else:
        return flask.Response(
            response='Object detector only supports application/json data',
            status=415,
            mimetype='text/plain')

    
    img = np.asarray(base64_image.get_pil_image())[:,:,:3]
    # pre-process
    y = model(img, scale)
    retval, buffer_img= cv2.imencode('.png', y[:,:,::-1])
    data = base64.b64encode(buffer_img)
    result = {'result': data.decode('utf8')}

    return flask.Response(response=json.dumps(result), status=200, mimetype='application/json')
    
server = pywsgi.WSGIServer(('0.0.0.0', 8080), app)
server.serve_forever()