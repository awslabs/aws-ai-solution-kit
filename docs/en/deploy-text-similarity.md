---
feature_id: TextSimilarity
feature_name: Text Similarity
feature_endpoint: text_similarity
deployment_time: 15 Minutes
destroy_time: 10 Minutes
sample_image: Image URL address
feature_description: Compare two Chinese words or sentences and return similarity score.
feature_scenario: Applicable to search engines, recommendation systems, machine translation, automatic response, named entity recognition, spelling error correction and other scenarios.
---

{%
  include "include-deploy-description.md"
%}
## REST API Reference

The API supports two input modes: single text or text pair.

### Single text mode

With a single text as input, it returns the feature vectors of the text. You need to maintain a vector retrieval system. This is applicable to search or callback scenarios.

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| text | *String* |Yes|Text data|

- Example JSON request

``` json
{
  "text": "Test"
}
```

- Response parameters

| **Name** | **Type** | **Description**  |
|----------|-----------|------------|
|result    |*List*   |List with 768 parameters for a 768-dimensional text vector|

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
### Text pair mode

With text pair as input, it returns the cosine similarity of two texts. This is applicable to similarity comparison.

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| text_1 | *String* |Text data.|
| text_2 | *String* |Text data.|

- Example JSON request

``` json
{
  "text_1": "Test1",
  "text_2": "Test2"
}
```

- Response parameters

| **Name** | **Type** | **Description**  |
|----------|-----------|------------|
|similarity    |*Float*   |Cosine similarity of the text pair, which is a Float value between 0 and 1. The closer it is to 1, the more similar the text pair is.|

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
  include "include-deploy-cost.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}
