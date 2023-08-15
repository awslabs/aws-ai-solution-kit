---
feature_id: GeneralNLU
feature_name: General NLU
feature_endpoint: general_nlu
deployment_time: 15 Minutes
destroy_time: 10 Minutes
sample_image: 图像的URL地址
feature_description: 支持各种中文文本理解任务，如文本分类、情感分析、提取和可定制的标签系统。
feature_scenario: 用于文本分类、情感分析、文本匹配和实体识别等场景。
---

{%
  include "include-deploy-description.md"
%}
## API参数说明

该API支持文本分类、情感分类、文本匹配和实体识别，共4大类任务。该API在不同的任务下有不同的输入参数。

### 文本分类

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| subtask_type | *String* | 是 |固定为“文本分类”|
| text | *String* | 是 |待分类的文本|
| choices | *List* | 是 |候选标签，请参考 **请求 Body 示例**。|
| question | *String* | 是 |用于指导模型的提示文本|

- 请求 Body 示例

例子1:

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

例子2:

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

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|result    |*Dict*   |与请求参数同格式，对应选项的label被置为1，同时增加score。请参考 **返回示例**。|

- 返回示例


例子1的返回:

假设模型返回"待分类的文本"的类别为“体育”。

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

例子2的返回:
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

### 情感分类

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| subtask_type | *String* | 是 |固定为“情感分类”|
| text | *String* | 是 |待分类的文本|
| choices | *List* | 是 |候选情感标签，请参考 **请求 Body 示例**。|
| question | *String* | 是 |用于指导模型的提示文本|

- 请求 Body 示例

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

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|result    |*Dict*   |与请求参数同格式，对应选项的label被置为1，同时增加score。请参考 **返回示例**。|

- 返回示例

假设模型返回"待分类的用户评论"的情感极性为“中性”。

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

### 文本匹配

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| subtask_type | *String* | 是 |固定为“文本匹配”|
| text | *String* | 是 |第一个文本|
| choices | *List* | 是 |每个元素的entity_type是提示词与第二个文本的拼接，例如“可以推断出：第二个文本”或“可以理解为：第二个文本”，请参考 **请求 Body 示例**。|
| question | *String* | 是 |用于指导模型的提示文本|

- 请求 Body 示例

例子1：

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

例子2：

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

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|result    |*Dict*   |与请求参数同格式，对应选项的label被置为1，同时增加score。请参考 **返回示例**。|

- 返回示例

例子1的返回：

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

例子2的返回：

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

### 实体识别

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| subtask_type | *String* | 是 |固定为“实体识别”|
| text | *String* | 是 |待分类的文本|
| choices | *List* | 是 |每个元素的entity_type是想要提取的实体类型。请参考 **请求 Body 示例**。|

- 请求 Body 示例

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

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|result    |*Dict*   |与请求参数同格式，对应实体的entity_list会增加抽取到的实体内容及位置。请参考 **返回示例**。|

- 返回示例

假设模型返回"待分类的用户评论"的情感极性为“中性”。

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

## 成本预估

您需要承担运行解决方案时使用亚马逊云科技各个服务的成本费用。截至这次发布的版本，影响解决方案的成本因素主要包括：

- AWS Lambda调用次数
- AWS Lambda运行时间
- Amazon API Gateway调用次数
- Amazon API Gateway数据输出量
- Amazon CloudWatch Logs存储量
- Amazon Elastic Container Registry存储量

!!! Note "说明"
    Amazon SageMaker相关的费用仅适用于图像超分辨率方案。

## 成本预估示例1 

以由西云数据运营的亚马逊云科技中国（宁夏）区域（cn-northwest-1）为例，处理时间1秒

使用本方案处理此文本所需的成本费用如下表所示：

| 服务                                  | 用量                  | 费用      |
|-------------------------------------|---------------------|---------|
| AWS Lambda                     | 调用百万次                 | ¥1.36   |
| AWS Lambda                     | 内存8192MB，每次运行1秒     | ¥907.8  |
| Amazon API Gateway                | 调用百万次                 | ¥28.94  |
| Amazon API Gateway             | 数据输出以每次10KB计算，¥0.933/GB | ¥9.33   |
| Amazon CloudWatch Logs              | 每次10KB，¥6.228/GB    | ¥62.28  |
| Amazon Elastic Container Registry | 0.5GB存储，每月每GB¥0.69    | ¥0.35   |
| 合计                                  |   | ¥1010.06 |

## 成本预估示例2

以美国东部（俄亥俄州）区域（us-east-2）为例，处理时间1秒

使用本方案处理此文本所需的成本费用如下表所示：

| 服务                                  | 用量                 | 费用     |
|-------------------------------------|--------------------|--------|
| Amazon Lambda                     | 调用百万次                | $0.20  |
| Amazon Lambda                     | 内存8192MB，每次运行1秒    | $133.3  |
| Amazon API Gateway                | 调用百万次                | $3.5   |
| Amazon API Gateway             | 数据输出以每次10KB计算，$0.09/GB | $0.9   |
| Amazon CloudWatch Logs              | 每次10KB，$0.50/GB    | $5     |
| Amazon Elastic Container Registry | 0.5GB存储，每月每GB$0.1    | $0.05  |
| 合计                                  |   | $142.95 |

{%
  include-markdown "include-deploy-uninstall.md"
%}
