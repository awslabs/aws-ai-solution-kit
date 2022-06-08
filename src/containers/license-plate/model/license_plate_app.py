import json
import time
from os import environ

import cv2
from aikits_utils import readimg, lambda_return

from main import *

if environ["MODEL_PATH"] is None:
    environ["MODEL_PATH"] = "/opt/program/model/"


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
        self.drop_score = 0.7
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
            buffer = math.ceil((tmp_box[1][0] -tmp_box[0][0]) / 8)
            img_crop = self.get_rotate_crop_image(ori_im, tmp_box)
            img_crop_list.append(img_crop)

            img_crop_list, angle_list = self.text_classifier(img_crop_list)
            rec_res = self.text_recognizer(img_crop_list)
            found = False
            for box, rec_reuslt in zip(dt_boxes, rec_res):
                text, score = rec_reuslt
                if score >= self.drop_score and len(text) == 7:
                    found = True

            if not found:
                img_crop_list = []
                # Vans license plate
                tmp_box_up = copy.deepcopy(tmp_box)
                tmp_box_up[0][0] = tmp_box[0][0] - buffer
                tmp_box_up[0][1] = tmp_box[0][1] - buffer

                tmp_box_up[1][0] = tmp_box[1][0] + buffer
                tmp_box_up[1][1] = tmp_box[1][1] - buffer

                tmp_box_up[2][0] = max(tmp_box[0][0], tmp_box[2][0]) + buffer
                tmp_box_up[2][1] = math.ceil(tmp_box[1][1] + (tmp_box[2][1] - tmp_box[1][1]) / 2) - 10

                tmp_box_up[3][0] = min(tmp_box[3][0], tmp_box[0][0]) -buffer
                tmp_box_up[3][1] = math.ceil(tmp_box[0][1] + (tmp_box[3][1] - tmp_box[0][1]) / 2) - 10

                img_crop_up = self.get_rotate_crop_image(ori_im, tmp_box_up)

                tmp_box_down = copy.deepcopy(tmp_box)
                tmp_box_down[0][0] = min(tmp_box[3][0], tmp_box[0][0]) - buffer
                tmp_box_down[0][1] = math.ceil(tmp_box[0][1] + (tmp_box[3][1] - tmp_box[0][1]) / 2) - buffer

                tmp_box_down[1][0] = max(tmp_box[0][0], tmp_box[2][0]) + buffer
                tmp_box_down[1][1] = math.ceil(tmp_box[1][1] + (tmp_box[2][1] - tmp_box[1][1]) / 2) - buffer

                tmp_box_down[2][0] = tmp_box[2][0] + buffer
                tmp_box_down[2][1] = tmp_box[2][1] + buffer

                tmp_box_down[3][0] = tmp_box[3][0] - buffer
                tmp_box_down[3][1] = tmp_box[3][1] + buffer

                img_crop_down = self.get_rotate_crop_image(ori_im, tmp_box_down)

                height, width = img_crop_down.shape[:2]
                img_crop_up = cv2.resize(img_crop_up, (width, height), interpolation= cv2.INTER_LINEAR)

                img_crop = cv2.hconcat([img_crop_up, img_crop_down])
                img_crop = cv2.resize(img_crop, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
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
    start_time = time.time()
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
        img = img[:,:,::-1]
    except:
        return lambda_return(400, 'invalid param')
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

    return lambda_return(200, json.dumps(result))
