---
feature_id: Image Similarity
feature_name: 图像相似度
feature_endpoint: text_similarity
deployment_time: 15 分钟
destroy_time: 10 分钟
sample_image: https://demo.solutions.aws.a2z.org.cn/image/sample.png
feature_description: 比较两幅图片是否相似，通过图片特征向量计算欧氏距离(Euclidean Distance)，并转化为置信度，根据置信度比较两张图片的相似性。
feature_scenario: 可应用于商品识别，翻拍识别，智能相册等场景。
---

{%
  include "include-deploy-description.md"
%}

{%
  include "include-deploy-lambda.md"
%}

{%
  include "include-deploy-cost.md"
%}

{%
  include "include-deploy.md"
%}

## 开始使用

{%
  include "include-call-url.md"
%}

### REST API接口参考

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| url | *String* |与 img 参数二选一，优先级高于 img|图像的 URL 地址。支持 HTTP/HTTPS 和 S3 协议。要求图像格式为 jpg/jpeg/png/bmp ，最长边不超过 4096px。|
| img | *String* |与 url 参数二选一|进行 base64 编码的图像数据|

- 请求 Body 示例

``` json
{
"url": "{{page.meta.sample_image}}"
}
```

``` json
{
"img": "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/……"
}
```

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|result    |*List*   |一个具有512个元素的List，为512维的图像向量|

- 返回示例

``` json
{
    "result": [
        -0.02555299922823906, 
        0.012955999933183193, 
        -0.10079500079154968, 
        ...
    ]
}
```

{%
  include-markdown "include-deploy-code.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}