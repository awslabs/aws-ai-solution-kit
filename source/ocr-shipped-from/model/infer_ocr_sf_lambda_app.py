# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import base64
import functools
import json
import re
from io import BytesIO
from os import environ
from urllib import request

import cv2
from PIL import ImageChops

from text_model import *


def sorted_boxes(dt_boxes):
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


def crop_result(image, left, top, width, height):
    result = []
    try:
        w, h = image.size
        w = min(w, left + width)
        h = min(h, top + height)
        pil_image_crop = image.crop((left, top, w, h))
        pil_image_crop = pil_image_crop.resize((width * 2, height * 2), Image.ANTIALIAS)
        width, height = pil_image_crop.size
        pil_image_crop = pil_image_crop.filter(ImageFilter.DETAIL)
        pil_image_crop = pil_image_crop.filter(ImageFilter.SHARPEN)
        # pil_image_crop = pil_image_crop.filter(ImageFilter.EDGE_ENHANCE)

        # pil_image_crop.save('rotate-output.png')

        img = np.array(pil_image_crop)[:, :, :3][:, :, ::-1]
        dt_boxes, rec_res = text_sys(img)

        dt_results = list(zip(dt_boxes, rec_res))
        dt_results.sort(key=lambda x: (x[0].min(0)[1]))

        result = []

        for row in dt_results:
            if float(row[1][1]) > 0.8:
                row = {
                    "words": row[1][0].replace('縠', ' '),
                    "location": {
                        "top": int(row[0][0][1]),
                        "left": int(row[0][0][0]),
                        "width": int(row[0][2][0] - row[0][0][0]),
                        "height": int(row[0][2][1] - row[0][0][1]),
                    },
                    "score": float(row[1][1]),
                }
                result.append(row)
        print(result)
    finally:
        return result


def center_location(location):
    return location['left'] + int(location['width'] / 2), location['top'] + int(location['height'] / 2)


def handler(event, context):
    start_time = time.time()
    if "body" not in event:
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
            },
        }
    if isinstance(event["body"], str):
        body = json.loads(event["body"])
    else:
        body = event["body"]
    if "url" in body:
        uri = body["url"]
        file_data = request.urlopen(body['url'])
        image_string = file_data.read()
    else:
        image_string = base64.b64decode(body["img"])

    pil_image = Image.open(BytesIO(image_string)).convert('RGB')
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                exif = dict(pil_image.getexif().items())
                if exif[orientation] == 3:
                    pil_image = pil_image.rotate(180, expand=True)
                if exif[orientation] == 8:
                    pil_image = pil_image.rotate(90, expand=True)
                if exif[orientation] == 6:
                    pil_image = pil_image.rotate(270, expand=True)
                break
    except Exception:
        pass

    angles = [0]
    ref_score = 0.96
    for arc in angles:
        if arc != 0:
            pil_image_rotate = pil_image.rotate(arc, expand=True)
        else:
            pil_image_rotate = pil_image

        width, height = pil_image_rotate.size
        if 'table' in body and body["table"]:
            crop_text_area = body['table']
            result_list = []
            for area in crop_text_area:
                full_words = crop_result(pil_image_rotate, area['crop'][0], area['crop'][1], area['crop'][2],
                                         area['crop'][3])
                print('full_words')
                print(full_words)
                print('------------------')
                for name in area['names']:
                    print(name)
                    match_words = []
                    for word in full_words:
                        if word['words'].replace(' ', '') == name.replace(' ', '') or word['words']. \
                                replace(' ', '').__contains__(name.replace(' ', '')):
                            match_word = []
                            name_value1 = ''
                            name_value2 = ''
                            match_word.append(word['words'])
                            # name_x = word['location']['left'] + int(word['location']['width'] / 2)
                            # name_y = word['location']['top'] + int(word['location']['height'] / 2)
                            x1, y1 = center_location(word['location'])
                            distance = 1000000

                            for value in full_words:
                                x2, y2 = center_location(value['location'])
                                distance2 = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                                if distance > distance2 > 0 and \
                                        y2 > word['location']['top'] and \
                                        y2 < word['location']['top'] + word['location']['height'] and \
                                        x2 > word['location']['left'] + word['location']['width']:
                                    distance = distance2
                                    name_value1 = value['words']
                            print(">" + name_value1)
                            distance = 1000000

                            for value in full_words:
                                x2, y2 = center_location(value['location'])
                                distance2 = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                                if distance2 < distance and distance2 > 0 and \
                                        value['location']['top'] > word['location']['top'] + 20 and \
                                        x2 > word['location']['left'] and \
                                        x2 < word['location']['left'] + word['location']['width']:
                                    distance = distance2
                                    name_value2 = value['words']
                            print(">" + name_value2)
                            match_word.append(name_value1)
                            match_word.append(name_value2)
                            match_words.append(match_word)
                    found = {
                        "name": name,
                        "match_words": match_words
                    }
                    result_list.append(found)
            print(json.dumps(result_list))
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST",
                },
                "body": json.dumps(result_list),
            }
