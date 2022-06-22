import json
import os
import main
from aikits_utils import readimg, lambda_return

model_path = os.environ['MODEL_PATH']
model = main.SCRFD(model_file = model_path + 'det.onnx')
arcface_model = main.ArcFaceONNX(model_file= model_path + 'w600k_r50.onnx')

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
    if 'body' not in event:
        return lambda_return(400, 'invalid param')
    try:
        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event['body']
        if 'url' in body and 'img' in body:
            return lambda_return(400, '`url` and `img` cannot be used at the same time')
        img = read_img(body)
        if isinstance(img, str):
            return lambda_return(400, f'`parameter `{img}` illegal')
    except:
        return lambda_return(400, 'invalid param')

    bboxes, kpss = model.detect(img)
    kpss = kpss[:,:5][:,[0,1,4,2,3]] # `LeftEye, RightEye, leftMouth, rightMouth, noise` to `LeftEye, RightEye, noise, leftMouth, rightMouth`
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

    return lambda_return(200, json.dumps(output))