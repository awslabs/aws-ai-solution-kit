---
feature_id: Image Similarity
feature_name: Image Similarity
feature_endpoint: text_similarity
deployment_time: 15 Minutes
destroy_time: 10 Minutes
sample_image: Image URL address
feature_description: Compare two images and return similarity score.
feature_scenario: It can be applied to scenarios such as product recognition, flip recognition, and intelligent photo albums.
---

{%
  include "include-deploy-description.md"
%}

## REST API Reference

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| url | *String* |Choose one of the two parameters with img, the priority is higher than the URL|Supports HTTP/HTTPS and S3 protocols. Requires the image format to be jpg/jpeg/png/bmp with the longest side not exceeding 4096px.|
| img | *String* |Choose one of two parameters with url|Base64 encoded image data|

- Example JSON request

``` json
{
"url": "{{page.meta.sample_image}}"
}
```

``` json
{
"img": "Base64-encoded image data"
}
```

- Response parameters

| **Name** | **Type** | **Description**  |
|----------|-----------|------------|
|result    |*List*   |A List with 512 parameters for a 512-dimensional image vector|

- Example JSON response

``` json
{
    "result": [
        -0.02555299922823906, 
        0.012955999933183193, 
        -0.10079500079154968, 
        ...
    ]
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