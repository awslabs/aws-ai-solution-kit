---
feature_id: TextSimilarity
feature_name: Text Similarity
feature_endpoint: text_similarity
deployment_time: 15 Minutes
destroy_time: 10 Minutes
sample_image: Image URL address
feature_description: Compare two Chinese words or sentences and return similarity score..
feature_scenario: Applicable to search engines, recommendation systems, machine translation, automatic response, named entity recognition, spelling error correction and other scenarios.
---

{%
  include "include-deploy-description.md"
%}
## API reference

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

## Cost Estimation

You are responsible for the cost of using each Amazon Web Services service when running the solution. As of June 2022, the main cost factors affecting the solution include.

- Amazon Lambda invocations
- Amazon Lambda running time
- Amazon API Gateway calls
- Amazon API Gateway data output
- Amazon CloudWatch Logs storage
- Amazon Elastic Container Registry storage

### Cost estimation example 1

In Amazon Web Services China (Ningxia) Region operated by NWCD (cn-northwest-1),  in 1 seconds

The cost of using this solution to process the text is shown below:

| Service | Dimensions                   | Cost       |
| ---- |----------------------|----------|
|Amazon Lambda | 1 million invocations                | ¥1.36    |
|Amazon Lambda | 8192MB memory, 1 seconds run each time      | ¥907.8  |
|Amazon API Gateway| 1 million invocations                  | ¥28.94   |
|Amazon API Gateway| 100KB data output each time, ¥0.933/GB | ¥93.3    |
|Amazon CloudWatch Logs| 10KB each time, ¥6.228/GB    | ¥62.28   |
|Amazon Elastic Container Registry| 0.5GB storage, ¥0.69/GB each month     | ¥0.35    |
| Total                                  |   | ¥1010.06 |

### Cost estimation example 2

In US East (Ohio) Region (us-east-2), in 1 seconds

The cost of using this solution to process this text is shown below:

| Service | Dimensions                   | Cost       |
|-------------------------------------|---------------------|---------|
| Amazon Lambda                     | 1 million invocations                 | $0.20   |
| Amazon Lambda                     | 8192MB memory, 1 seconds run each time     | $133.3  |
| Amazon API Gateway                | 1 million invocations                 | $3.5    |
| Amazon API Gateway              | 100KB data output each time, $0.09/GB | $9      |
| Amazon CloudWatch Logs              | 10KB each time, $0.50/GB     | $5      |
| Amazon Elastic Container Registry | 0.5GB存储，$0.1/GB each month      | $0.05   |
| Total                                 |   | $142.95 |

{%
  include-markdown "include-deploy-uninstall.md"
%}
