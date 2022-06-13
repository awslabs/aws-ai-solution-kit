---
feature_id: CarLicensePlate
feature_name: Car License Plate
feature_endpoint: car_license_plate
deployment_time: 9 Minutes
destroy_time: 6 Minutes
sample_image: Image URL address
feature_description: Recognize text on Chinese car license plate.
feature_scenario: Applicable to identifying car license plates in car parking lots and communities, or detecting vehicles for traffic violations.
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
|words    |*String*   | Recognized license plate number.|
|location |*JSON*     | Coordinates of the recognized car license plate, including top, left, width, height as integer values.|
|score    |*Float*   |Confidence score of the car license plate, which is a float type value between 0 and 1.|

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