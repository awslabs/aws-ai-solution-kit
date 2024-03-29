---
feature_id: CustomOCR
feature_name: 自定义模板文字识别
feature_endpoint: custom_ocr
deployment_time: 18 分钟
destroy_time: 20 分钟
sample_image: 图像的URL地址
feature_description: 客户可自定义OCR模板，提取卡证票据中结构化文字信息，并以键值对应关系的形式展现结果。
feature_scenario: 可应用于卡证票据类图片的结构化识别场景，如物流单据、发票、营业执照、行程单、火车票等。
---

{%
  include "include-deploy-description.md"
%}

## API参数说明

### 增加模板

进行文字识别之前，您需要通过**增加模板API**创建模板。为了提高文字识别准确性，请选择与被识别图像细节近似并且文字内容清晰的图片创建模板。同一个模板可以包含多个识别区域。

要创建模板，每个待识别区域都需要指定矩形框的四个坐标点和该区域的名称，您可以使用常见的图像处理软件来辅助获取坐标点，或者使用本方案工具来创建模版。以下为本方案工具来说明：

1. 点击工具[链接](https://awslabs.github.io/aws-ai-solution-kit/zh/tools/custom-template/index.htm)。
2. 点击**选择本地图片**。
3. 把鼠标移动到图片上，对待识别内容，点击左上角，然后滑动鼠标到右下角，释放鼠标，在弹出的对话框中输入对应的标识名。
4. 如果有多个待识别内容，重复第3步。
5. 点击**复制结果到剪贴板**，此内容为请求Body，创建自定义模板，并在创建成功后记录的模板ID。
6. 创建好模板后，首先用原图片和模板ID进行文字识别测试，以确保模板能够准确识别到所需信息。
7. （可选）如果发现提取信息不完整的情况，请确认坐标点是否标注正确，并适当扩大识别区域重新创建模板。 


!!! Important "重要说明"
    矩形框区域必须完全覆盖要识别的文字内容，请在不遮盖其他识别矩形区域的前提下，在识别区域四边留出足够的容错空间，从而获得准确的识别能力。

以下为API的参数说明。

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| url | *String* |与 img 参数二选一|图像的 URL 地址。支持 HTTP/HTTPS 和 S3 协议。要求图像格式为 jpg/jpeg/png/bmp ，最长边不超过 4096px。|
| img | *String* |与 url 参数二选一|进行Base64编码的图像数据|
| type | *String* |是|增加模板需要将*type*指定为*add*|
| template | *List* |是|每个元素为一个待提取区域坐标及其名称，请参考 **请求 Body 示例**。|

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
|template_id    |*String*   |模板的ID|

- 返回示例

``` json
{
    "template_id": "模板的ID",
}
```
### 内容识别

在创建好模板后，可以通过对应的模板 ID 对图片进行文字识别，返回值为模板中识别区域名称与文本内容。

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| url | *String* |与 img 参数二选一|图像的 URL 地址。支持 HTTP/HTTPS 和 S3 协议。要求图像格式为 jpg/jpeg/png/bmp ，最长边不超过 4096px。|
| img | *String* |与 url 参数二选一|进行Base64编码的图像数据|
| type | *String* |固定为query|
| template_id | *String* |已存在的模板ID|

- 请求 Body 示例

``` json
{
  "template_id": "已存在的模板ID",
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
### 删除模板

如果需要删除模板，可通过指定需要删除的模板 ID 进行删除。请注意，模板被删除后不能恢复。

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| template_id | *List* |已存在模板的id|
| type | *String* |固定为del|

- 请求 Body 示例

``` json
{
    "type": "del", 
    "template_id": "已存在模板ID"
}
```

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|template_id    |*String*   |已删除模板的ID|

- 返回示例

``` json
{
    "template_id": "已删除模板的ID"
}
```
### 列出所有模板

可以把已经创建的模板通过 ID 列表的方式列出。

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
|template_id_list    |*List*   |已存在模板的列表|

- 返回示例

``` json
{
    "template_id_list": ["已存在模板的列表"]
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