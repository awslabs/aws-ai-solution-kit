import boto3
import datetime
import json
import logging
import os
import re
import subprocess
from pathlib import Path

from ocr import TextSystem
from table import TableSystem
from layout import LayoutPredictor
import numpy as np
from markdownify import markdownify as md
from utils import check_and_read
from xycut import recursive_xy_cut
import time
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StructureSystem(object):
    def __init__(self):
        self.mode = 'structure'
        self.recovery = True
        drop_score = 0
        # init model
        self.layout_predictor = LayoutPredictor()
        self.text_system = TextSystem()
        self.table_system = TableSystem(
            self.text_system.text_detector,
            self.text_system.text_recognizer)
    def __call__(self, img, return_ocr_result_in_table=False, lang='ch'):
        time_dict = {
            'image_orientation': 0,
            'layout': 0,
            'table': 0,
            'table_match': 0,
            'det': 0,
            'rec': 0,
            'kie': 0,
            'all': 0
        }
        start = time.time()
        ori_im = img.copy()
        layout_res, elapse = self.layout_predictor(img)
        time_dict['layout'] += elapse
        res_list = []
        for region in layout_res:
            res = ''
            if region['bbox'] is not None:
                x1, y1, x2, y2 = region['bbox']
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                x1, y1, x2, y2 = max(x1, 0), max(y1, 0), max(x2, 0), max(y2, 0)
                roi_img = ori_im[y1:y2, x1:x2, :]
            else:
                x1, y1, x2, y2 = 0, 0, w, h
                roi_img = ori_im
            if region['label'] == 'table':
                res, table_time_dict = self.table_system(
                    roi_img, return_ocr_result_in_table, lang)
                time_dict['table'] += table_time_dict['table']
                time_dict['table_match'] += table_time_dict['match']
                time_dict['det'] += table_time_dict['det']
                time_dict['rec'] += table_time_dict['rec']
            else:
                wht_im = np.ones(ori_im.shape, dtype=ori_im.dtype)
                wht_im[y1:y2, x1:x2, :] = roi_img
                filter_boxes, filter_rec_res = self.text_system(
                    wht_im, lang)

                # remove style char,
                # when using the recognition model trained on the PubtabNet dataset,
                # it will recognize the text format in the table, such as <b>
                style_token = [
                    '<strike>', '<strike>', '<sup>', '</sub>', '<b>',
                    '</b>', '<sub>', '</sup>', '<overline>',
                    '</overline>', '<underline>', '</underline>', '<i>',
                    '</i>'
                ]
                res = []
                for box, rec_res in zip(filter_boxes, filter_rec_res):
                    rec_str, rec_conf = rec_res
                    for token in style_token:
                        if token in rec_str:
                            rec_str = rec_str.replace(token, '')
                    if not self.recovery:
                        box += [x1, y1]
                    res.append({
                        'text': rec_str,
                        'confidence': float(rec_conf),
                        'text_region': box.tolist()
                    })
            res_list.append({
                'type': region['label'].lower(),
                'bbox': [x1, y1, x2, y2],
                'img': roi_img,
                'res': res,
            })
        end = time.time()
        time_dict['all'] = end - start
        return res_list, time_dict

structure_engine = StructureSystem()

def remove_symbols(text):
    """
    Removes symbols from the given text using regular expressions.

    Args:
        text (str): The input text.

    Returns:
        str: The cleaned text with symbols removed.
    """
    cleaned_text = re.sub(r"[^\w\s\u4e00-\u9fff]", "", text)
    return cleaned_text


def structure_predict(img, lang, output_type=None, table_type='markdown') -> str:

    all_res = []
    result, _ = structure_engine(img, lang=lang)
    if result != []:
        boxes = [row["bbox"] for row in result]
        res = []
        recursive_xy_cut(np.asarray(boxes).astype(int), np.arange(len(boxes)), res)
        all_res = [result[idx] for idx in res]
    if output_type=='json':
        result = []
        for row in all_res:
            if row['type'] == 'table':
                if table_type == 'html':
                    region_text = row["res"]["html"]
                else:
                    region_text = md(
                        row["res"]["html"],
                        strip=["b", "img"],
                        heading_style="ATX",
                        newline_style="BACKSLASH",
                    )
            else:
                region_text = ""
                for _, line in enumerate(row['res']):
                    region_text += line["text"] + (" " if lang == 'en' else '')
            row = {
                "BlockType": row['type'],
                "Geometry": {
                    "BoundingBox": {
                        'Width': row['bbox'][2]-row['bbox'][0],
                        'Height': row['bbox'][3]-row['bbox'][1],
                        'Left': row['bbox'][0],
                        'Top': row['bbox'][1]
                    }
                },
                "Text": region_text.strip()
            }
            result.append(row)
        return result
    doc = ""
    prev_region_text = ""

    for _, region in enumerate(all_res):
        if len(region["res"]) == 0:
            continue
        if region["type"].lower() == "figure":
            region_text = ""
            for _, line in enumerate(region["res"]):
                region_text += line["text"]
        elif region["type"].lower() == "title":
            region_text = ''
            for i, line in enumerate(region['res']):
                region_text += line['text'] + ''
            if remove_symbols(region_text) != remove_symbols(prev_region_text):
                doc += '## ' + region_text + '\n\n'
                prev_region_text = region_text
        elif region["type"].lower() == "table":
            if "<thead>" not in region["res"]["html"]:
                region["res"]["html"] = (
                    region["res"]["html"]
                    .replace("<tr>", "<thead><tr>", 1)
                    .replace("</tr>", "</thead></tr>", 1)
                )
            if table_type == 'html':
                doc += (
                    region["res"]["html"] + "\n\n"
                )
            else:
                doc += (
                    md(
                        region["res"]["html"],
                        strip=["b", "img"],
                        heading_style="ATX",
                        newline_style="BACKSLASH",
                    )
                    + "\n\n"
                )
        elif region["type"].lower() in ("header", "footer"):
            continue
        else:
            region_text = ""
            for _, line in enumerate(region["res"]):
                region_text += line["text"] + " "
            if remove_symbols(region_text) != remove_symbols(prev_region_text):
                doc += region_text
                prev_region_text = region_text

        doc += "\n\n"
    doc = re.sub("\n{2,}", "\n\n", doc.strip())
    return {'Markdown': doc}

def readimg(body, keys=None):
    if keys is None:
        keys = body.keys()
    inputs = dict()
    for key in keys:
        try:
            if key.startswith('url'): # url形式
                if body[key].startswith('http'): # http url
                    image_string = urllib2.urlopen(body[key]).read()
                elif body[key].startswith('s3'): # s3 key
                    o = urlparse(body[key])
                    bucket = o.netloc
                    path = o.path.lstrip('/')
                    s3 = boto3.resource('s3')
                    img_obj = s3.Object(bucket, path)
                    image_string = img_obj.get()['Body'].read()
                else:
                    raise
            elif key.startswith('img'): # base64形式
                image_string = base64.b64decode(body[key])
            else:
                raise
            inputs[key] = np.array(Image.open(BytesIO(image_string)).convert('RGB'))[:, :, :3]
        except:
            inputs[key] = None
    return inputs

if __name__ == "__main__":
    body = {
        "s3_bucket": "icyxu-llm-glue-assets",
        "object_key": "test_data/test_glue_lib/cn_pdf/2023.ccl-2.6.pdf",
        "destination_bucket": "llm-bot-document-results-icyxu",
        "mode": "ppstructure",
        "lang": "zh",
    }

    print(process_pdf_pipeline(body))
