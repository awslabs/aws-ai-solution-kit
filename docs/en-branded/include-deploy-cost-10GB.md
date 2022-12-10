## Cost estimation

You are responsible for the cost of using each Amazon Web Services service when running the solution. As of June 2022, the main cost factors affecting the solution include.

- Amazon API Gateway calls
- Amazon API Gateway data output
- Amazon CloudWatch Logs storage
- Amazon Elastic Container Registry storage

If you choose an Amazon Lambda based deployment, the costs will include:

- Amazon Lambda invocations
- Amazon Lambda running time

If you choose an Amazon SageMaker based deployment, the costs will include:

- Amazon SageMaker endpoint node instance type
- Amazon SageMaker endpoint node data input
- Amazon SageMaker endpoint node data output

### Cost estimation example 1

In Amazon Web Services China (Ningxia) Region operated by NWCD (cn-northwest-1), process an image of 1MB in 1 seconds

The cost of using this solution to process the image is shown below:

| Service | Dimensions                   | Cost       |
| ---- |----------------------|----------|
|Amazon Lambda | 1 million invocations                | ¥1.36    |
|Amazon Lambda | 10240MB memory, 1 seconds run each time      | ¥1134.8  |
|Amazon API Gateway| 1 million invocations                  | ¥28.94   |
|Amazon API Gateway| 100KB data output each time, ¥0.933/GB | ¥93.3    |
|Amazon CloudWatch Logs| 10KB each time, ¥6.228/GB    | ¥62.28   |
|Amazon Elastic Container Registry| 0.5GB storage, ¥0.69/GB each month     | ¥0.35    |
| Total                                  |   | ¥1237.06 |

### Cost estimation example 2

In US East (Ohio) Region (us-east-2), process an image of 1MB in 4 seconds

The cost of using this solution to process this image is shown below:

| Service | Dimensions                   | Cost       |
|-------------------------------------|---------------------|---------|
| Amazon Lambda                     | 1 million invocations                 | $0.20   |
| Amazon Lambda                     | 10240MB memory, 1 seconds run each time     | $166.7  |
| Amazon API Gateway                | 1 million invocations                 | $3.5    |
| Amazon API Gateway              | 100KB data output each time, $0.09/GB | $9      |
| Amazon CloudWatch Logs              | 10KB each time, $0.50/GB     | $5      |
| Amazon Elastic Container Registry | 0.5GB存储，$0.1/GB each month      | $0.05   |
| Total                                 |   | $176.35 |