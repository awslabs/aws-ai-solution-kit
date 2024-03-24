---
feature_id: DocumentLayoutAnalysis
feature_name: 文档版面分析
feature_endpoint: layout_analysis
deployment_time: 20 Minutes
destroy_time: 15 Minutes
sample_image: 图像的URL地址
feature_description: 将文档图像转换为 Markdown/JSON 格式输出，并以 Markdown/HTML 格式生成表格。
feature_scenario: 适用于将纸质文件更改为电子格式、文件识别和内容审查，以提高信息处理效率。
---

{%
include "include-deploy-description.md"
%}

## API 参数说明

- HTTP 方法: `POST`

- Body 请求参数

| **名称**                    | **类型** | **是否必选**      | **说明**                                                                                                                                                                                                                             |
| --------------------------- | -------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| url&nbsp;&nbsp;&nbsp;&nbsp; | _String_ | 与 img 参数二选一 | 图像的 URL 地址。支持 HTTP/HTTPS 和 S3 协议。要求图像格式为 jpg/jpeg/png/bmp ，图像大小建议不超过 1920 _ 1080，在开启人像增强的情况下，图像大小建议不超过 1280 _ 720。AWS Lambda 版本方案由于性能限制，图像大小建议不超过 400 \* 400 |
| img                         | _String_ | 与 url 参数二选一 | 进行 Base64 编码的图像数据                                                                                                                                                                                                           |
| output_type                 | _String_ |                   | json`或`markdown`，返回结果是 json 格式还是转换为 markdown 格式。                                                                                                                                                                    |
| table_type                  | _String_ |                   | html "或 "markdown"，结果中的表格是以 html 格式返回还是转换为 markdown 格式。                                                                                                                                                        |

- 请求 Body 示例

**示例 1**

```json
{
  "url": "{{page.meta.sample_image}}",
  "output_type": "json"
}
```

```json
{
  "img": "Base64-encoded image data",
  "output_type": "json"
}
```

**示例 2**

```json
{
  "url": "{{page.meta.sample_image}}",
  "output_type": "markdown"
}
```

```json
{
  "img": "Base64-encoded image data",
  "output_type": "markdown"
}
```

- 返回参数

- 返回参数

| **名称**  | **类型** | **说明**                                                   |
| --------- | -------- | ---------------------------------------------------------- |
| BlockType | _String_ | 这些元素与版面的不同部分相对应，它们是：文本、标题、图或表 |
| Geometry  | _Dict_   | 文档页面上检测到的项目的位置信息                           |
| Text      | _String_ | 当前块的文本内容。当 BlockType 为 "table "时，将根据 "table_type "返回表格的 html 或 markdown。 |

当 `output_type` 为 `markdown` 时，将返回一个 dict。

| **名称**  | **类型** | **说明**                                                   |
| -------- | -------- | ------------------------------------ |
| markdown | _String_ | 将图像转换为 markdown 结果 |

- 返回示例

** 示例 1 `output_type` 是 `json` 格式**

```json
[
  {
    "BlockType": "text",
    "Geometry": {
      "BoundingBox": {
        "Width": 972,
        "Height": 79,
        "Left": 561,
        "Top": 564
      }
    },
    "Text": "核准日期：xxx年xx月xx日"
  },
  {
    "BlockType": "text",
    "Geometry": {
      "BoundingBox": {
        "Width": 1543,
        "Height": 80,
        "Left": 569,
        "Top": 678
      }
    },
    "Text": "修改日期：xxx年xx月xx日"
  }
    ...
]
```

**示例 2 `output_type` 是 `markdown` 格式**

```json
{
  "Markdown": "核准日期：xxx年xx月xx日 \n\n修改日期：xxx年xx月xx日...."
}
```

{%
include-markdown "include-deploy-code.md"
%}

{%
include "include-deploy-cost-8GB.md"
%}

{%
include-markdown "include-deploy-uninstall.md"
%}
