from gevent import pywsgi
import flask
import json
import time
from os import environ

import cv2
from aikits_utils import readimg

from main import *

app = flask.Flask(__name__)


if environ["MODEL_NAME"] is None:
    environ["MODEL_NAME"] = "advanced"

if environ["MODEL_PATH"] is None:
    environ["MODEL_PATH"] = "/opt/ml/model/model/"

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

def sorted_boxes(dt_boxes):
    """
    Sort text boxes in order from top to bottom, left to right
    args:
        dt_boxes(array):detected text boxes with shape [4, 2]
    return:
        sorted boxes(array) with shape [4, 2]
    """
    num_boxes = dt_boxes.shape[0]
    sorted_boxes = sorted(dt_boxes, key=lambda x: (x[0][1], x[0][0]))
    _boxes = list(sorted_boxes)

    for i in range(num_boxes - 1):
        if abs(_boxes[i + 1][0][1] - _boxes[i][0][1]) < 10 and (
            _boxes[i + 1][0][0] < _boxes[i][0][0]
        ):
            tmp = _boxes[i]
            _boxes[i] = _boxes[i + 1]
            _boxes[i + 1] = tmp
    return _boxes


class TextSystem:
    def __init__(self):
        self.text_detector = TextDetector()
        self.text_recognizer = TextRecognizer()
        self.drop_score = 0.3
        self.text_classifier = TextClassifier()

    def get_rotate_crop_image(self, img, points):
        """
        img_height, img_width = img.shape[0:2]
        left = int(np.min(points[:, 0]))
        right = int(np.max(points[:, 0]))
        top = int(np.min(points[:, 1]))
        bottom = int(np.max(points[:, 1]))
        img_crop = img[top:bottom, left:right, :].copy()
        points[:, 0] = points[:, 0] - left
        points[:, 1] = points[:, 1] - top
        """
        img_crop_width = int(
            max(
                np.linalg.norm(points[0] - points[1]),
                np.linalg.norm(points[2] - points[3]),
            )
        )
        img_crop_height = int(
            max(
                np.linalg.norm(points[0] - points[3]),
                np.linalg.norm(points[1] - points[2]),
            )
        )
        pts_std = np.float32(
            [
                [0, 0],
                [img_crop_width, 0],
                [img_crop_width, img_crop_height],
                [0, img_crop_height],
            ]
        )
        M = cv2.getPerspectiveTransform(points, pts_std)
        dst_img = cv2.warpPerspective(
            img,
            M,
            (img_crop_width, img_crop_height),
            borderMode=cv2.BORDER_REPLICATE,
            flags=cv2.INTER_CUBIC,
        )
        dst_img_height, dst_img_width = dst_img.shape[0:2]
        if dst_img_height * 1.0 / dst_img_width >= 1.5:
            dst_img = np.rot90(dst_img)
        return dst_img

    def __call__(self, img):
        ori_im = img.copy()
        dt_boxes = self.text_detector(img)
        if dt_boxes is None:
            return None, None
        img_crop_list = []

        dt_boxes = sorted_boxes(dt_boxes)

        for bno in range(len(dt_boxes)):
            tmp_box = copy.deepcopy(dt_boxes[bno])
            img_crop = self.get_rotate_crop_image(ori_im, tmp_box)
            img_crop_list.append(img_crop)
        img_crop_list, angle_list = self.text_classifier(img_crop_list)

        rec_res = self.text_recognizer(img_crop_list)
        filter_boxes, filter_rec_res = [], []
        for box, rec_reuslt in zip(dt_boxes, rec_res):
            text, score = rec_reuslt
            if score >= self.drop_score:
                filter_boxes.append(box)
                filter_rec_res.append(rec_reuslt)
        return filter_boxes, filter_rec_res


text_sys = TextSystem()

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
        health = text_sys is not None     # You can insert a health check here
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
    start_time = time.time()
    if flask.request.content_type == 'application/json':
        request_body = flask.request.data.decode('utf-8')
        body = json.loads(request_body)
        if "body" in body:
            body = body["body"]
        try:
            if 'url' in body and 'img' in body:
                return flask.Response(
                    response='`url` and `img` cannot be used at the same time',
                    status=400, mimetype='application/json')
            img = read_img(body)
            if isinstance(img, str):
                return flask.Response(
                    response=f'`parameter `{img}` illegal',
                    status=400, mimetype='application/json')
            img = img[:,:,::-1]
        except:
            return flask.Response(
                    response='invalid param',
                    status=400, mimetype='application/json')
    else:
        return flask.Response(
            response='Object detector only supports application/json data',
            status=415, mimetype='application/json')

    dt_boxes, rec_res = text_sys(img)
    dt_results = list(zip(dt_boxes, rec_res))
    dt_results.sort(key=lambda x: (x[0].min(0)[1]))

    result = []
    for row in dt_results:
        row = {
            "words": row[1][0],
            "location": {
                "top": int(row[0][0][1]),
                "left": int(row[0][0][0]),
                "width": int(row[0][2][0] - row[0][0][0]),
                "height": int(row[0][2][1] - row[0][0][1]),
            },
            "score": float(row[1][1]),
        }
        result.append(row)
    
    if 'duration' in body and body['duration']:
        result.append({"duration": time.time() - start_time})
    return flask.Response(
        response=json.dumps(result),
        status=200, mimetype='application/json')

server = pywsgi.WSGIServer(('0.0.0.0', 8080), app)
server.serve_forever()