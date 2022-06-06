---
feature_id: HumanImageSegmentation
feature_name: 智能人像分割
feature_endpoint: human_image_segmentation
deployment_time: 15 分钟
destroy_time: 9 分钟
sample_image: 图像的URL地址
feature_description: 基于AI深度学习框架识别图像中的人体轮廓，实现高精度分割，使之与背景进行分离。
feature_scenario: 可应用于照片背景替换、后期处理、证件照制作，人像抠图美化、背景虚化等多种场景。
---

{%
  include "include-deploy-description.md"
%}

## API参数说明

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| url | *String* |与 img 参数二选一|图像的 URL 地址。支持 HTTP/HTTPS 和 S3 协议。要求图像格式为 jpg/jpeg/png/bmp ，最长边不超过 4096px。|
| img | *String* |与 url 参数二选一|进行 Base64 编码的图像数据|
| type | *String* |否|当type为"foreground"时，将返回PNG格式透明背景图像Base64编码，type默认空，将返回去除背景后的图像Alpha通道Base64编码|

- 请求 Body 示例

``` json
{
"url": "{{page.meta.sample_image}}",
"type": "foreground"
}
```

``` json
{
"img": "Base64编码的图像数据",
"type": "foreground"
}
```

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|result    |*String*   |Base64编码图像数据|

- 返回示例

``` json
{
  "result": "Base64编码图像数据"
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
