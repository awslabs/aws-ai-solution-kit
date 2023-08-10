---
feature_id: GeneralNLU
feature_name: General NLU
feature_endpoint: general_nlu
deployment_time: 15 Minutes
destroy_time: 10 Minutes
sample_image: Image URL address
feature_description: Support a variety of Chinese text understanding tasks, such as text classification, sentiment analysis, extraction, and customizable labeling systems.
feature_scenario: Used in scenarios such as text classification, sentiment analysis, text matching, and entity recognition.
---

{%
include "include-deploy-description.md"
%}

!!! Info "Note"
In v1.4.0, General NLU API only support Chinese language processing.

## API reference

### Text classification

- HTTP request method: `POST`

- Request body parameters

| **Name**     | **Type** | **Required** | **Description**                                                |
|--------------|----------|--------------|----------------------------------------------------------------|
| subtask_type | *String* | Yes          | Fixed as "Text Classification"                                 |
| text         | *String* | Yes          | The text to be classified                                      |
| choices      | *List*   | Yes          | Candidate labels, please refer to the **Request Body Example** |
| question     | *String* | Yes          | Prompts the model for guidance                                 |

- Example Request

**Example 1**

``` json
{
    "subtask_type": "文本分类",
    "text": "待分类的文本",
    "choices": [{
        "entity_type": "投资",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "科技",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "体育",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "美食",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "旅游",
        "label": 0,
        "entity_list": []
    }],
    'question': '这是篇什么类型的新闻'
}
```

**Example 2**

``` json
{
    "subtask_type": "文本分类",
    "text": "待分类的文本",
    "choices": [{
        "entity_type": "农业工程",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "哲学",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "教育学",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "理学",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "农学",
        "label": 0,
        "entity_list": []
    }],
    'question': '这篇文章属于哪个学科'
}
```

- Response parameters

| **Name** | **Type** | **Description**                                                                                                                                                      |
|----------|----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| result   | *Dict*   | Same format as the request parameters, with the label of the corresponding option set to 1 and an added score. Please refer to the **Response Example** for details. |

- Example JSON response

**Example 1 Response**

Assuming the model returns the category of the "unclassified text" as "sports."

``` json
{
    "subtask_type": "文本分类",
    "text": "待分类的文本",
    "choices": [{
        "entity_type": "投资",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "科技",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "体育",
        "label": 1,
        "entity_list": [],
        "score": 0.91592306
    }, {
        "entity_type": "美食",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "旅游",
        "label": 0,
        "entity_list": []
    }],
    'question': '这是篇什么类型的新闻'
}
```

**Example 2 Response**

``` json
{
    "subtask_type": "文本分类",
    "text": "待分类的文本",
    "choices": [{
        "entity_type": "农业工程",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "哲学",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "教育学",
        "label":1,
        "entity_list": [],
        "score": 0.91592306
    }, {
        "entity_type": "理学",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "农学",
        "label": 0,
        "entity_list": []
    }],
    'question': '这篇文章属于哪个学科'
}
```

### sentiment analysis

- HTTP request method: `POST`

- Request body parameters

| **Name**     | **Type** | **Required** | **Description**                                                          |
|--------------|----------|--------------|--------------------------------------------------------------------------|
| subtask_type | *String* | Yes          | Fixed as "Sentiment Classification"                                      |
| text         | *String* | Yes          | The text to be classified                                                |
| choices      | *List*   | Yes          | Candidate sentiment labels, please refer to the **Request Body Example** |
| question     | *String* | Yes          | Prompts the model for guidance                                           |

- Example Request

``` json
{
    "subtask_type": "情感分类",
    "text": "待分类的用户评论",
    "choices": [{
        "entity_type": "积极",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "中性",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "消极",
        "label": 0,
        "entity_list": []
    }],
    'question': '这句话的情感极性是什么'
}

```

- Response parameters

| **Name** | **Type** | **Description**                                                                                                                                                      |
|----------|----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| result   | *Dict*   | Same format as the request parameters, with the label of the corresponding option set to 1 and an added score. Please refer to the **Response Example** for details. |

- Example JSON response

Assuming the model returns the sentiment polarity of the "unclassified user comment" as "neutral."

``` json
{
    "subtask_type": "情感分类",
    "text": "待分类的用户评论",
    "choices": [{
        "entity_type": "积极",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "中性",
        "label": 1,
        "entity_list": [],
        "score": 0.91592306
    }, {
        "entity_type": "消极",
        "label": 0,
        "entity_list": []
    }],
    'question': '这句话的情感极性是什么'
}
```

### Text matching

- HTTP request method: `POST`

- Request body parameters

| **Name**     | **Type** | **Required** | **Description**                                                                                                                                                                                                                             |
|--------------|----------|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| subtask_type | *String* | Yes          | Fixed as "Text Matching"                                                                                                                                                                                                                    |
| text         | *String* | Yes          | The first text                                                                                                                                                                                                                              |
| choices      | *List*   | Yes          | The entity_type of each element is the concatenation of the prompt word with the second text, for example, "can be inferred: second text" or "can be understood as: second text". Please refer to the **Request Body Example** for details. |
| question     | *String* | Yes          | Prompts the model for guidance                                                                                                                                                                                                              |

- Example Request

**Example 1**

``` json
{
    "subtask_type": "文本匹配",
    "text": "在白云的蓝天下，一个孩子伸手摸着停在草地上的一架飞机的螺旋桨。",
    "choices": [{
        "entity_type": "可以推断出：一个孩子正伸手摸飞机的螺旋桨。",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "不能推断出：一个孩子正伸手摸飞机的螺旋桨。",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "很难推断出：一个孩子正伸手摸飞机的螺旋桨。",
        "label": 0,
        "entity_list": []
    }],
    'question': '同义文本'
}

```

**Example 2**

``` json
{
    "subtask_type": "文本匹配",
    "text": "您好，我还款了怎么还没扣款",
    "choices": [{
        "entity_type": "可以理解为：今天一直没有扣款",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "不能理解为：今天一直没有扣款",
        "label": 0,
        "entity_list": []
    }],
    'question': '同义文本'
}
```

- Response parameters

| **Name** | **Type** | **Description**                                                                                                                                                      |
|----------|----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| result   | *Dict*   | Same format as the request parameters, with the label of the corresponding option set to 1 and an added score. Please refer to the **Response Example** for details. |

- Example JSON response

**Example 1 response**

``` json
{
    "subtask_type": "文本匹配",
    "text": "在白云的蓝天下，一个孩子伸手摸着停在草地上的一架飞机的螺旋桨。",
    "choices": [{
        "entity_type": "可以推断出：一个孩子正伸手摸飞机的螺旋桨。",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "不能推断出：一个孩子正伸手摸飞机的螺旋桨。",
        "label": 1,
        "entity_list": [],
        "score": 0.91592306
    }, {
        "entity_type": "很难推断出：一个孩子正伸手摸飞机的螺旋桨。",
        "label": 0,
        "entity_list": []
    }],
    'question': '同义文本'
}

```

**Example 2 response**

``` json
{
    "subtask_type": "文本匹配",
    "text": "您好，我还款了怎么还没扣款",
    "choices": [{
        "entity_type": "可以理解为：今天一直没有扣款",
        "label": 1,
        "entity_list": [],
        "score": 0.91592306
    }, {
        "entity_type": "不能理解为：今天一直没有扣款",
        "label": 0,
        "entity_list": []
    }],
    'question': '同义文本'
}
```

### Entity recognition

- HTTP request method: `POST`

- Request body parameters

| **Name**     | **Type** | **Required** | **Description**                                                                                                                          |
|--------------|----------|--------------|------------------------------------------------------------------------------------------------------------------------------------------|
| subtask_type | *String* | Yes          | Fixed as "Entity Recognition"                                                                                                            |
| text         | *String* | Yes          | The text to be classified                                                                                                                |
| choices      | *List*   | Yes          | The entity_type of each element represents the desired entity type to extract. Please refer to the **Request Body Example** for details. |

- Example Request

``` json
{
    "subtask_type": "实体识别",
    "text": "我们是首家支持英特尔、AMD 和 Arm 处理器的主要云提供商",
    "choices": [{
        "entity_type": "地址",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "公司名",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "人物姓名",
        "label": 0,
        "entity_list": []
    }]
}

```

- Response parameters

| **Name** | **Type** | **Description**                                                                                                                                                                                  |
|----------|----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| result   | *Dict*   | Same format as the request parameters, with the entity_list corresponding to the extracted entities added with their content and position. Please refer to the **Response Example** for details. |

- Example JSON response

Assuming the model returns the sentiment polarity of the "unclassified user comment" as "neutral."

``` json
{
    "subtask_type": "实体识别",
    "text": "我们是首家支持英特尔、AMD 和 Arm 处理器的主要云提供商",
    "choices": [{
        "entity_type": "地址",
        "label": 0,
        "entity_list": []
    }, {
        "entity_type": "公司名",
        "label": 0,
        "entity_list": [{
            "entity_name":"英特尔",
            "entity_type":"公司名",
            "entity_idx":[
                [7, 9]
            ]
        },{
            "entity_name":"AMD",
            "entity_type":"公司名",
            "entity_idx":[
                [11, 13]
            ]
        }]
    }, {
        "entity_type": "人物姓名",
        "label": 0,
        "entity_list": []
    }]
}
```

{%
include-markdown "include-deploy-code.md"
%}

{%
include "include-deploy-cost-8GB.md"
%}

{%
include-markdown "include-deploy-uninstall.md"
%}
