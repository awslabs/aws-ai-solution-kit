---
feature_id: HumanImageSegmentation
feature_name: 智能人像分割
feature_endpoint: human_image_segmentation
deployment_time: 10 分钟
destroy_time: 5 分钟
sample_image: https://aikits.demo.solutions.aws.a2z.org.cn/img/seg-2.jpg
feature_description: 基于 AI 深度学习框架可以识别图像中的人体轮廓，实现高精度分割，使之与背景进行分离。
feature_scenario: 可应用于照片背景替换、后期处理、证件照制作，人像抠图美化、背景虚化等多种场景。
---

{%
  include "include-deploy-description.md"
%}

{%
  include "include-deploy-lambda.md"
%}

## 成本预估 

您需要承担运行 AI Solution Kit 解决方案时使用亚马逊云科技各个服务的成本费用。截至2022年4月，影响解决方案的成本因素主要包括：

- Amazon Lambda调用
- Amazon Lambda运行
- Amazon API Gateway调用
- Amazon API Gateway数据输出
- Amazon CloudWatch Logs
- Amazon Elastic Container Registry存储

### 宁夏
| 服务 | 用量                   | 费用       |
| ---- |----------------------|----------|
|Amazon Lambda调用 | 百万次                  | ¥1.36    |
|Amazon Lambda运行| 内存4096MB，每次运行4秒      | ¥1815.6  |
|Amazon API Gateway调用| 百万次                  | ¥28.94   |
|Amazon API Gateway数据输出| 以每次100KB计算,¥0.933/GB | ¥93.3    |
|Amazon CloudWatch Logs| 每次10KB,¥6.228/GB     | ¥62.28   |
|Amazon Elastic Container Registry存储| 0.5GB,每月每GB¥0.69     | ¥0.35    |
| 合计                                  |   | ¥2001.83 |


### 美国东部(俄亥俄)

| 服务                                  | 用量                  | 费用      |
|-------------------------------------|---------------------|---------|
| Amazon Lambda调用                     | 百万次                 | $0.20   |
| Amazon Lambda运行                     | 内存4096MB，每次运行4秒     | $266.8  |
| Amazon API Gateway调用                | 百万次                 | $3.5    |
| Amazon API Gateway数据输出              | 以每次100KB计算,$0.09/GB | $9      |
| Amazon CloudWatch Logs              | 每次10KB,$0.50/GB     | $5      |
| Amazon Elastic Container Registry存储 | 待定GB,每月每GB$0.1      | $0.05   |
| 合计                                  |   | $284.55 |
​

{%
  include "include-deploy.md"
%}

## 开始使用

### 调用 URL

您可以在 Amazon CloudFormation 的 Outputs 标签页中看到以 **aikitsInvokeURL** 为前缀的记录的 URL 。

### REST API接口参考

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| url | *String* |与 img 参数二选一，优先级高于 img|图像的 URL 地址。支持 HTTP/HTTPS 和 S3 协议。要求图像格式为 jpg/jpeg/png/bmp ，最长边不超过 4096px。|
| img | *String* |与 url 参数二选一|进行 base64 编码的图像数据|

- 请求 Body 示例

``` json
{
  "url": "{{page.meta.sample_image}}"
}
```

``` json
{
  "img": "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/……"
}
```

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|result    |*String*   |去除背景后的 base64 编码的 Alpha 通道图像数据|

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
