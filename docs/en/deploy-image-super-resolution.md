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

{%
  include "include-deploy-cost.md"
%}

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
