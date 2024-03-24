---
feature_id: DocumentLayoutAnalysis
feature_name: Document Layout Analysis
feature_endpoint: layout_analysis
deployment_time: 20 Minutes
destroy_time: 15 Minutes
sample_image: Image URL address
feature_description: Convert document images to a Markdown/JSON format output, with table format in Markdown/HTML.
feature_scenario: Applicable to a variety of scenarios such as paper documents changed to electronic format, document identification, and content review to improve information processing efficiency.
---

{%
include "include-deploy-description.md"
%}

## API reference

- HTTP request method: `POST`

- Request body parameters

| **Name**    | **Type** | **Required**       | **Description**                                                                                                                                          |
| ----------- | -------- | ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| url         | _String_ | Choose url or img. | Image URL address, which supports HTTP/HTTPS and S3 protocols. Supported image formats are jpg/jpeg/png/bmp, with the longest side not exceeding 4096px. |
| img         | _String_ | Choose url or img. | Base64 encoded image data.                                                                                                                               |
| output_type | _String_ |                    | `json` or `markdown`, Whether the result is returned in json or converted to markdown.                                                                   |
| table_type  | _String_ |                    | `html` or `markdown`, Whether the table in the result is returned in html or converted to markdown.                                                      |

- Example Request

**Example 1**

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

**Example 2**

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

- Response parameters

When `output_type` is `json`, a list is returned, and an item in the list is a block in a document.

| **Name**  | **Type** | **Description**                                                                                                                                     |
| --------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| BlockType | _String_ | These elements correspond to the different portions of the layout, and are: text, title, figure or table                                            |
| Geometry  | _Dict_   | location information about the location of detected items on a document page.                                                                       |
| Text      | _String_ | The text content of the current block. When BlockType is `table`, the html or markdown of the table will be returned depending on the `table_type`. |

When `output_type` is `markdown`, a dict is returned.

| **Name** | **Type** | **Description**                      |
| -------- | -------- | ------------------------------------ |
| markdown | _String_ | Converted images to markdown result. |

- Example JSON response

**Example 1 `output_type` is `json` response**

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

**Example 2 `output_type` is `markdown` response**

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
