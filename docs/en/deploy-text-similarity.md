---
feature_id: TextSimilarity
feature_name: Text Similarity
feature_endpoint: text_similarity
deployment_time: 15 Minutes
destroy_time: 10 Minutes
sample_image: Image URL address
feature_description: Compare two Chinese words or sentences and return similarity score.
feature_scenario: It can be used in search engines, recommendation systems, machine translation, automatic response, named entity recognition, spelling error correction and other scenarios.
---

{%
  include "include-deploy-description.md"
%}
## REST API Reference

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| text | *String* |Texts data|

- Example JSON request

``` json
{
  "text": "Testing of text"
}
```

- Response parameters

| **Name** | **Type** | **Description**  |
|----------|-----------|------------|
|result    |*List*   |A List with 768 elements, a 768-dimensional text vector|

- Example JSON response
``` json
{
    "result": [
        0.025645000860095024, 
        0.001914000022225082, 
        0.007929000072181225, 
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
