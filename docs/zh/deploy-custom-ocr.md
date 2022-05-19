---
feature_id: CustomOCR
feature_name: 自定义模板文字识别
feature_endpoint: custom_ocr
deployment_time: 18 分钟
destroy_time: 20 分钟
sample_image: 图像的URL地址
feature_description: 客户可自定义OCR模版，提取卡证票据中结构化文字信息，并以键值对应关系的形式展现结果。
feature_scenario: 可应用于卡证票据类图片的结构化识别场景，如物流单据、发票、营业执照、行程单、火车票等。
---

{%
  include "include-deploy-description.md"
%}

## API参数说明

#### 增加模版

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| url | *String* |与 img 参数二选一|图像的 URL 地址。支持 HTTP/HTTPS 和 S3 协议。要求图像格式为 jpg/jpeg/png/bmp ，最长边不超过 4096px。|
| img | *String* |与 url 参数二选一|进行Base64编码的图像数据|
| type | *String* |固定为add|
| template | *List* |每个元素为一个待提取区域坐标及其名称|

- 请求 Body 示例

``` json
{
    "type": "add", 
    "url": "图像的URL地址", 
    "template": [
        [
            [[421, 465], [909, 471], [911, 503], [419, 495]], "名称"
        ], 
        [
            [[419, 495], [911, 503], [909, 533], [415, 527]], "识别号"
        ], 
        [
            [[345, 339], [595, 343], [583, 397], [341, 385]], "发票号"
        ]
    ]
}
```

``` json
{
  "type": "add", 
  "img": "Base64编码的图像数据",
  "template": [
        [
            [[421, 465], [909, 471], [911, 503], [419, 495]], "名称"
        ], 
        [
            [[419, 495], [911, 503], [909, 533], [415, 527]], "识别号"
        ], 
        [
            [[345, 339], [595, 343], [583, 397], [341, 385]], "发票号"
        ]
    ]
}
```

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|template_id    |*String*   |模版的ID|

- 返回示例

``` json
{
    "template_id": "模版的ID",
}
```

#### 删除模版

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| template_id | *List* |已存在模版的id|
| type | *String* |固定为del|

- 请求 Body 示例

``` json
{
    "type": "del", 
    "template_id": "已存在模版ID"
}
```

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|template_id    |*String*   |已删除模版的ID|

- 返回示例

``` json
{
    "template_id": "已删除模版的ID"
}
```

#### 列出所有模版

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| type | *String* |固定为list|

- 请求 Body 示例

``` json
{
    "type": "list"
}
```

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|template_id_list    |*List*   |已存在模版的列表|

- 返回示例

``` json
{
    "template_id_list": ["已存在模版的列表"]
}
```

#### 内容识别

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| url | *String* |与 img 参数二选一|图像的 URL 地址。支持 HTTP/HTTPS 和 S3 协议。要求图像格式为 jpg/jpeg/png/bmp ，最长边不超过 4096px。|
| img | *String* |与 url 参数二选一|进行Base64编码的图像数据|
| type | *String* |固定为query|
| template_id | *String* |已存在的模版ID|

- 请求 Body 示例

``` json
{
  "template_id": "已存在的模版ID",
  "url": "图像的URL地址"
}
```

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|key    |*String*   |字段名|
|value    |*String*   |提取到的值|
|score    |*Float*   |置信度|

- 返回示例

``` json
[
    {
        "key": "名称", 
        "value": "亚马逊通技术服务(北京)有限公司", 
        "score": 97.98
    }, 
    {
        "key": "识别号", 
        "value": "911101165900000000", 
        "score": 99.62
    }, 
    {
        "key": "发票号", 
        "value": "4403212222", 
        "score": 96.58
    }
]
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