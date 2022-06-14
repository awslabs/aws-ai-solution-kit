---
feature_id: FaceDetection
feature_name: Face Detection
feature_endpoint: face_detection
deployment_time: 9 Minutes
destroy_time: 6 Minutes
sample_image: Image URL address
feature_description: Detect the face in an image, and map the detected facial features and contour key point information to 64 vector coordinates. 
feature_scenario: Applicable to a variety of scenarios such as camera monitoring, facial feature analysis, and interactive marketing.
---

{%
  include "include-deploy-description.md"
%}
## API reference

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| url | *String* |Choose url or img.|Image URL address, which supports HTTP/HTTPS and S3 protocols. Supported image formats are jpg/jpeg/png/bmp, with the longest side not exceeding 4096px.|
| img | *String* |Choose url or img.|Base64 encoded image data.|

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
|Faces    |*List*   |List of detected faces in the image.|
|landmark_106    |*List*   |106 contour key points.|
|x    |*Int*   |Number of pixels the key point from the left edge.|
|y    |*Int*   |Number of pixels the key point from the upper edge.|
|gender    |*String*   |Gender information.|
|age    |*String*   |Age information.|
|BoundingBox |*JSON*     |Coordinate values of the face in the image, including the percentage of top, left, width, height relative to the full screen.|
|Confidence    |*Float*   |Confidence score of the recognized face, which is a float type value between 0 and 1.|
|FaceModelVersion    |*String*   |Current model version.|

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
  include "include-deploy-cost-8GB.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}