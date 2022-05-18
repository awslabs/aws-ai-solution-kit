import base64
import json
import os
from io import BytesIO

import numpy as np
import onnxruntime
from utils import preprocess, multiclass_nms, postprocess
from collections import defaultdict
from PIL import Image
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

COCO_CLASSES = ['accordion', 'airplane', 'alligator', 'apple', 'army_tank', 'awning', 'backpack', 'ball', 'balloon', 'banana', 'barrel', 'baseball', 'baseball_bat', 'baseball_glove', 'basket', 'bathtub', 'bear', 'bed', 'bee', 'beer_bottle', 'bell_pepper', 'belt', 'bench', 'bicycle', 'billboard', 'bird', 'blackboard', 'boat', 'book', 'bookcase', 'boot', 'bottle', 'bowl', 'bowling_ball', 'box', 'bracelet', 'brassiere', 'bread', 'broccoli', 'building', 'bus_(vehicle)', 'butterfly', 'cabinet', 'cake', 'camel', 'camera', 'can', 'candle', 'candy_bar', 'cannon', 'canoe', 'car_(automobile)', 'carrot', 'cart', 'castle', 'cat', 'caterpillar', 'cello', 'cellular_telephone', 'chair', 'chicken_(animal)', 'chopping_board', 'chopstick', 'christmas_tree', 'clock', 'coat', 'cocktail', 'coffee_table', 'coin', 'computer_keyboard', 'computer_monitor', 'cone', 'cookie', 'cow', 'cowboy_hat', 'crab_(animal)', 'crown', 'cucumber', 'cup', 'cupboard', 'curtain', 'deer', 'desk', 'dessert', 'dinosaur', 'dog', 'doll', 'dolphin', 'door', 'doorknob', 'doughnut', 'dragonfly', 'drawer', 'dress', 'drum_(musical_instrument)', 'duck', 'duffel_bag', 'eagle', 'earring', 'egg', 'elephant', 'fan', 'faucet', 'fireplace', 'fireplug', 'fish', 'flag', 'flower_arrangement', 'flowerpot', 'football_helmet', 'fork', 'fountain', 'french_fries', 'frisbee', 'frog', 'fruit', 'fruit_juice', 'frying_pan', 'gazelle', 'giraffe', 'glass_(drink_container)', 'glove', 'goat', 'goggles', 'goose', 'grape', 'guitar', 'gun', 'hamburger', 'hamster', 'handbag', 'handle', 'harbor_seal', 'hat', 'headset', 'helicopter', 'helmet', 'high_heels', 'hog', 'horse', 'house', 'icecream', 'insect', 'jacket', 'jaguar', 'jean', 'jellyfish', 'kitchen_table', 'kite', 'knife', 'ladder', 'lamp', 'lantern', 'laptop_computer', 'lavender', 'lemon', 'lettuce', 'license_plate', 'life_jacket', 'lightbulb', 'lighthouse', 'lily', 'lion', 'lizard', 'maple', 'mask', 'microphone', 'microwave_oven', 'minivan', 'mirror', 'monkey', 'motorcycle', 'mouse_(computer_equipment)', 'muffin', 'mug', 'mushroom', 'musical_instrument', 'napkin', 'necklace', 'necktie', 'nightstand', 'onion', 'orange_(fruit)', 'oven', 'owl', 'paddle', 'painting', 'palm_tree', 'parachute', 'parking_meter', 'parrot', 'pasta', 'pastry', 'pen', 'penguin', 'person', 'piano', 'pillow', 'pizza', 'plastic_bag', 'plate', 'polar_bear', 'pool_table', 'porch', 'poster', 'potted_plant', 'pumpkin', 'rabbit', 'refrigerator', 'remote_control', 'ring', 'roller_skate', 'rose', 'salad', 'sandal_(type_of_shoe)', 'sandwich', 'saucer', 'saxophone', 'scarf', 'scissors', 'sculpture', 'sheep', 'shirt', 'shoe', 'short_pants', 'shrimp', 'sink', 'skateboard', 'ski', 'skirt', 'skullcap', 'snake', 'snowboard', 'soccer_ball', 'sock', 'sofa', 'sofa_bed', 'sparrow', 'speaker_(stero_equipment)', 'spectacles', 'spider', 'spoon', 'sportswear', 'squirrel', 'stool', 'stop_sign', 'stove', 'straw_(for_drinking)', 'strawberry', 'street_sign', 'streetlight', 'suit_(clothing)', 'suitcase', 'sunflower', 'sunglasses', 'sunhat', 'surfboard', 'sushi', 'swimming_pool', 'swimsuit', 'table', 'tablet_computer', 'taxi', 'teddy_bear', 'telephone', 'television_set', 'tennis_ball', 'tennis_racket', 'tent', 'tiger', 'toilet', 'toilet_tissue', 'tomato', 'toothbrush', 'towel', 'tower', 'toy', 'traffic_light', 'train_(railroad_vehicle)', 'trash_can', 'tray', 'tree', 'tripod', 'trousers', 'truck', 'trumpet', 'turtle', 'umbrella', 'vase', 'vegetables', 'violin', 'wall_socket', 'watch', 'water_jug', 'whale', 'wheel', 'wheelchair', 'window', 'wineglass', 'zebra']

model_path = os.environ['MODEL_PATH']
ort_session = onnxruntime.InferenceSession(model_path + '/yolox_l.onnx', providers=['CPUExecutionProvider'])

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
        image_string = urllib2.urlopen(uri).read()
    else:
        image_string = base64.b64decode(body['img'])

    pil_image = Image.open(BytesIO(image_string)).convert('RGB')

    origin_img = np.asarray(pil_image)[:, :, :3][:,:,::-1]
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

    output = {
        "Labels": [],
        "LabelModelVersion": "1.2.0"
    }
    for k,v in d.items():
        label = {
            "Name": k,
            "Confidence": max(list(map(lambda x:x[1], v))),
            "Instances": []
        }
        for row in v:
            bbox = {
                "BoundingBox": {
                    "Width": row[0][2] - row[0][0],
                    "Height": row[0][3] - row[0][1],
                    "Left": row[0][0],
                    "Top": row[0][1]
                },
                "Confidence": row[1]
            }
            label['Instances'].append(bbox)
        output["Labels"].append(label)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,GET'
        },

        'body': json.dumps(output)
    }
