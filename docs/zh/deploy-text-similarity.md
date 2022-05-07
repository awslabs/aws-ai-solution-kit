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

{%
  include-markdown "include-deploy-code.md"
%}

{%
  include "include-deploy-cost.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}
