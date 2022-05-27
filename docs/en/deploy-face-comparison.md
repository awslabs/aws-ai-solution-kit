---
feature_id: FaceComparison
feature_name: Face Comparison
feature_endpoint: face_comparison
deployment_time: 10 Minutes
destroy_time: 6 Minutes
sample_image: Image URL address
feature_description: Compare two faces of same person and return a confidence score of the similarity
feature_scenario: 可应用于客户身份验证、照片分类等场景，例如：自助酒店入住、人员报到、校园入口通行、相册制作。
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
|+face_hash    |*List*   |一个具有768个元素的List，为768维的人脸向量|
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
  include "include-deploy-cost.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}