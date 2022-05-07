---
feature_id: GeneralOCRTraditional
feature_name: 通用文字识别（繁体中文）
feature_endpoint: general_ocr_traditional
deployment_time: 10 分钟
destroy_time: 10 分钟
sample_image: 图像的URL地址
feature_description: 通用场景文字提取，通过返回图片中文字内容与坐标位置等信息，便于客户进行比对或结构化操作。支持识别**繁体中文**、英文、数字和常用符号。
feature_scenario: 可应用于纸质文档电子化，证件识别，内容审核等多种场景，大幅提高信息处理效率。
---

{%
  include "include-deploy-description.md"
%}
### API参数说明

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| url | *String* |与 img 参数二选一，优先级高于 img|图像的 URL 地址。支持 HTTP/HTTPS 和 S3 协议。要求图像格式为 jpg/jpeg/png/bmp ，最长边不超过 4096px。|
| img | *String* |与 url 参数二选一|进行Base64编码的图像数据|

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
|words    |*String*   |识别文本字符串内容|
|location |*JSON*     |识别文本在图像中的的坐标值，包含 top，left，width，height的整数值|
|score    |*Float*   |识别文本的置信度值，为0到1区间内 Float 型数值|

- 返回示例

``` json
[
  {
      "words": "香港永久性居民身份證",
      "location": {
          "top": 18,
          "left": 148,
          "width": 169,
          "height": 17
      },
      "score": 0.9923796653747559
  },
  {
      "words": "HONG KONG PERMANENTIDENTITYCARD",
      "location": {
          "top": 36,
          "left": 71,
          "width": 321,
          "height": 17
      },
      "score": 0.9825196266174316
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