---
feature_id: GeneralOCRTraditional
feature_name: General OCR (Traditional Chinese)
feature_endpoint: general_ocr_traditional
deployment_time: 10 Minutes
destroy_time: 10 Minutes
sample_image: Image URL address
feature_description: Recognize and extract Traditional Chinese, numbers, alphabetical characters and symbols from images. Return the information such as text or coordinates.
feature_scenario: Applicable to a variety of scenarios such as paper documents changed to electronic format, document identification, and content review to improve information processing efficiency.
---

{%
  include "include-deploy-description.md"
%}
### REST API Reference

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
|words    |*String*   |Recognized text.|
|location |*JSON*     |Coordinates of the recognized text, including top, left, width, height as integer values.|
|score    |*Float*   |Confidence score of the recognized text, which is a float type value between 0 and 1.|

- Example JSON response

``` json
[
  {
      "words": "香港永久性居民身份證",
      "location": {
          "top": 18,
          "left": 148,
          "width": 169,
          "height": 17
      },
      "score": 0.9923796653747559
  },
  {
      "words": "HONG KONG PERMANENTIDENTITYCARD",
      "location": {
          "top": 36,
          "left": 71,
          "width": 321,
          "height": 17
      },
      "score": 0.9825196266174316
  }

]
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