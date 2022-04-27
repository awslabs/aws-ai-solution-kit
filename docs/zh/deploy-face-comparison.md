---
feature_id: FaceComparison
feature_name: 人脸相似度比对
feature_endpoint: face_comparison
deployment_time: 10 分钟
destroy_time: 6 分钟
sample_image: https://demo.solutions.aws.a2z.org.cn/image/sample.png
feature_description: 通过两张人脸图片中的特征向量计算欧氏距离(Euclidean Distance)，并转化为置信度，根据置信度比较，从而判断是否为同一个人。
feature_scenario: 可应用于客户身份验证、照片分类等场景，例如：自助酒店入住、人员报到、校园入口通行、相册制作。
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
|Faces    |*List*   |图像中找到的人脸列表|
|+face_hash    |*List*   |一个具有768个元素的List，为768维的人脸向量|
|+BoundingBox |*JSON*     |人脸在图像中的的坐标值，包含top，left，width，height相对全画面的百分比|
|+Confidence    |*Float*   |识别人脸置信度值，为0到1区间内Float型数值|
|FaceModelVersion    |*String*   |当前模型版本号|

- 返回示例

``` json
{
    "Faces": [
        {
            "BoundingBox": {
                "Width": 0.057923507690429685, 
                "Height": 0.10426715253778117, 
                "Left": 0.5258836364746093, 
                "Top": 0.40569204600369024
            }, 
            "Confidence": 0.8736226558685303, 
            "face_hash": [64.8125, -86.8125, -9.84375, 12.390625, 161.625, ..., 4.8046875
            ]
        }, 
        {
            "BoundingBox": {
                "Width": 0.04332921028137207, 
                "Height": 0.10577215250117152, 
                "Left": 0.1566245174407959, 
                "Top": 0.6526811308355788
            }, 
            "Confidence": 0.8055327534675598, 
            "face_hash": [61.21875, -33.84375, -36.71875, 70.625, 110.125, ..., -28.421875
            ]
        }
    ], 
    "FaceModelVersion": "1.2.0"
}
```

{%
  include-markdown "include-deploy-code.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}