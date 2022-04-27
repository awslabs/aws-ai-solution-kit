---
feature_id: HumanImageSegmentation
feature_name: 智能人像分割
feature_endpoint: human_image_segmentation
deployment_time: 10 分钟
destroy_time: 5 分钟
sample_image: https://demo.solutions.aws.a2z.org.cn/image/sample.png
feature_description: 智能人像分割方案基于 AI 深度学习框架可以识别图像中的人体轮廓，实现高精度分割，使之与背景进行分离。
feature_scenario: 传统人像抠图需要人工来完成，并且合成效果不稳定。本解决方案具有处理速度快、目标物体检测准确、价格低、可私有化部署等优势，能有效保护用户隐私数据。可应用于照片背景替换、后期处理、证件照制作，人像抠图美化、背景虚化等多种场景。
---

{%
  include "include-deploy-description.md"
%}

{%
  include "include-deploy-lambda.md"
%}

{%
  include "include-deploy-cost.md"
%}

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
