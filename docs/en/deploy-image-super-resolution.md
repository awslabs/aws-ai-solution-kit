---
feature_id: ImageSuperResolution
feature_name: Image Super Resolution
feature_endpoint: image_super_resolution
deployment_time: 25 Minutes
destroy_time: 20 Minutes
sample_image: Image URL address
feature_description: Upscale the resolution and enhance details in the images.
feature_scenario: It can be applied to many scenarios such as solving the problem of insufficient resolution of the original picture.
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
|scale     |*Integer*    |no|Image zoom, support zoom 2 or 4, the default value is 2|
|face      |*Bool*       |no|When set to True, face enhancement is additionally turned on, default value is False.|

- Example JSON request

``` json
{
"url": "Image URL address",
"scale" : 2
}
```

``` json
{
"img": "Base64-encoded image data",
"scale" : 4
}
```

- Response parameters

| **Name** | **Type** | **Description**  |
|----------|-----------|------------|
|result    |*String*   |Base64-encoded image data after scaling|

- Example JSON response

``` json
{
  "result": "Base64-encoded image data after scaling"
}
```

{%
  include-markdown "include-deploy-code.md"
%}

## Cost Estimation 

You are responsible for the cost of using each Amazon Web Services service when running the solution. As of May 2022, the main cost factors affecting the solution include.

- AWS Lambda调用次数
- AWS Lambda运行时间
- Amazon API Gateway调用次数
- Amazon API Gateway数据输出量
- Amazon CloudWatch Logs存储量
- Amazon Elastic Container Registry存储量
- Amazon SageMaker终端节点实例类型
- Amazon SageMaker终端节点数据输入量
- Amazon SageMaker终端节点数据输出量

### 示例

以美国东部（俄亥俄州）区域（us-east-2）为例，处理一张图按1秒计算，处理1百万图片。其中Amazon SageMaker终端节点实例开启时会一直计费。

使用本方案的成本费用如下表所示：

| 服务                                  | 用量                                 | 费用      |
|-------------------------------------|------------------------------------|---------|
| Amazon Lambda                     | 调用百万次                                | $0.20   |
| Amazon Lambda                     | 内存4096MB，每次运行1秒                    | $66.7   |
| Amazon API Gateway                | 调用百万次                                | $3.5    |
| Amazon API Gateway              | 数据输出以每次4MB计算，$0.09/GB                  | $360    |
| Amazon CloudWatch Logs              | 每次10KB，$0.50/GB                    | $0.05   |
| Amazon Elastic Container Registry | 0.5GB存储，每月每GB$0.1                    | $0.05   |
| Amazon SageMaker           | 终端节点实例需要运行278小时，ml.inf1.xlarge $0.297/小时 | $82.57  |
| Amazon SageMaker          | 终端节点数据输入以每次1MB计算，$0.016/GB                 | $16     |
| Amazon SageMaker         | 终端节点数据输出以每次4MB计算，$0.016/GB                 | $64     |
| 合计                                  |   | $593.07 |


{%
  include-markdown "include-deploy-uninstall.md"
%}
