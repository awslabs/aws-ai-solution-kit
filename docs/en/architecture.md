Two types of AI functionality implementations are included in this solution architecture: AWS Lambda-based architecture and Amazon SageMaker-based architecture.

!!! Note "Description"
    The Amazon SageMaker-based architecture is only available in version 1.2.0 for **Image Super Resolution Solution**.

## Architecture based on AWS Lambda

! [](./images/arch-lambda.png)

1. the user or application sends an API request to the Amazon API Gateway. the request payload needs to contain information about the image or text being processed.

2. Amazon API Gateway sends the incoming user request directly to the AWS Lambda function. 3.

3. the AWS Lambda function returns the result to the caller.

## Architecture based on Amazon SageMaker

! [](./images/arch-sagemaker.png)

1. the user or application sends an API request to the Amazon API Gateway. the request payload needs to contain the image or text information to be processed.

2. Amazon API Gateway sends the request to AWS Lambda (invoke endpoint) function. 3.

3. AWS Lambda calls Amazon SageMaker Endpoint, which performs the inference process in Amazon SageMaker and returns the inference result (usually JSON format data).
