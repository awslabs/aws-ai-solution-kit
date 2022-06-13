---
feature_id: PornographyDetection
feature_name: Pornography Detection
feature_endpoint: pornography-detection
deployment_time: 15 Minutes
destroy_time: 10 Minutes
sample_image: Image URL address
feature_description: Detect pornographic image in three dimensions (normal, sexy, porn) and return confidence scores.
feature_scenario: Applicable to fast processing of pornographic content, thus helping to reduce auditing manpower, effectively reduce the risk of pornography, and improve the efficiency of information processing.
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
|normal |*Float* |Proportion of normal dimensions of the recognized image|
|sexy |*Float* |Proportion of sexy dimensions of the recognized image|
|porn |*Float* |Proportion of pornographic dimensions of the recognized image|

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

