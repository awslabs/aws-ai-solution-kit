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


# environ["MODEL_NAME"] = "standard_cn_business_license"
# environ["MODEL_PATH"] = "./model/"
text_sys = TextSystem()


def trim_crop(image):
    bg = Image.new(image.mode, image.size, image.getpixel((0, 0)))
    diff = ImageChops.difference(image, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return image.crop(bbox)


def crop_result(image, left, top, width, bottom):
    result = []
    try:
        width, height = image.size
        pil_image_crop = image.crop((left, top, width, bottom))
        # pil_image_crop = trim_crop(pil_image_crop)
        width, height = pil_image_crop.size
        if 0 < height < 50 or 0 < width < 50:
            pil_image_crop = pil_image_crop.resize((width * 4, height * 4), Image.ANTIALIAS)
            if 'ENHANCE_MODE' in environ and os.getenv('ENHANCE_MODE').lower() == 'true':
                pil_image_crop = pil_image_crop.filter(ImageFilter.DETAIL)
                pil_image_crop = pil_image_crop.filter(ImageFilter.SHARPEN)

        img = np.array(pil_image_crop)[:, :, :3][:, :, ::-1]
        dt_boxes, rec_res = text_sys(img)

        dt_results = list(zip(dt_boxes, rec_res))
        dt_results.sort(key=lambda x: (x[0].min(0)[1]))

        result = []

        for row in dt_results:
            if float(row[1][1]) > 0.8:
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
    finally:
        return result


def str_cells_words(cells):
    str_content = ''
    for i in range(len(cells)):
        if isinstance(cells[i], dict):
            str_content = str_content + str(cells[i]['words']).replace(' ', '')

    return str_content

def match_license_id(str_content):
    license_id = ''
    if license_id == '':
        license_id = ''.join(re.findall(r"代码([0-9a-zA-Z!\)]{18})", str_content)).strip()
    if license_id == '':
        license_id = ''.join(re.findall(r"注册号([0-9a-zA-Z!\)]{18})", str_content)).strip()
    if license_id == '':
        license_id = ''.join(re.findall(r"码([0-9a-zA-Z!\)]{18})", str_content)).strip()
    if license_id == '':
        license_id = ''.join(re.findall(r"([0-9]{2}[0-9A-Z!\)]{16})", str_content)).strip()
    if license_id == '':
        license_id = ''.join(re.findall(r"注册号([0-9a-zA-Z!\)]{15})", str_content)).strip()
    if license_id == '':
        license_id = ''.join(re.findall(r"代码([0-9a-zA-Z!\)]{0,18})", str_content)).strip()
    # replace by naming rule

    license_id = license_id.replace('o', '0')
    license_id = license_id.replace('O', '0')
    license_id = license_id.replace('i', '1')
    license_id = license_id.replace('I', '1')
    license_id = license_id.replace('z', '2')
    license_id = license_id.replace('Z', '2')
    license_id = license_id.replace('l', '1')
    license_id = license_id.replace('!', '1')
    license_id = license_id.replace(')', 'J')

    # upper must be after replace
    license_id = license_id.upper()
    if len(license_id) > 18:
        license_id = license_id[:18]
    return license_id


def match_company_name(str_content):
    company_name = ''
    if company_name == '':
        company_name = ''.join(re.findall(r'称(?!.*称)(.*?公司|厂)', str_content)[:1])
    if company_name == '':
        company_name = ''.join(re.findall(r'称((?!.*?名称|公司).*公司)类型', str_content)[:1])
    if company_name == '':
        company_name = ''.join(re.findall(r'称((?!.*?名称|公司).*公司)统一', str_content)[:1])

    if company_name == '':
        company_name = ''.join(re.findall(r'称(.*?厂)', str_content)[:1])
    company_name = company_name.replace(')', '）')
    company_name = company_name.replace('(', '（')
    company_name = company_name.replace('"', '')
    company_name = company_name.replace('~', '')
    return company_name


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

    license_id = ''
    company_name = ''
    angles = [0]
    if 'AUTO_ROTATION' in environ and os.getenv('AUTO_ROTATION').lower() == 'true':
        angles = [0, 90, 180, 270]

    ref_score = 0.90
    if 'REFERECNE_SCORE' in environ:
        ref_score = float(os.getenv('REFERECNE_SCORE'))

    for arc in angles:
        if arc != 0:
            pil_image_rotate = pil_image.rotate(arc, expand=True)
        else:
            pil_image_rotate = pil_image

        width, height = pil_image_rotate.size
        top_buf = 50
        result = crop_result(pil_image_rotate, 50, top_buf, width - 50, top_buf + int(height / 2))

        crop_top = 0

        str_content = ''
        if company_name == '':
            # crop
            for item in result:
                if item['words'].__contains__('公司') and item['score'] < ref_score:
                    crop_top = item['location']['top'] + top_buf - 10
                    crop_bottom = crop_top + item['location']['height'] + 20
                    break
            if crop_top > 0:
                str_content = str_content + str_cells_words(
                    simple_form(crop_result(pil_image_rotate, item['location']['left'], crop_top, width, crop_bottom)))
                company_name = match_company_name(str_content)

        if license_id == '':
            for item in result:
                if (item['words'].__contains__('代码') or item['words'].__contains__('注册号')) and item[
                    'score'] < ref_score:
                    crop_top = item['location']['top'] + top_buf - 10
                    if item['location']['height'] < 0:
                        crop_top = crop_top + item['location']['height']
                    crop_bottom = crop_top + abs(item['location']['height']) + 10
                    break
            if crop_top > 0:
                str_content = str_content + str_cells_words(
                    simple_form(
                        crop_result(pil_image_rotate, item['location']['left'], crop_top, item['location']['width'],
                                    crop_bottom)))
                license_id = match_license_id(str_content)
        # if len(cells) == 0:
        cells = []
        cells = simple_form(result)
        str_content = str_content + str_cells_words(cells)
        str_content = str_content.replace('…', '')
        if license_id == '':
            license_id = match_license_id(str_content)

        if company_name == '':
            company_name = match_company_name(str_content)

        if (license_id != '' and company_name != ''):
            break


    result = {}

    if 'COMPANY_NAME' in environ and os.getenv('COMPANY_NAME').lower() == 'true':
        result["company_name"] = str(company_name)

    if 'LICENSE_ID' in environ and os.getenv('LICENSE_ID').lower() == 'true':
        result["license_id"] = str(license_id)

    if 'DURATION' in environ and os.getenv('DURATION').lower() == 'true':
        result["duration"] = str(round(time.time() - start_time, 3))

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
        },
        "body": json.dumps(result),
    }


def simple_form_sort_row_first(a, b):
    if abs(a['location']['top'] - b['location']['top']) < 20:
        return a['location']['left'] - b['location']['left']
    else:
        return a['location']['top'] - b['location']['top']


def simple_form_sort_column_fisrt(a, b):
    if abs(a['location']['left'] - b['location']['left']) < 10:
        return a['location']['top'] - b['location']['top']
    else:
        return a['location']['left'] - b['location']['left']


def simple_form(result):
    word_list = []
    for item in result:
        word_list.append(item)

    sorted_word_list = sorted(word_list, key=functools.cmp_to_key(simple_form_sort_row_first))
    return sorted_word_list


# def main():
#     sample_dir = '/Users/yiyanz/Downloads/Test_Business_Licnese'
#
#     with open('output-license.txt', 'w') as output:
#         output.write('[')
#     for root, dirs, files in os.walk(sample_dir, topdown=False):
#         for f in files:
#             start_time = time.time()
#             if os.path.join(root, f).endswith('.jpg'):
#                 tmp_png = open(os.path.join(root, f), 'rb')  # 转为二进制格式
#                 base64_data = base64.b64encode(tmp_png.read())  # 使用base64 编码
#                 event = {
#                     "body": {
#                         "img": str(base64_data, encoding="utf-8"),
#                     }
#                 }
#
#                 cells = handler(event=event, context=None)
#
#                 cells['image_name'] = f
#
#                 print('cells')
#                 print(cells)
#
#                 with open('output-license.txt', 'a') as output:
#                     output.write(str(cells).replace('\'', '"') + ',')
#
#
# if __name__ == '__main__':
#     main()
