---
feature_id: GeneralOCR
feature_name: 通用文字识别
feature_endpoint: general_ocr
deployment_time: 15 分钟
destroy_time: 15 分钟
sample_image: https://images-cn.ssl-images-amazon.cn/images/G/28/AGS/LIANG/Deals/2020/Dealpage_KV/1500300.jpg
feature_description: 通用文本识别解决方案基于人工智能文本识别技术，自动完成各类场景中文字的识别，并返回文字在图片中的坐标位置等信息以便于客户进行比对或结构化等操作，对客户的工作流程和业务流程进行了极大的改进，可满足医疗、金融、政务、法务、教育等行业文档快速录入的需求，有效降低企业人力成本，提高信息录入效率。目前支持识别简体/繁体中文，英文和数字。可将图片上的文字识别为文本，并返回对应文字的坐标与置信度，并且本解决方案还增强了对中文语言的处理与识别能力，结合精准的语言模型和大词库，如香港增补字符集（HKSCS）等大字符集识别，从而提高输入转化效率。
feature_scenario: 通用文本识别解决方案具有中文识别精度（准确率）高、价格低、处理速度快、可私有化部署等优势，能有效保护用户隐私数据。可应用于纸质文档电子化，证件识别，内容审核等多种场景，大幅提升信息处理效率。
---

{%
  include "include-deploy-description-zh.md"
%}

{%
  include "include-deploy-lambda-zh.md"
%}

{%
  include "include-deploy-cost-zh.md"
%}

{%
  include "include-deploy-zh.md"
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
|words    |*String*   |识别文本字符串内容|
|location |*JSON*     |识别文本在图像中的的坐标值，包含 top，left，width，height的整数值|
|score    |*Float*   |识别文本的置信度值，为0到1区间内 Float 型数值|

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
  include-markdown "include-deploy-code-zh.md"
%}

{%
  include-markdown "include-deploy-uninstall-zh.md"
%}