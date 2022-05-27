---
feature_id: PornographyDetection
feature_name: Pornography Detection
feature_endpoint: pornography-detection
deployment_time: 15 Minutes
destroy_time: 10 Minutes
sample_image: Image URL address
feature_description: Detect pornographic image in three dimensions (normal, sexy, porn) and return confidence scores.
feature_scenario: It can be applied to the scene of fast processing of pornographic content. Help customers reduce auditing manpower, effectively reduce the risk of pornography, and improve the efficiency of information processing.
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
|normal |*Float* |Recognize the normal dimension ratio of the image|
|sexy |*Float* |Identifies the proportion of sexy dimensions of an image|
|porn |*Float* |Identifies the proportion of pornographic dimensions of images|

- Example JSON response

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
  include "include-deploy-cost.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}

