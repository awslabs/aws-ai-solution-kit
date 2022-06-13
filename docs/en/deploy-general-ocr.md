---
feature_id: GeneralOCR
feature_name: General OCR (Simplified Chinese)
feature_endpoint: general_ocr
deployment_time: 16 Minutes
destroy_time: 10 Minutes
sample_image: Image URL address
feature_description: Recognize and extract Simplified Chinese, numbers, alphabetical characters and symbols. Return the information such as text or coordinates.
feature_scenario: Applicable to a variety of scenarios such as paper documents changed to electronic format, document identification, and content review to improve information processing efficiency.
---

{%
  include "include-deploy-description.md"
%}
## API parameters

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| url | *String* |Choose url or img.| Image URL address, which supports HTTP/HTTPS and S3 protocols. Supported image formats are jpg/jpeg/png/bmp, with the longest side not exceeding 4096px.|
| img | *String* |Choose url or img.|Base64 encoded image data.|

- Example Request

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

## Cost estimation: example 1 

In AWS China (Ningxia) Region operated by NWCD (cn-northwest-1), process an image of 1MB in one second

The cost of using this solution to process the image is shown below:

| Service                                 | Dimensions                  | Cost      |
|-------------------------------------|---------------------|---------|
| AWS Lambda                     | 1 million invocations                 | ¥1.36   |
| AWS Lambda                     | 4096MB memory, 1 second run each time     | ¥453.9  |
| Amazon API Gateway                | 1 million invocations                  | ¥28.94  |
| Amazon API Gateway             | 10KB data output each time, ¥0.933/GB | ¥9.33   |
| Amazon CloudWatch Logs              | 10KB each time, ¥6.228/GB    | ¥62.28  |
| Amazon Elastic Container Registry | 0.5GB storage, ¥0.69/GB each month    | ¥0.35   |
| Total                                  |   | ¥556.16 |

## Cost estimation: example 2

In US East (Ohio) Region (us-east-2), process an image of 1MB in one second

The cost of using this solution to process this image is shown below:

| Service                                  | Dimensions                | Cost     |
|-------------------------------------|--------------------|--------|
| Amazon Lambda                     | 1 million invokes                | $0.20  |
| Amazon Lambda                     | 4096MB memory, 1 second run each time    | $66.7  |
| Amazon API Gateway                | 1 million invokes                | $3.5   |
| Amazon API Gateway             | 10KB data output each time, $0.09/GB | $0.9   |
| Amazon CloudWatch Logs              | 10KB data output each time, $0.50/GB    | $5     |
| Amazon Elastic Container Registry | 0.5GB storage, GB$0.1/GB each month    | $0.05  |
| Total                                 |   | $76.35 |


{%
  include-markdown "include-deploy-uninstall.md"
%}