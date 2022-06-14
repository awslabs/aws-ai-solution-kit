---
feature_id: Image Similarity
feature_name: 图像相似度
feature_endpoint: text_similarity
deployment_time: 15 分钟
destroy_time: 10 分钟
sample_image: 图像的URL地址
feature_description: 比较两幅图片是否相似，通过图片特征向量计算余弦距离，并转化为置信度，根据置信度比较两张图片的相似性。
feature_scenario: 可应用于商品识别，翻拍识别，智能相册等场景。
---

{%
  include "include-deploy-description.md"
%}

## API参数说明

该API支持单图片、图片对两种输入模式。

### 单张图片模式

该模式输入为单张图片，返回图片的特征向量。需自行维护一个向量检索系统。适合搜索、召回等场景。

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| url | *String* |与 img 参数二选一|图像的 URL 地址。支持 HTTP/HTTPS 和 S3 协议。要求图像格式为 jpg/jpeg/png/bmp ，最长边不超过 4096px。|
| img | *String* |与 url 参数二选一|进行 Base64 编码的图像数据|

- 请求 Body 示例

``` json
{
"url": "{{page.meta.sample_image}}"
}
```

``` json
{
"img": "Base64编码的图像数据"
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

### 两张图片模式

该模式输入为两张图片，返回两张图片的余弦相似度。适合相似度比较的场景。

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| url_1 | *String* |与 img_1 参数二选一|图像的 URL 地址。支持 HTTP/HTTPS 和 S3 协议。要求图像格式为 jpg/jpeg/png/bmp ，最长边不超过 4096px。|
| img_1 | *String* |与 url_1 参数二选一|进行 Base64 编码的图像数据|
| url_2 | *String* |与 img_2 参数二选一|图像的 URL 地址。支持 HTTP/HTTPS 和 S3 协议。要求图像格式为 jpg/jpeg/png/bmp ，最长边不超过 4096px。|
| img_2 | *String* |与 url_2 参数二选一|进行 Base64 编码的图像数据|

- 请求 Body 示例

``` json
{
"url_1": "{{page.meta.sample_image}}",
"url_2": "{{page.meta.sample_image}}"
}
```

``` json
{
"img_1": "Base64编码的图像数据",
"img_2": "Base64编码的图像数据"
}
```

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|similarity    |*Float*   |两张图片的余弦相似度，为0到1区间内Float型数值。越接近于1，代表图片越相似。|

- 返回示例

``` json
{
    "similarity": 0.95421
}
```

{%
  include-markdown "include-deploy-code.md"
%}

{%
  include "include-deploy-cost-10GB.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}