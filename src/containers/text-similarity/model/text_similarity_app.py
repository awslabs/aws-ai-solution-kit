import json
import os
import numpy as np
import onnxruntime
from transformers import BertTokenizerFast

model_path = os.environ['MODEL_PATH']
ort_session = onnxruntime.InferenceSession(model_path + '/CoSENT.onnx')
tokenizer = BertTokenizerFast.from_pretrained("hfl/chinese-roberta-wwm-ext", cache_dir= model_path +'/tokenizer')

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

    text = body['text']

    inputs = tokenizer(text, return_tensors='np')
    data = {
        'input_ids': inputs['input_ids'],
        'attention_mask': inputs['attention_mask'],
        'token_type_ids': inputs['token_type_ids']
    }
    label_name = ort_session.get_outputs()[0].name

    text_embedding = ort_session.run([label_name], data)[0][0].round(6).tolist()
    
    result = {'result': text_embedding}
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,GET'
        },

        'body': json.dumps(result)
    }
