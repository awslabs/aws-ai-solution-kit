import json
import os

import numpy as np
import onnxruntime
from utils import preprocess, multiclass_nms, postprocess
from collections import defaultdict
import cv2

from aikits_utils import readimg, lambda_return

import GPUtil
cuda_available = True if len(GPUtil.getGPUs()) else False
if cuda_available:
    print(GPUtil.getGPUs()[0].name)

COCO_CLASSES = ['accordion', 'airplane', 'alligator', 'apple', 'army_tank', 'awning', 'backpack', 'ball', 'balloon', 'banana', 'barrel', 'baseball', 'baseball_bat', 'baseball_glove', 'basket', 'bathtub', 'bear', 'bed', 'bee', 'beer_bottle', 'bell_pepper', 'belt', 'bench', 'bicycle', 'billboard', 'bird', 'blackboard', 'boat', 'book', 'bookcase', 'boot', 'bottle', 'bowl', 'bowling_ball', 'box', 'bracelet', 'brassiere', 'bread', 'broccoli', 'building', 'bus_(vehicle)', 'butterfly', 'cabinet', 'cake', 'camel', 'camera', 'can', 'candle', 'candy_bar', 'cannon', 'canoe', 'car_(automobile)', 'carrot', 'cart', 'castle', 'cat', 'caterpillar', 'cello', 'cellular_telephone', 'chair', 'chicken_(animal)', 'chopping_board', 'chopstick', 'christmas_tree', 'clock', 'coat', 'cocktail', 'coffee_table', 'coin', 'computer_keyboard', 'computer_monitor', 'cone', 'cookie', 'cow', 'cowboy_hat', 'crab_(animal)', 'crown', 'cucumber', 'cup', 'cupboard', 'curtain', 'deer', 'desk', 'dessert', 'dinosaur', 'dog', 'doll', 'dolphin', 'door', 'doorknob', 'doughnut', 'dragonfly', 'drawer', 'dress', 'drum_(musical_instrument)', 'duck', 'duffel_bag', 'eagle', 'earring', 'egg', 'elephant', 'fan', 'faucet', 'fireplace', 'fireplug', 'fish', 'flag', 'flower_arrangement', 'flowerpot', 'football_helmet', 'fork', 'fountain', 'french_fries', 'frisbee', 'frog', 'fruit', 'fruit_juice', 'frying_pan', 'gazelle', 'giraffe', 'glass_(drink_container)', 'glove', 'goat', 'goggles', 'goose', 'grape', 'guitar', 'gun', 'hamburger', 'hamster', 'handbag', 'handle', 'harbor_seal', 'hat', 'headset', 'helicopter', 'helmet', 'high_heels', 'hog', 'horse', 'house', 'icecream', 'insect', 'jacket', 'jaguar', 'jean', 'jellyfish', 'kitchen_table', 'kite', 'knife', 'ladder', 'lamp', 'lantern', 'laptop_computer', 'lavender', 'lemon', 'lettuce', 'license_plate', 'life_jacket', 'lightbulb', 'lighthouse', 'lily', 'lion', 'lizard', 'maple', 'mask', 'microphone', 'microwave_oven', 'minivan', 'mirror', 'monkey', 'motorcycle', 'mouse_(computer_equipment)', 'muffin', 'mug', 'mushroom', 'musical_instrument', 'napkin', 'necklace', 'necktie', 'nightstand', 'onion', 'orange_(fruit)', 'oven', 'owl', 'paddle', 'painting', 'palm_tree', 'parachute', 'parking_meter', 'parrot', 'pasta', 'pastry', 'pen', 'penguin', 'person', 'piano', 'pillow', 'pizza', 'plastic_bag', 'plate', 'polar_bear', 'pool_table', 'porch', 'poster', 'potted_plant', 'pumpkin', 'rabbit', 'refrigerator', 'remote_control', 'ring', 'roller_skate', 'rose', 'salad', 'sandal_(type_of_shoe)', 'sandwich', 'saucer', 'saxophone', 'scarf', 'scissors', 'sculpture', 'sheep', 'shirt', 'shoe', 'short_pants', 'shrimp', 'sink', 'skateboard', 'ski', 'skirt', 'skullcap', 'snake', 'snowboard', 'soccer_ball', 'sock', 'sofa', 'sofa_bed', 'sparrow', 'speaker_(stero_equipment)', 'spectacles', 'spider', 'spoon', 'sportswear', 'squirrel', 'stool', 'stop_sign', 'stove', 'straw_(for_drinking)', 'strawberry', 'street_sign', 'streetlight', 'suit_(clothing)', 'suitcase', 'sunflower', 'sunglasses', 'sunhat', 'surfboard', 'sushi', 'swimming_pool', 'swimsuit', 'table', 'tablet_computer', 'taxi', 'teddy_bear', 'telephone', 'television_set', 'tennis_ball', 'tennis_racket', 'tent', 'tiger', 'toilet', 'toilet_tissue', 'tomato', 'toothbrush', 'towel', 'tower', 'toy', 'traffic_light', 'train_(railroad_vehicle)', 'trash_can', 'tray', 'tree', 'tripod', 'trousers', 'truck', 'trumpet', 'turtle', 'umbrella', 'vase', 'vegetables', 'violin', 'wall_socket', 'watch', 'water_jug', 'whale', 'wheel', 'wheelchair', 'window', 'wineglass', 'zebra']

model_path = os.environ['MODEL_PATH']
ort_session = onnxruntime.InferenceSession(model_path + '/yolox_l.onnx', providers=['CUDAExecutionProvider'] if cuda_available else ['CPUExecutionProvider'])
ort_session_1 = onnxruntime.InferenceSession(model_path + '/model_1.onnx', providers=['CUDAExecutionProvider'] if cuda_available else ['CPUExecutionProvider'])
ort_session_2 = onnxruntime.InferenceSession(model_path + '/model_2.onnx', providers=['CUDAExecutionProvider'] if cuda_available else ['CPUExecutionProvider'])
ort_session_3 = onnxruntime.InferenceSession(model_path + '/model_3.onnx', providers=['CUDAExecutionProvider'] if cuda_available else ['CPUExecutionProvider'])
ort_session_4 = onnxruntime.InferenceSession(model_path + '/model_4.onnx', providers=['CUDAExecutionProvider'] if cuda_available else ['CPUExecutionProvider'])
outputs_template = {
    'upper_wear': {'短袖':0, '长袖':1},
    'upper_wear_texture': {'图案': 0, '纯色': 1, '条纹/格子': 2},
    'lower_wear': {'短裤/裙':0, '长裤/裙':1},
    'glasses': {'有眼镜':0, '无眼镜':1},
    'bag': {'有背包':0, '无背包':1},
    'headwear': {'有帽':0, '无帽':1},
    'orientation': {'左侧面':0, '背面':1, '正面':2, '右侧面':3},
    'upper_cut': {'有截断':0, '无截断':1},
    'lower_cut': {'无截断':1, '有截断':0},
    'occlusion': {'无遮挡':0, '重度遮挡':2, '轻度遮挡':1},
    'face_mask': {'无口罩':1, '戴口罩':0},
    'gender': {'男性':0, '女性':1},
    'age': {'幼儿':0, '青少年':1, '中年':2, '老年':3},
    'smoke': {'吸烟':0, '未吸烟':1},
    'cellphone': {'使用手机':0, '未使用手机':1},
    'carrying_item': {'有手提物':0, '无手提物':1}
}
def softmax(x):
    x = np.asarray(x)
    x_col_max = x.max(axis=0)
    x_col_max = x_col_max.reshape([1,x.shape[1]])
    x = x - x_col_max  # 防止数值上溢
    x_exp = np.exp(x)
    x_exp_col_sum = x_exp.sum(axis=0).reshape([1,x.shape[1]])
    softmax = x_exp / x_exp_col_sum
    return softmax

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

        origin_img = img[:,:,::-1]
    except:
        return lambda_return(400, 'invalid param')
    h_ori, w_ori, _ = origin_img.shape

    h, w = (640, 640)
    image, ratio = preprocess(origin_img, (h, w))
    res = ort_session.run(['output'], {'images': image[np.newaxis,:]})[0]
    predictions = postprocess(res, (h, w), p6=False)[0]
    boxes = predictions[:, :4]
    scores = predictions[:, 4, None] * predictions[:, 5:]

    boxes_xyxy = np.ones_like(boxes)
    boxes_xyxy[:, 0] = boxes[:, 0] - boxes[:, 2]/2.
    boxes_xyxy[:, 1] = boxes[:, 1] - boxes[:, 3]/2.
    boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2]/2.
    boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3]/2.
    boxes_xyxy /= ratio
    dets = multiclass_nms(boxes_xyxy, scores, nms_thr=0.45, score_thr=0.1)
    if dets is not None:
        final_boxes = dets[:, :4]
        final_scores, final_cls_inds = dets[:, 4], dets[:, 5]
    final_boxes[:, 0] /= w_ori
    final_boxes[:, 1] /= h_ori
    final_boxes[:, 2] /= w_ori
    final_boxes[:, 3] /= h_ori

    d = defaultdict(list)
    for i in range(len(final_boxes)):
        label = COCO_CLASSES[int(final_cls_inds[i])]
        d[label].append([final_boxes[i].tolist(), final_scores[i]*100])

    person = d.get('person', [])

    output = {
        "Labels": [],
        "LabelModelVersion": "1.2.0"
    }

    for bbox in person:
        bbox = bbox[0]
        img_person = origin_img[int(h_ori*bbox[1]):int(h_ori*bbox[3]), int(w_ori*bbox[0]):int(w_ori*bbox[2]),::-1]
        img_person = cv2.resize(img_person, (int(220*1.5), int(395*1.5)))/255
        img_person = img_person.transpose((2,0,1))[np.newaxis,:].astype('float32')
        rlt =  ort_session_1.run(['upper_wear', 'upper_wear_texture', 'lower_wear', 'glasses', 'bag', 'headwear'], {'img': img_person})
        upper_wear, upper_wear_texture, lower_wear, glasses, bag, headwear = [softmax(row.T).T[0].tolist() for row in rlt]
        rlt =  ort_session_2.run(['orientation', 'upper_cut', 'lower_cut', 'occlusion', 'face_mask'], {'img': img_person})
        orientation, upper_cut, lower_cut, occlusion, face_mask = [softmax(row.T).T[0].tolist() for row in rlt]
        rlt =  ort_session_3.run(['gender', 'age'], {'img': img_person})
        gender, age = [softmax(row.T).T[0].tolist() for row in rlt]
        rlt =  ort_session_4.run(['smoke', 'cellphone', 'carrying_item'], {'img': img_person})
        smoke, cellphone, carrying_item = [softmax(row.T).T[0].tolist() for row in rlt]
        person_output = defaultdict(dict)
        for k, v in outputs_template.items():
            for label, idx in v.items():
                person_output[k][label] = round(eval(k)[idx]*100, 2)
        person_output["BoundingBox"] = {
            "Width": bbox[2] - bbox[0],
            "Height": bbox[3] - bbox[1],
            "Left": bbox[0],
            "Top": bbox[1]
        }
        output["Labels"].append(dict(person_output))
    return lambda_return(200, json.dumps(output))