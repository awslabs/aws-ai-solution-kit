---
feature_id: ImageSuperResolution
feature_name: 图像超分辨率
feature_endpoint: image_super_resolution
deployment_time: 20 分钟
destroy_time: 15 分钟
sample_image: https://aikits.demo.solutions.aws.a2z.org.cn/img/sr-5.jpg
feature_description: 图像超分辨率方案基于 AI 推理，可将图片进行智能放大2到4倍，并保持结果图像的清晰度，从而获取清晰度更高、细节丰富的图像，解决原始图片分辨率不足的问题。
feature_scenario: 本解决方案具有处理速度快、价格低、可私有化部署等优势，能有效保护用户隐私数据。可以解决图像放大之后模糊失真的问题，提升细节保持结果图像的清晰度。应用于等多种场景，解决原始图片分辨率不足的问题，大幅提升信息处理效率。
---

{%
  include "include-deploy-description.md"
%}

{%
  include "include-deploy-lambda.md"
%}

## 成本预估 

处理一张图按1秒计算，Amazon SageMaker 终端节点实例开启时会一直计费，这里仅计算处理完1百万图片需要消耗时长对应的实例费用

### 美国东部(俄亥俄)

| 服务                                  | 用量                                 | 费用      |
|-------------------------------------|------------------------------------|---------|
| Amazon Lambda调用                     | 百万次                                | $0.20   |
| Amazon Lambda运行                     | 内存4096MB，每次运行1秒                    | $66.7   |
| Amazon API Gateway调用                | 百万次                                | $3.5    |
| Amazon API Gateway数据输出              | 以每次4MB计算,$0.09/GB                  | $360    |
| Amazon CloudWatch Logs              | 每次10KB,$0.50/GB                    | $0.05   |
| Amazon Elastic Container Registry存储 | 0.5GB,每月每GB$0.1                    | $0.05   |
| Amazon SageMaker 终端节点实例           | 需要运行278小时，ml.inf1.xlarge $0.297/小时 | $82.57  |
| Amazon SageMaker 终端节点数据输入         | 以每次1MB计算，$0.016/GB                 | $16     |
| Amazon SageMaker 终端节点数据输出         | 以每次4MB计算，$0.016/GB                 | $64     |
| 合计                                  |   | $593.07 |


{%
  include "include-deploy.md"
%}
## 开始使用

### 调用 URL

您可以在 Amazon CloudFormation 的 Outputs 标签页中看到以 **{{ page.meta.feature_id }}** 为前缀的记录的 URL。

### REST API接口参考

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
|url&nbsp;&nbsp;&nbsp;&nbsp;       |*String*     |与 img 参数二选一，优先级高于 img|图像的 URL 地址。支持 HTTP/HTTPS 和 S3 协议。要求图像格式为 jpg/jpeg/png/bmp ，图像大小建议不超过1920 * 1080，在开启人像增强的情况下，图像大小建议不超过1280 * 720。Lambda 版本方案由于性能限制，图像大小建议不超过400 * 400|
|img       |*String*     |与 url 参数二选一|进行 base64 编码的图像数据|
|scale     |*Integer*    |否|图像放大倍数，支持放大倍数为2或4，默认值为2|
|face      |*Bool*       |否|当True时，额外开启人脸增强，默认值为False。（仅支持 **GPU** 版本部署方式）|

- 请求 Body 示例

``` json
{
  "url": "https://aikits.demo.solutions.aws.a2z.org.cn/img/sr-5.jpg",
  "scale" : 2
}
```

``` json
{
  "img": "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/……",
  "scale" : 4
}
```

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|result    |*String*   |按比例放大后 base64 编码的图像数据|

- 返回示例
``` json
{
    "result": "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/……"
}
```

{%
  include-markdown "include-deploy-code.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}
