---
feature_id: TextSimilarity
feature_name: 文本相似度
feature_endpoint: text_similarity
deployment_time: 15 分钟
destroy_time: 10 分钟
sample_image: 图像的URL地址
feature_description: 比较两段不同文本之间相似度，并输出一个介于0到1之间的置信度，根据置信度比较两段文字的相似性。
feature_scenario: 可应用于搜索引擎、推荐系统、机器翻译、自动应答、命名实体识别、拼写纠错等场景。
---

{%
  include "include-deploy-description.md"
%}
## API参数说明

该API支持单文本、文本对两种输入模式。

### 单文本模式

该模式输入为单个文本，返回文本的特征向量。需自行维护一个向量检索系统。适合搜索、召回等场景。

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| text | *String* |文本数据|

- 请求 Body 示例

``` json
{
  "text": "测试文本"
}
```

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|result    |*List*   |一个具有768个元素的List，为768维的文本向量|

- 返回示例
``` json
{
    "result": [
        0.025645000860095024, 
        0.001914000022225082, 
        0.007929000072181225, 
        ...
    ]
}
```

### 文本对模式

该模式输入为两个文本，返回两个文本的余弦相似度。适合相似度比较的场景。

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| text_1 | *String* |文本数据|
| text_2 | *String* |文本数据|

- 请求 Body 示例

``` json
{
  "text_1": "测试文本",
  "text_2": "测试文本"
}
```

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|similarity    |*Float*   |两个文本的余弦相似度，为0到1区间内Float型数值。越接近于1，代表文本越相似。|

- 返回示例
``` json
{
    "similarity": 0.95421
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
