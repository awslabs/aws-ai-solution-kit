---
feature_id: FaceDetection
feature_name: 人脸识别
feature_endpoint: face_detection
deployment_time: 9 分钟
destroy_time: 6 分钟
sample_image: https://demo.solutions.aws.a2z.org.cn/image/sample.png
feature_description: 识别人脸面部特征，将检测到的五官与轮廓关键点信息映射到64个矢量坐标上。
feature_scenario: 可应用于摄像头监控、人脸特征分析、互动营销等多种场景。
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
|+landmark_106    |*List*   |106个关键点坐标|
|++x    |*Int*   |关键点距左边缘的像素数|
|++y    |*Int*   |关键点距上边缘的像素数|
|+gender    |*String*   |性别|
|+age    |*String*   |年龄|
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
            "landmark_106": [
                {"x": 894, "y": 542}, 
                {"x": 846, "y": 461}, 
                ...
            ], 
            "gender": "male", 
            "age": 27
        }, 
        {
            "BoundingBox": {
                "Width": 0.04332921028137207, 
                "Height": 0.10577215250117152, 
                "Left": 0.1566245174407959, 
                "Top": 0.6526811308355788
            }, 
            "Confidence": 0.8055327534675598, 
            "landmark_106": [
                {"x": 306, "y": 802}, 
                {"x": 254, "y": 734}, 
                ...
            ], 
            "gender": "male", 
            "age": 35
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