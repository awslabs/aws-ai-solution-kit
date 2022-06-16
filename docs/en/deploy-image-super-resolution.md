---
feature_id: ImageSuperResolution
feature_name: Image Super Resolution
feature_endpoint: image_super_resolution
deployment_time: 25 Minutes
destroy_time: 20 Minutes
sample_image: Image URL address
feature_description: Upscale the resolution and enhance details in the images..
feature_scenario: Applicable to converting original image assets into high resolution images.
---

{%
  include "include-deploy-description.md"
%}

## Requirements for AWS service quotas

- This API needs to create a GPU instance based on Amazon SageMaker. If the corresponding instance limit in your AWS account is insufficient, the API feature will be deployed abnormally. You can click **Support Center** on the toolbar at the top of the AWS Management Console to create a support ticket to request an increase in the instance limit of the Amazon SageMaker service. For more information, see [AWS service quotas](https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html).
- The default **AWS Lambda** memory is about 4GB (4096 MB). If the AWS Lambda function limit in your AWS account is lower than 4096 MB, the API feature will be deployed abnormally. You can click **Support Center** on the toolbar at the top of the AWS Management Console to create a support ticket and request to increase the memory limit of the AWS Lambda service. For more information, see [AWS service quotas](https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html).


## API reference

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| url | *String* |Choose url or img.|Image URL address, which supports HTTP/HTTPS and S3 protocols. Supported image formats are jpg/jpeg/png/bmp. Image size should not exceed 1920 * 1080. With portrait enhancement enabled, it is recommended that the image size should not exceed 1280 * 720. Due to performance limitations, the recommended image size does not exceed 400 * 400 for architecture based on AWS Lambda.|
| img | *String* |Choose url or img.|Base64-encoded image data|
|scale     |*Integer*    |no|Upscale size. 2 (default) or 4 is supported|
|face      |*Bool*       |no|By default, it is False. When set to True, face enhancement is enabled. Only GPU deployment is supported.|

- Example JSON request

``` json
{
"url": "Image URL address",
"scale" : 2
}
```

``` json
{
"img": "Base64-encoded image data",
"scale" : 4
}
```

- Response parameters

| **Name** | **Type** | **Description**  |
|----------|-----------|------------|
|result    |*String*   |Base64-encoded image data after scaling|

- Example JSON response

``` json
{
  "result": "Base64-encoded image data after scaling"
}
```

{%
  include-markdown "include-deploy-code.md"
%}

## Cost Estimation 

You are responsible for the cost of using each Amazon Web Services service when running the solution. As of June 2022, the main cost factors affecting the solution include.

- Amazon API Gateway calls
- Amazon API Gateway data output
- Amazon CloudWatch Logs storage
- Amazon Elastic Container Registry storage
- Amazon SageMaker endpoint instance type
- Amazon SageMaker endpoint data input
- Amazon SageMaker endpoint data output

### Example

In US East (Ohio) Region (us-east-2), process one million images, with an average processing time of 1 second for one image. Amazon SageMaker endpoint instance will be charged as long as it is started.

The cost of using this solution is shown below:

| Service                                 | Dimensions                                 | Cost      |
|-------------------------------------|------------------------------------|---------|
| Amazon API Gateway                | 1 million invocations                                | $3.5    |
| Amazon API Gateway              | 4MB data output each time, $0.09/GB                 | $360    |
| Amazon CloudWatch Logs              | 10KB each time, $0.50/GB                    | $0.05   |
| Amazon Elastic Container Registry | 0.5GB storage, $0.1/GB per month                    | $0.05   |
| Amazon SageMaker           | Endpoint instance runs for 278 hours, ml.g4dn.xlarge $0.736/hour | $204.61  |
| Amazon SageMaker          | Endpoint instance data input is 1MB each time, $0.016/GB                 | $16     |
| Amazon SageMaker         | Endpoint instance data output is 4MB each time, $0.016/GB                 | $64     |
| Total                                  |   | $648.21 |


{%
  include-markdown "include-deploy-uninstall.md"
%}
