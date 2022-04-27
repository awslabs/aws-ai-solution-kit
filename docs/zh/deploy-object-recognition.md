---
feature_id: ObjectRecognition
feature_name: 通用物体识别
feature_endpoint: object_recognition
deployment_time: 15 分钟
destroy_time: 10 分钟
sample_image: https://demo.solutions.aws.a2z.org.cn/image/sample.png
feature_description: 检测图像中的通用对象主体，返回该对象主体的区域信息与置信度。支持识别60类物体。
feature_scenario: 可应用于IPC图像检测、交通、安防等行业中图像场景的目标检测与跟踪。
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
|Labels    |*List*   |图像中找到的目标列表|
|+Name    |*String*   |目标类别名|
|+Instances    |*List*   |类别实例列表|
|++BoundingBox |*JSON*     |实例在图像中的的坐标值，包含top，left，width，height相对全画面的百分比|
|++Confidence    |*Float*   |实例的置信度，0-100|
|+Confidence    |*Int*   |当前类别实例置信度的最大值|
|LabelModelVersion    |*String*   |当前模型版本号|

- 返回示例
``` json
{
    "Labels": [
        {
            "Name": "car_(automobile)", 
            "Confidence": 67.87780523300171, 
            "Instances": [
                {
                    "BoundingBox": {
                        "Width": 1.0013043403596384, 
                        "Height": 0.9958885181613408, 
                        "Left": -0.00021715163893532008, 
                        "Top": 0.00033918747441136817
                    }, 
                    "Confidence": 67.87780523300171
                }
            ]
        }, 
        {
            "Name": "mirror", 
            "Confidence": 59.2678964138031, 
            "Instances": [
                {
                    "BoundingBox": {
                        "Width": 0.14041614532470703, 
                        "Height": 0.29166373257057565, 
                        "Left": 0.2743588984012604, 
                        "Top": 0.2794425819140053
                    }, 
                    "Confidence": 59.2678964138031
                }
            ]
        }, 
        {
            "Name": "window", 
            "Confidence": 16.396354138851166, 
            "Instances": [
                {
                    "BoundingBox": {
                        "Width": 0.44319993257522583, 
                        "Height": 0.6673663154702585, 
                        "Left": 0.5509995222091675, 
                        "Top": 0.015529238811174562
                    }, 
                    "Confidence": 16.396354138851166
                }
            ]
        }
    ], 
    "LabelModelVersion": "1.2.0"
}
```

{%
  include-markdown "include-deploy-code.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}