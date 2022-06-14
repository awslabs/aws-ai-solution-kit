---
feature_id: FaceComparison
feature_name: Face Comparison
feature_endpoint: face_comparison
deployment_time: 10 Minutes
destroy_time: 6 Minutes
sample_image: Image URL address
feature_description: Compare two faces of the same person and return a confidence score of the similarity.
feature_scenario: Applicable to customer authentication, photo classification and other scenarios, such as self-service hotel check-in, personnel check-in, campus entrance passage, and photo album production.
---

{%
  include "include-deploy-description.md"
%}

## REST API Reference

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
|face_hash    |*List*   |List with 768 parameters for a 768-dimensional face vector.|
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