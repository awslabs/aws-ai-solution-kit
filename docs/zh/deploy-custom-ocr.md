---
feature_id: CustomOCR
feature_name: 自定义模板文字识别
feature_endpoint: custom_ocr
deployment_time: 18 分钟
destroy_time: 20 分钟
sample_image: https://demo.solutions.aws.a2z.org.cn/image/sample.png
feature_description: 客户可自定义OCR模版，提取卡证票据中结构化文字信息，并以键值对应关系的形式展现结果。
feature_scenario: 可应用于卡证票据类图片的结构化识别场景，如物流单据、发票、营业执照、行程单、火车票等。
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
|words    |*String*   |识别文本字符串内容|
|location |*JSON*     |识别文本在图像中的的坐标值，包含top，left，width，height的整数值|
|score    |*Float*   |识别文本的置信度值，为0到1区间内Float型数值|

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
  include-markdown "include-deploy-uninstall.md"
%}