---
feature_id: CustomOCR
feature_name: 自定义模板文字识别
feature_endpoint: custom_ocr
deployment_time: 18 Minutes
destroy_time: 20 Minutes
sample_image: Image URL address
feature_description: 客户可自定义OCR模版，提取卡证票据中结构化文字信息，并以键值对应关系的形式展现结果。
feature_scenario: 可应用于卡证票据类图片的结构化识别场景，如物流单据、发票、营业执照、行程单、火车票等。
---

{%
  include "include-deploy-description.md"
%}

## REST API Reference

#### 增加模版

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| url | *String* |Choose one of the two parameters with img, the priority is higher than the URL|Supports HTTP/HTTPS and S3 protocols. Requires the image format to be jpg/jpeg/png/bmp with the longest side not exceeding 4096px.|
| img | *String* |Choose between the url parameter|进行Base64-encoded image data|
| type | *String* |固定为add|
| template | *List* |每个元素为一个待提取区域坐标及其名称|

- Example JSON request

``` json
{
    "type": "add", 
    "url": "Image URL address", 
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
  "img": "Base64-encoded image data",
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

- Response parameters

| **Name** | **Type** | **Description**  |
|----------|-----------|------------|
|template_id    |*String*   |模版的ID|

- Example JSON response

``` json
{
    "template_id": "模版的ID",
}
```

#### 删除模版

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| template_id | *List* |已存在模版的id|
| type | *String* |固定为del|

- Example JSON request

``` json
{
    "type": "del", 
    "template_id": "已存在模版ID"
}
```

- Response parameters

| **Name** | **Type** | **Description**  |
|----------|-----------|------------|
|template_id    |*String*   |已删除模版的ID|

- Example JSON response

``` json
{
    "template_id": "已删除模版的ID",
}
```

#### 列出所有模版

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| type | *String* |固定为list|

- Example JSON request

``` json
{
    "type": "list", 
}
```

- Response parameters

| **Name** | **Type** | **Description**  |
|----------|-----------|------------|
|template_id_list    |*List*   |已存在模版的列表|

- Example JSON response

``` json
{
    "template_id_list": ["已存在模版的列表"],
}
```

#### 内容识别

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| url | *String* |Choose one of the two parameters with img, the priority is higher than the URL|Supports HTTP/HTTPS and S3 protocols. Requires the image format to be jpg/jpeg/png/bmp with the longest side not exceeding 4096px.|
| img | *String* |Choose between the url parameter|进行Base64-encoded image data|
| type | *String* |固定为query|
| template_id | *String* |已存在的模版ID|

- Example JSON request

``` json
{
  "template_id": "已存在的模版ID", 
  "url": "Image URL address"
}
```

- Response parameters

| **Name** | **Type** | **Description**  |
|----------|-----------|------------|
|key    |*String*   |字段名|
|value    |*String*   |提取到的值|
|score    |*Float*   |置信度|

- Example JSON response

``` json
[
    {
        "key": "名称", 
        "value": "亚马逊通技术服务(北京)有限公司", 
        "score": 97.98
    }, 
    {
        "key": "识别号", 
        "value": "91110116592334142D", 
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