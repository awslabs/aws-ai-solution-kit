---
feature_id: GeneralOCR
feature_name: 通用文字识别
feature_endpoint: general_ocr
deployment_time: 16 分钟
destroy_time: 10 分钟
sample_image: 图像的URL地址
feature_description: 通用场景文字提取，通过返回在图片中文字内容与坐标位置等信息，便于客户进行比对或结构化操作。支持识别**简体中文**、英文、数字和常用符号。
feature_scenario: 可应用于纸质文档电子化，证件识别，内容审核等多种场景，大幅提高信息处理效率。
---

{%
  include "include-deploy-description.md"
%}
## API参数说明

- HTTP 方法: `POST`

- 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| url | *String* |与`img`参数二选一。|图像URL地址。支持HTTP/HTTPS和S3协议。要求图像格式为 jpg/jpeg/png/bmp，最长边不超过 4096px。|
| img | *String* |与`url`参数二选一。|进行Base64编码的图像数据。|

- 请求示例

``` json
{
  "url": "{{page.meta.sample_image}}"
}
```

``` json
{
  "img": "Base64编码的图像数据"
}
```

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|words    |*String*   |识别文本字符串内容。|
|location |*JSON*     |识别文本在图像中的的坐标值，包含 top，left，width，height的整数值。|
|score    |*Float*   |识别文本的置信度值，为0到1区间内Float型数值。|

- 返回示例

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

## 成本预估示例1 

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

## 成本预估示例2

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