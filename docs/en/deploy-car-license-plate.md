---
feature_id: CarLicensePlate
feature_name: Car License Plate
feature_endpoint: car_license_plate
deployment_time: 9 Minutes
destroy_time: 6 Minutes
sample_image: Image URL address
feature_description: Recognize text on Chinese car license plate
feature_scenario: It could be used in car park, district automatic identification car license plate information, or vehicle violation information detection and other scenarios.
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
  | img | *String* |Choose one of two parameters with url|Base64 encoded image data|

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
|words    |*String*   |识别车牌内容|
|location |*JSON*     |识别车牌在图像中的的坐标值，包含top，left，width，height的整数值|
|score    |*Float*   |识别车牌的置信度值，为0到1区间内Float型数值|

- Example JSON response

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