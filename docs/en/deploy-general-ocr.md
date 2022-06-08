---
feature_id: GeneralOCR
feature_name: General OCR (Simplified Chinese)
feature_endpoint: general_ocr
deployment_time: 16 Minutes
destroy_time: 10 Minutes
sample_image: Image URL address
feature_description: Recognize and extract Simplified Chinese, numbers, alphabetical characters and symbols.
feature_scenario: Applicable to a variety of scenarios such as paper documents changed to electronic format, document identification, and content review to improve information processing efficiency.
---

{%
  include "include-deploy-description.md"
%}
## REST API Reference

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| url | *String* |Choose url or img. url has higher priority than img.| Image URL address, which supports HTTP/HTTPS and S3 protocols. Supported image formats are jpg/jpeg/png/bmp, with the longest side not exceeding 4096px.|
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
|words    |*String*   |Recognize text.|
|location |*JSON*     |Recognize the coordinates of the text in the image, including top, left, width, height as integer values.|
|score    |*Float*   |Confidence value of the recognized text, which is a float type value between 0 to 1.|

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

## Cost example 1 

以由西云数据运营的亚马逊云科技中国（宁夏）区域（cn-northwest-1）为例，处理1MB图像，处理时间1秒

使用本方案处理此图像所需的成本费用如下表所示：

| 服务                                  | 用量                  | 费用      |
|-------------------------------------|---------------------|---------|
| AWS Lambda                     | 调用百万次                 | ¥1.36   |
| AWS Lambda                     | 内存4096MB，每次运行1秒     | ¥453.9  |
| Amazon API Gateway                | 调用百万次                 | ¥28.94  |
| Amazon API Gateway             | 数据输出以每次10KB计算，¥0.933/GB | ¥9.33   |
| Amazon CloudWatch Logs              | 每次10KB，¥6.228/GB    | ¥62.28  |
| Amazon Elastic Container Registry | 0.5GB存储，每月每GB¥0.69    | ¥0.35   |
| 合计                                  |   | ¥556.16 |

## Cost example 2

以美国东部（俄亥俄州）区域（us-east-2）为例，处理1MB图像，处理时间1秒

使用本方案处理此图像所需的成本费用如下表所示：

| 服务                                  | 用量                 | 费用     |
|-------------------------------------|--------------------|--------|
| Amazon Lambda                     | 调用百万次                | $0.20  |
| Amazon Lambda                     | 内存4096MB，每次运行1秒    | $66.7  |
| Amazon API Gateway                | 调用百万次                | $3.5   |
| Amazon API Gateway             | 数据输出以每次10KB计算，$0.09/GB | $0.9   |
| Amazon CloudWatch Logs              | 每次10KB，$0.50/GB    | $5     |
| Amazon Elastic Container Registry | 0.5GB存储，每月每GB$0.1    | $0.05  |
| 合计                                  |   | $76.35 |


{%
  include-markdown "include-deploy-uninstall.md"
%}