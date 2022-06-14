---
feature_id: ImageSuperResolution
feature_name: 图像超分辨率
feature_endpoint: image_super_resolution
deployment_time: 25 分钟
destroy_time: 20 分钟
sample_image: 图像的URL地址
feature_description: 可将图片智能放大2或4倍，从而获取清晰度更高、细节丰富的图像。
feature_scenario: 可应用于等多种场景，解决原始图片分辨率不足的问题。
---

{%
  include "include-deploy-description.md"
%}

## 配额说明

- 图像超分辨率API需要创建一个基于**Amazon SageMaker**的GPU类型实例。如果您AWS账户中对应实例限制不足，则会导致该功能部署异常。您可以在AWS管理控制台上方工具栏点击**支持中心**，创建支持工单，要求提高**Amazon SageMaker**服务的实例限额。具体步骤请参阅[请求提高配额](https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html)。
- 方案中默认的**AWS Lambda**内存约为4GB（4096 MB），如果您AWS账户中AWS Lambda函数限制低于4096 MB，则会导致该部署异常。您可以在AWS管理控制台上方工具栏点击**支持中心**，创建支持工单，要求提高**AWS Lambda**服务的内存限额。具体步骤请参阅[请求提高配额](https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html)。

## API参数说明

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
|url&nbsp;&nbsp;&nbsp;&nbsp;       |*String*     |与 img 参数二选一|图像的 URL 地址。支持 HTTP/HTTPS 和 S3 协议。要求图像格式为 jpg/jpeg/png/bmp ，图像大小建议不超过1920 * 1080，在开启人像增强的情况下，图像大小建议不超过1280 * 720。AWS Lambda版本方案由于性能限制，图像大小建议不超过400 * 400|
|img       |*String*     |与 url 参数二选一|进行 Base64 编码的图像数据|
|scale     |*Integer*    |否|图像放大倍数，支持放大倍数为2或4，默认值为2|
|face      |*Bool*       |否|当设置为True时，额外开启人脸增强，默认值为False。（仅支持**GPU**版本部署方式）|

- 请求 Body 示例

``` json
{
"url": "图像的URL地址",
"scale" : 2
}
```

``` json
{
"img": "Base64编码的图像数据",
"scale" : 4
}
```

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|result    |*String*   |按比例放大后 Base64 编码的图像数据|

- 返回示例

``` json
{
  "result": "按比例放大后的Base64编码的图像数据"
}
```

{%
  include-markdown "include-deploy-code.md"
%}

## 成本预估 

您需要承担运行解决方案时使用亚马逊云科技各个服务的成本费用。截至2022年6月，影响解决方案的成本因素主要包括：

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
| Amazon API Gateway                | 调用百万次                                | $3.5    |
| Amazon API Gateway              | 数据输出以每次4MB计算，$0.09/GB                  | $360    |
| Amazon CloudWatch Logs              | 每次10KB，$0.50/GB                    | $0.05   |
| Amazon Elastic Container Registry | 0.5GB存储，每月每GB$0.1                    | $0.05   |
| Amazon SageMaker           | 终端节点实例需要运行278小时，ml.g4dn.xlarge $0.736/小时 | $204.61  |
| Amazon SageMaker          | 终端节点数据输入以每次1MB计算，$0.016/GB                 | $16     |
| Amazon SageMaker         | 终端节点数据输出以每次4MB计算，$0.016/GB                 | $64     |
| 合计                                  |   | $648.21 |


{%
  include-markdown "include-deploy-uninstall.md"
%}
