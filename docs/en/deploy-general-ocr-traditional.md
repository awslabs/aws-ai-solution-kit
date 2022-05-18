---
feature_id: GeneralOCRTraditional
feature_name: General OCR (Traditional Chinese)
feature_endpoint: general_ocr_traditional
deployment_time: 10 Minutes
destroy_time: 10 Minutes
sample_image: Image URL address
feature_description: Recognize and extract Traditional Chinese, numbers, alphabetical characters and symbols.
feature_scenario: It can be applied to a variety of scenarios such as paper documents electronically, document identification, content review, etc. to improve information processing efficiency.
---

{%
  include "include-deploy-description.md"
%}
### REST API Reference

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
|words    |*String*   |Recognize text content|
|location |*JSON*     |Recognize the coordinates of the text in the image, including top, left, width, height as integer values|
|score    |*Float*   |Confidence value of the recognized text, Float type value in the interval 0 to 1|

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
  include "include-deploy-cost.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}