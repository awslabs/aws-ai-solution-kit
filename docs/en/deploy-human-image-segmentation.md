---
feature_id: HumanImageSegmentation
feature_name: Human Image Segmentation
feature_endpoint: human_image_segmentation
deployment_time: 15 Minutes
destroy_time: 9 Minutes
sample_image: Image URL address
feature_description: Segment human bodies from background and return the alpha channel which is a color component representing the degree of transparency of a color.
feature_scenario: Applicable to photo background replacement, post-processing, ID photo production, portrait cutout beautification, background blur and many other scenarios.
---

{%
  include "include-deploy-description.md"
%}

## REST API Reference

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| url | *String* |Choose url or img.|Image URL address, which supports HTTP/HTTPS and S3 protocols. Supported image formats are jpg/jpeg/png/bmp, with the longest side not exceeding 4096px.|
| img | *String* |Choose url or img.|Base64 encoded image data.|
| type | *String* |No|By default, type is empty, and it will return the Base64 encoding of the Alpha channel of the image after removing the background. When type is `foreground`, it will return the Base64 encoding of the transparent background image in PNG format. |

- Example JSON request

``` json
{
"url": "{{page.meta.sample_image}}",
"type": "foreground"
}
```

``` json
{
"img": "Base64-encoded image data",
"type": "foreground"
}
```

- Response parameters

| **Name** | **Type** | **Description**  |
|----------|-----------|------------|
|result    |*String*   |Base64 encoded image data|

- Example JSON response

``` json
{
  "result": "Base64 encoded image data"
}
```

{%
  include-markdown "include-deploy-code.md"
%}

{%
  include "include-deploy-cost.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}
