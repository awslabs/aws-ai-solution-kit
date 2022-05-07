---
feature_id: CarLicensePlate
feature_name: 车牌信息识别
feature_endpoint: car_license_plate
deployment_time: 9 分钟
destroy_time: 6 分钟
sample_image: 图像的URL地址
feature_description: 识别中华人民共和国境内常见机动车号牌，提取机动车号牌信息中的地区编号和车牌号。
feature_scenario: 可应用于停车场、小区自动识别车辆号牌信息，或车辆违章信息检测等场景。
---

{%
  include "include-deploy-description.md"
%}

## API参数说明

- HTTP 方法: `POST`

- Body 请求参数

  | **名称**  | **类型**  | **是否必选** |  **说明**  |
  |----------|-----------|------------|------------|
  | url | *String* |与 img 参数二选一，优先级高于 img|图像的 URL 地址。支持 HTTP/HTTPS 和 S3 协议。要求图像格式为 jpg/jpeg/png/bmp ，最长边不超过 4096px。|
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
|words    |*String*   |识别车牌内容|
|location |*JSON*     |识别车牌在图像中的的坐标值，包含top，left，width，height的整数值|
|score    |*Float*   |识别车牌的置信度值，为0到1区间内Float型数值|

- 返回示例

``` json
[
  {
      "words": "京C45678",
      "location": {
          "top": 18,
          "left": 148,
          "width": 169,
          "height": 17
      },
      "score": 0.9923796653747559
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