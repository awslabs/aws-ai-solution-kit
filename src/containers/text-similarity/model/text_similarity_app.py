import json
import os
import numpy as np
import onnxruntime
from transformers import BertTokenizerFast
from aikits_utils import lambda_return

model_path = os.environ['MODEL_PATH']
ort_session = onnxruntime.InferenceSession(model_path + '/CoSENT.onnx')
_ = ort_session.run(None, {"input_ids": np.zeros([1, 1], dtype='int64'), "token_type_ids": np.zeros([1, 1], dtype='int64'), "attention_mask": np.zeros([1, 1], dtype='int64')})
tokenizer = BertTokenizerFast.from_pretrained(model_path +'/tokenizer')
def get_embedding(text):
    inputs = tokenizer(text, return_tensors='np')
    data = {
        'input_ids': inputs['input_ids'],
        'attention_mask': inputs['attention_mask'],
        'token_type_ids': inputs['token_type_ids']
    }
    label_name = ort_session.get_outputs()[0].name
    text_embedding = ort_session.run([label_name], data)[0][0]
    return text_embedding

def get_cos_similar(v1, v2):
    num = float(np.dot(v1, v2))
    denom = np.linalg.norm(v1) * np.linalg.norm(v2)
    return 0.5 + 0.5 * (num / denom)

def handler(event, context):
    if 'body' not in event:
        return lambda_return(400, 'invalid param')
    try:
        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event['body']
        if 'text_1' in body:
            task = 'multi'
            text_1 = body['text_1']
            text_2 = body['text_2']
        else:
            task = 'single'
            text = body['text']
    except:
        return lambda_return(400, 'invalid param')

    if task == 'single':
        text_embedding = get_embedding(text).round(6).tolist()
        result = {'result': text_embedding}
    else:
        text_embedding_1 = get_embedding(text_1)
        text_embedding_2 = get_embedding(text_2)
        result = {'similarity': float(get_cos_similar(text_embedding_1, text_embedding_2).round(6))}
    return lambda_return(200, json.dumps(result))