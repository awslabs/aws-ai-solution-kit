import json
import os
import numpy as np
import onnxruntime
from tokenizer import CPMAntTokenizer
import unicodedata
from aikits_utils import lambda_return

tokenizer = CPMAntTokenizer()
    
model_path = os.environ['MODEL_PATH']
ort_session = onnxruntime.InferenceSession(model_path + "/nlu.onnx", providers=['CUDAExecutionProvider'])

def sigmoid(x):
    """
    Compute the sigmoid of x

    Arguments:
    x -- A scalar or numpy array of any size

    Return:
    s -- sigmoid(x)
    """
    
    ### START CODE HERE ### (≈ 1 line of code)
    s = 1 / (1 + np.exp(-x))
    ### END CODE HERE ###
    
    return s
class OffsetMapping:
    def __init__(self):
        self._do_lower_case = False

    @staticmethod
    def stem(token):
        if token[:2] == '##':
            return token[2:]
        else:
            return token

    @staticmethod
    def _is_control(ch):
        return unicodedata.category(ch) in ('Cc', 'Cf')

    @staticmethod
    def _is_special(ch):
        return bool(ch) and (ch[0] == '[') and (ch[-1] == ']')

    def rematch(self, text, tokens):
        if self._do_lower_case:
            text = text.lower()

        normalized_text, char_mapping = '', []
        for i, ch in enumerate(text):
            if self._do_lower_case:
                ch = unicodedata.normalize('NFD', ch)
                ch = ''.join(
                    [c for c in ch if unicodedata.category(c) != 'Mn'])
            ch = ''.join([
                c for c in ch
                if not (ord(c) == 0 or ord(c) == 0xfffd or self._is_control(c))
            ])
            normalized_text += ch
            char_mapping.extend([i] * len(ch))

        text, token_mapping, offset = normalized_text, [], 0
        for token in tokens:
            if self._is_special(token):
                token_mapping.append([offset])
                offset += 1
            else:
                token = self.stem(token)
                print(text[offset:], token)
                start = text[offset:].index(token) + offset
                end = start + len(token)
                token_mapping.append(char_mapping[start:end])
                offset = end

        return token_mapping
def extract_index(span_logits, sample_length, split_value=0.5):
    result = []
    sample_length = sample_length if sample_length < span_logits.shape[0] else span_logits.shape[0]
    for i in range(sample_length):
        for j in range(i, sample_length):
            if span_logits[i, j] > split_value:
                result.append((i, j, span_logits[i, j]))
    return result
def extract_entity(text, entity_idx, text_mapping):
    start_split = text_mapping[entity_idx[0]] if entity_idx[0] < len(text_mapping) and entity_idx[0] >= 0 else []
    end_split = text_mapping[entity_idx[1]] if entity_idx[1] < len(text_mapping) and entity_idx[1] >= 0 else []
    entity = ''
    if start_split != [] and end_split != []:
        entity = text[start_split[0]:end_split[-1]+1]
    return entity

def handler(event, context):
    if 'body' not in event:
        return lambda_return(400, 'invalid param')
    try:
        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event['body']
        
        predict_data = body
        
    except:
        return lambda_return(400, 'invalid param')

    prompt_length=32
    max_length=256
    item = predict_data
    input_ids0 = []
    attention_mask0 = []
    token_type_ids0 = []
    span_labels_masks0 = []
    task_type = item["subtask_type"]
    option_list = item["choices"]
    if task_type == '实体识别':
        task_id = 1
        option_tag = '类型'
    elif task_type == '文本分类':
        task_id = 2
        option_tag = '选项'
    elif task_type == '情感分类':
        task_id = 3
        option_tag = '情感'
    elif task_type == '数学计算':
        task_id = 4
        option_tag = '公式'
    elif task_type == '文本匹配':
        task_id = 5
        option_tag = '选项'
    elif task_type == '语义匹配':
        task_id = 5
        option_tag = '选项'
    elif task_type == '事件抽取':
        task_id = 5
        option_tag = '抽取项'
    elif task_type == '阅读理解':
        task_id = 5
        option_tag = '问题'

    text = item["text"]

    question = item.get("question", '')
    if len(question):
        if question[0] != '[':
            question = '[问题]' + question
        text += question
    input_ids = [tokenizer.bos_id] + tokenizer.encode(text)
    res = {}
    res["input"] = []
    res["length"] = []
    res["position"] = []
    res["span"] = []
    res["context"] = []
    res["segment"] = []
    res["span_label_mask"] = []
    for option_idx, option in enumerate(option_list):
        cur_input_ids = (
            input_ids + tokenizer.encode(f'[{option_tag}]') + tokenizer.encode(option["entity_type"])# + tokenizer.encode("[是否正确]")
        )
        if prompt_length + len(cur_input_ids) > max_length:
            tr_input_length = max_length - prompt_length
            assert tr_input_length > 0
            cur_input_ids = [tokenizer.bos_id] + cur_input_ids[-tr_input_length-1:]
        ids = [
            x + prompt_length * task_id for x in range(prompt_length)
        ] + cur_input_ids
        res["input"].append(ids)
        res["length"].append(len(ids))
        res["position"].append(list(range(len(ids))))
        res["span"].append([0] * len(ids))
        res["context"].append([True] * len(ids))
        res["segment"].append([0] * prompt_length + [2] * len(cur_input_ids))
        span_label_mask = np.zeros((len(cur_input_ids), len(cur_input_ids)))-10000
        if task_type in ('文本分类', '情感分类', '数学计算', '文本匹配'):
            span_label_mask[0, 0] = 0
        elif task_type in ('实体识别', '事件抽取', '阅读理解'):
            question_len = len(cur_input_ids)
            span_label_mask[1:question_len,1:question_len] = 0
        res["span_label_mask"].append(span_label_mask)
    for key in res:
        for i in range(len(res[key])):
            if key in ("span_label", "span_label_mask"):
                res[key][i] = np.array(res[key][i],dtype='float32')
            else:
                res[key][i] = np.array(res[key][i],dtype='int32')
    cur_max_length = max([row.shape[0] for row in res["input"]])
    for k,v in res.items():
        if k == "span_label_mask":
            padding_value = -10000
        else:
            padding_value = 0
        dim = len(v[0].shape)
        dtype = v[0].dtype
        batch_size = len(v)
        if dim == 1:
            tensor = np.zeros((batch_size, cur_max_length), dtype=dtype) + padding_value
            for i in range(batch_size):
                tensor[i, :len(v[i])] = v[i]
        elif dim == 2:
            tensor = np.zeros((batch_size, cur_max_length-32, cur_max_length-32), dtype=dtype) + padding_value
            for i in range(batch_size):
                tensor[i, :v[i].shape[0], :v[i].shape[1]] = v[i]
        else:
            tensor = np.array(v, dtype=dtype)
        res[k] = np.expand_dims(tensor, 0)
    span_logits = ort_session.run(None, res)
    span_logits = sigmoid(span_logits[0])
    if item["subtask_type"] in ('文本分类', '情感分类', '数学计算', '文本匹配'):
        cls_idx = 0
        max_c = np.argmax(span_logits[0, :, cls_idx, cls_idx])
        predict_data['choices'][max_c]['label'] = 1
        predict_data['choices'][max_c]['score'] = float(span_logits[0,max_c, cls_idx, cls_idx])
    else:
        textb = item['text']
        offset_mapping = OffsetMapping().rematch(textb, tokenizer.tokenize(textb))
        for c in range(len(item['choices'])):
            logits = span_logits[0, c, :, :]
            entity_name_list = []
            entity_list = []
            sample_length = len(input_ids)
            entity_idx_type_list = extract_index(logits, sample_length, split_value=0.5)
            for entity_idx in entity_idx_type_list:
                entity = extract_entity(
                    item['text'], (entity_idx[0]-1, entity_idx[1]-1), offset_mapping)

                if entity not in entity_name_list:

                    entity_name_list.append(entity)

                    entity = {
                        'entity_name': entity,
                        'score': float(entity_idx[2])
                    }
                    entity_list.append(entity)
            predict_data['choices'][c]['entity_list'] = entity_list
    result = {'result': predict_data}
    return lambda_return(200, json.dumps(result))