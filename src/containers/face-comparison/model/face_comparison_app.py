import base64
import json
import os
from io import BytesIO
import numpy as np
from PIL import Image
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import main

model_path = os.environ['MODEL_PATH']
model = main.RetinaFace(model_file = model_path + 'det.onnx')
arcface_model = main.ArcFaceONNX(model_file= model_path + 'w600k_r50.onnx')

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

    img = np.asarray(pil_image)[:, :, :3]
    bboxes, kpss = model.detect(img)
    face_list = []
    for i in range(len(bboxes)):
        face = {
            "BoundingBox": {
                "Width": float((bboxes[i][2] - bboxes[i][0])/img.shape[1]),
                "Height": float((bboxes[i][3] - bboxes[i][1])/img.shape[0]),
                "Left": float(bboxes[i][0]/img.shape[1]),
                "Top": float(bboxes[i][1]/img.shape[0])
            },
            "Confidence": float(bboxes[i][4])
        }
        face_hash = arcface_model.get(img, kpss[i]).astype('float16').tolist()
        face.update(face_hash=face_hash)
        face_list.append(face)

    output = {
        "Faces": face_list,
        "FaceModelVersion": "1.2.0"
    }

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
