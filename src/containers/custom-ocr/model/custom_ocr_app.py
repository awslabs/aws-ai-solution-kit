import hashlib
import json
import os
import time
from os import environ

import cv2

from main import *
import hashlib
import pickle
from aikits_utils import readimg, lambda_return

model_path = os.environ['MODEL_PATH']
os.makedirs('/mnt/custom-ocr/', exist_ok=True)
ort_session_backbone = onnxruntime.InferenceSession(model_path + 'matcher_backbone.onnx', providers=['CPUExecutionProvider'])
_ = ort_session_backbone.run(['feat_c', 'feat_f'], {'img': np.zeros([1, 1, 64, 64], dtype='float32')})

ort_session_pos_encoding = onnxruntime.InferenceSession(model_path + 'matcher_pos_encoding.onnx', providers=['CPUExecutionProvider'])
_ = ort_session_pos_encoding.run(['feat_c_out'], {'feat_c_in': np.zeros([1, 256, 64, 64], dtype='float32')})

ort_session_loftr_coarse = onnxruntime.InferenceSession(model_path + 'matcher_loftr_coarse.onnx', providers=['CPUExecutionProvider'])
_ = ort_session_loftr_coarse.run(['feat_c0_out', 'feat_c1_out'], {'feat_c0_in': np.zeros([1, 64, 256], dtype='float32'), 'feat_c1_in': np.zeros([1, 64, 256], dtype='float32')})

ort_session_coarse_matching = onnxruntime.InferenceSession(model_path + 'matcher_coarse_matching.onnx', providers=['CPUExecutionProvider'])

ort_session_fine_preprocess = onnxruntime.InferenceSession(model_path + 'matcher_fine_preprocess.onnx', providers=['CPUExecutionProvider'])
_ = ort_session_fine_preprocess.run(['feat_f0_unfold', 'feat_f1_unfold'],
                                    {'feat_f0': np.zeros([1, 128, 64, 64], dtype='float32'), 'feat_f1': np.zeros([1, 128, 64, 64], dtype='float32'), 'feat_c0': np.zeros([1, 64, 256], dtype='float32'), 'feat_c1':np.zeros([1, 64, 256], dtype='float32'),
                                     'b_ids': np.zeros([1], dtype='int64'), 'i_ids': np.zeros([1], dtype='int64'), 'j_ids': np.zeros([1], dtype='int64')})

ort_session_loftr_fine = onnxruntime.InferenceSession(model_path + 'matcher_loftr_fine.onnx', providers=['CPUExecutionProvider'])
_ = ort_session_loftr_fine.run(['feat_f0_unfold_out', 'feat_f1_unfold_out'],
                               {'feat_f0_unfold_in': np.zeros([1, 64, 128], dtype='float32'), 'feat_f1_unfold_in': np.zeros([1, 64, 128], dtype='float32')})

ort_session_fine_matching = onnxruntime.InferenceSession(model_path + 'matcher_fine_matching.onnx', providers=['CPUExecutionProvider'])


lmdb_root = "/mnt/custom-ocr"

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
            pad = min(img_crop.shape[:2])//10
            if pad:
                img_crop = cv2.copyMakeBorder(img_crop, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(255,255,255))
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
def get_feature(img):
    feat_c, feat_f = ort_session_backbone.run(['feat_c', 'feat_f'], {'img': img[np.newaxis,np.newaxis,:]})
    feat_c = ort_session_pos_encoding.run(['feat_c_out'], {'feat_c_in': feat_c})[0].transpose((0, 2, 3, 1))
    n, h, w, c = feat_c.shape
    feat_c = feat_c.reshape(n, -1, c)
    return feat_c, feat_f, (h,w), (feat_f.shape[2], feat_f.shape[3])
def generate_template(img):
    h, w, _ = img.shape
    scale = 480/max(h, w)
    img = cv2.resize(img, None, fx=scale, fy=scale)
    img = (cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)/255).astype('float32')
    feat_c, feat_f, hw_c, hw_f = get_feature(img)
    hw_i = img.shape
    return {
        'feat_c': feat_c,
        'feat_f': feat_f,
        'hw_c': hw_c,
        'hw_f': hw_f,
        'hw_i': hw_i,
        'scale': scale
    }

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
    if isinstance(event['body'], str):
        body = json.loads(event['body'])
    else:
        body = event['body']

    if body.get("type", '') == 'add':
        try:
            img = read_img(body)
            if isinstance(img, str):
                return lambda_return(400, f'`parameter `{img}` illegal')
            if isinstance(body["template"], str):
                template_dict = json.loads(body["template"])
            else:
                template_dict = body["template"]
        except:
            return lambda_return(400, f'`invalid param')
        img_hash = hashlib.sha1(img).hexdigest()[:20] + hashlib.sha1(str(time.time()).encode()).hexdigest()[20:]
        template = generate_template(img)
        template.update(template=template_dict)
        pickle.dump(template, open(os.path.join(lmdb_root, f'{img_hash}.pkl'), 'wb'))
        result = {
            'template_id': img_hash
        }
    elif body.get("type", '') == 'del':
        try:
            img_hash = body["template_id"]
        except:
            return lambda_return(400, 'invalid param')

        os.remove(os.path.join(lmdb_root, f'{img_hash}.pkl'))
        result = {
            'template_id': body["template_id"]
        }
    elif body.get("type", '') == 'list':
        keys = [row[:-4] for row in os.listdir(lmdb_root) if row[-3:] == 'pkl']
        results = []
        for key in keys:
            template = pickle.load(open(os.path.join(lmdb_root, f'{key}.pkl'), 'rb'))
            results.append({
                key: template['template']
            })
        result = {
            'template_id_list': keys,
            'template': results
        }
        
    else:
        try:
            img_hash = body["template_id"]
            template = pickle.load(open(os.path.join(lmdb_root, f'{img_hash}.pkl'), 'rb'))
            hw_c = np.array(template['hw_c'], dtype='long')
            hw0_i = np.array(template['hw_i'], dtype='long')
            img = read_img(body)
            if isinstance(img, str):
                return lambda_return(400, f'`parameter `{img}` illegal')
        except:
            return lambda_return(400, 'invalid param')

        h,w,_ = img.shape
        h_scale, w_scale = h/template['hw_i'][0], w/template['hw_i'][1]
        im = cv2.resize(img, (template['hw_i'][1], template['hw_i'][0]))
        im = (cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)/255).astype('float32')
        feat_c1, feat_f1, hw1_c, hw1_f = get_feature(im)
        
        hw1_c = np.array(hw1_c, dtype='long')
        feat_c0, feat_c1 = ort_session_loftr_coarse.run(['feat_c0_out', 'feat_c1_out'], {'feat_c0_in': template['feat_c'], 'feat_c1_in': feat_c1})
        b_ids, i_ids, j_ids, gt_mask, m_bids, mkpts0_c, mkpts1_c, mconf = \
            ort_session_coarse_matching.run(['b_ids', 'i_ids','j_ids', 'gt_mask','m_bids', 'mkpts0_c','mkpts1_c', 'mconf'],
                                            {'feat_c0': feat_c0, 'feat_c1': feat_c1, 'hw0_c': hw_c, 'hw1_c': hw1_c, 'hw0_i': hw0_i})
        del hw1_c
        del hw0_i
        del hw_c
        feat_f0_unfold, feat_f1_unfold = ort_session_fine_preprocess.run(['feat_f0_unfold', 'feat_f1_unfold'],
                                                                        {'feat_f0': template['feat_f'], 'feat_f1': feat_f1, 'feat_c0': template['feat_c'], 'feat_c1':feat_c1, 'b_ids': b_ids, 'i_ids': i_ids, 'j_ids': j_ids})
        feat_f0_unfold, feat_f1_unfold = ort_session_loftr_fine.run(['feat_f0_unfold_out', 'feat_f1_unfold_out'],
                                                                    {'feat_f0_unfold_in': feat_f0_unfold, 'feat_f1_unfold_in': feat_f1_unfold})
        mkpts0_f, mkpts1_f = ort_session_fine_matching.run(['mkpts0_f', 'mkpts1_f'],
                                                        {'feat_f0_unfold': feat_f0_unfold, 'feat_f1_unfold': feat_f1_unfold, 'hw0_i': np.array(template['hw_i'], dtype='long'), 'hw0_f': np.array(template['hw_f'], dtype='long'),
                                                        'mkpts0_c':mkpts0_c, 'mkpts1_c':mkpts1_c})
        H, inliers = cv2.findHomography(mkpts0_f, mkpts1_f, cv2.USAC_MAGSAC, 0.5, 0.999, 100000)
        inliers = inliers > 0
        result = []
        for row in template['template']:
            points = row[0]
            key = row[1]
            pt = np.expand_dims(np.float32(points), 1)*template['scale']
            rec_new = cv2.perspectiveTransform(pt, H).astype('float32')
            rec_new[:,:,0]*=w_scale
            rec_new[:,:,1]*=h_scale
            tmp_box = copy.deepcopy(rec_new[:,0,:])
            img_crop = text_sys.get_rotate_crop_image(img, tmp_box)
            img_crop = cv2.copyMakeBorder(img_crop, 15, 15, 15, 15, cv2.BORDER_CONSTANT, value=(255,255,255))
            _, rec_res = text_sys(img_crop)
            text = [rec[0] for rec in rec_res]
            score = float(np.mean([rec[1] for rec in rec_res]))
            res = {
                'key': key, 'value': text, 'score': round(score*100, 2), 'position': tmp_box.astype('uint32').tolist()
            }
            result.append(res)
    
    if 'duration' in body and body['duration']:
        result.append({"duration": time.time() - start_time})
        
    return lambda_return(200, json.dumps(result))
