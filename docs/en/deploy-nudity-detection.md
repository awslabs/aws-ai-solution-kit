---
feature_id: NudityDetection
feature_name: 色情内容审核
feature_endpoint: nudity_detection
deployment_time: 5 分钟
destroy_time: 5 分钟
sample_image: https://aikits.demo.solutions.aws.a2z.org.cn/img/detect-1.jpg
feature_description: 内容审核-色情图片识别方案基于AI 技术，自动对图片进行审核，识别及获取多维度色情量化信息（normal，sexy，porn），实现精准快速的色情倾向判断。
feature_scenario: 本解决方案具有识别精度（准确率）高、价格低、处理速度快、可私有化部署等优势，能有效保护用户隐私数据。通过智能识别图片内容，并对色情程度进行多维度打分，方便客户对涉黄内容进行快速处理，帮助客户减少审核人力，有效降低涉黄风险，提升信息处理效率。
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
|normal    |*Float*   |识别图像的正常维度占比|
|sexy      |*Float*   |识别图像的性感维度占比|
|porn      |*Float*   |识别图像的色情维度占比|

- 返回示例
``` json
{ 
   “normal”  : 0.15993066132068634,
   “sexy”    : 0.5451669692993164, 
   “porn”    : 0.2949024438858032 
}
```

{%
  include-markdown "include-deploy-code.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}
