---
feature_id: FaceDetection
feature_name: Face Detection
feature_endpoint: face_detection
deployment_time: 9 Minutes
destroy_time: 6 Minutes
sample_image: Image URL address
feature_description: Detect the face in a image and return coordinate information of the face.
feature_scenario: It can be applied to a variety of scenarios such as camera monitoring, face feature analysis, and interactive marketing.
---

{%
  include "include-deploy-description.md"
%}
## REST API Reference

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| url | *String* |Choose one of the two parameters with img, the priority is higher than the URL|Supports HTTP/HTTPS and S3 protocols. Requires the image format to be jpg/jpeg/png/bmp with the longest side not exceeding 4096px.|
| img | *String* |Choose between the url parameter|进行Base64-encoded image data|

- Example JSON request

``` json
{
  "url": "{{page.meta.sample_image}}"
}
```

``` json
{
  "img": "Base64-encoded image data"
}
```

- Response parameters

| **Name** | **Type** | **Description**  |
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

- Example JSON response

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
  include "include-deploy-cost.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}