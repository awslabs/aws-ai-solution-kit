---
feature_id: Image Similarity
feature_name: Image Similarity
feature_endpoint: text_similarity
deployment_time: 15 Minutes
destroy_time: 10 Minutes
sample_image: Image URL address
feature_description: Compare two images by calculating the cosine distance from the image feature vector and converting it into confidence, and return similarity score. 
feature_scenario: Applicable to scenarios such as commodity recognition, remake recognition, and intelligent photo albums.
---

{%
  include "include-deploy-description.md"
%}

## API reference

The API supports two input modes: single image and image pair.

### Single image mode

With a single image as input, it returns the feature vectors of the image. You need to maintain a vector retrieval system. This is applicable to search or callback scenarios.

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| url | *String* |Choose url or img.|Image URL address, which supports HTTP/HTTPS and S3 protocols. Supported image formats are jpg/jpeg/png/bmp, with the longest side not exceeding 4096px.|
| img | *String* |CChoose url or img.|Base64 encoded image data.|

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
|result    |*List*   |List with 512 parameters for a 512-dimensional image vector.|

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
### Image pair mode

With two images as input, it returns the cosine similarity of two images. This is applicable to similarity comparison.

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| url_1 | *String* |Choose url_1 or img_1.|Image URL address, which supports HTTP/HTTPS and S3 protocols. Supported image formats are jpg/jpeg/png/bmp, with the longest side not exceeding 4096px.|
| img_1 | *String* |Choose img_1 or url_1.|Base64 encoded image data.|
| url_2 | *String* |Choose url_2 or img_2.|Image URL address, which supports HTTP/HTTPS and S3 protocols. Supported image formats are jpg/jpeg/png/bmp, with the longest side not exceeding 4096px.|
| img_2 | *String* |Choose img_2 or url_2.|Base64 encoded image data.|

- Example JSON request

``` json
{
"url_1": "{{page.meta.sample_image}}",
"url_2": "{{page.meta.sample_image}}"
}
```

``` json
{
"img_1": "Base64编码的图像数据",
"img_2": "Base64编码的图像数据"
}
```

- Response parameters

| **Name** | **Type** | **Description**  |
|----------|-----------|------------|
|similarity    |*Float*   |Cosine similarity of the two images, which is a Float value between 0 and 1. The closer it is to 1, the more similar the two images are.|

- Example JSON response

``` json
{
    "similarity": 0.95421
}
```

{%
  include-markdown "include-deploy-code.md"
%}

{%
  include "include-deploy-cost-10GB.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}