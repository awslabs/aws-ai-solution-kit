import json
import os
import main
from aikits_utils import readimg, lambda_return

model_path = os.environ['MODEL_PATH']
model = main.SCRFD(model_file = model_path + 'det.onnx')
landmark_model_2d = main.Landmark(model_file = model_path + 'landmark.onnx')
attribute_model = main.Attribute(model_file = model_path + 'attribute.onnx')
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
    bboxes, _ = model.detect(img)
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
        #landmark_3d, pose = landmark_model_3d.get(img, bboxes[i])
        landmark_2d = landmark_model_2d.get(img, bboxes[i])
        landmark_106 = []
        for row in landmark_2d:
            landmark_106.append({
                'x': int(row[0]),
                'y': int(row[1])
            }),
        face.update(landmark_106=landmark_106)
        attribute_pred = attribute_model.get(img, bboxes[i])
        face.update(gender= attribute_pred['Gender'][0].lower())
        face.update(age= int((attribute_pred['AgeRange'][0]+attribute_pred['AgeRange'][1])/2))
        face_list.append(face)

    output = {
        "Faces": face_list,
        "FaceModelVersion": "1.2.0"
    }

    return lambda_return(200, json.dumps(output))
