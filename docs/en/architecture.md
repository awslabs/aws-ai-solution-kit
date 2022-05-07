# Architecture overview

A user or program sends an API request to Amazon API Gateway, and the request payload needs to contain the processed image or text information. After receiving the HTTP request, Amazon API Gateway sends the request data to the corresponding Amazon Lambda function or Amazon SageMaker Endpoint, thereby Implement the inference process and return the inference result (JSON format data).

This solution architecture includes two types of AI function implementations (the *Amazon SageMaker* architecture in version 1.2.0 is only applicable to **[Image Super Resolution](deploy-image-super-resolution.md)** API)

## Based on Amazon Lambda architecture
Amazon API Gateway directly sends the received user request to the Lambda function, and the Lambda function returns the result to the calling end.
![](./images/arch-lambda.png)

## Based on Amazon SageMaker architecture
First, API Gateway sends the user request to the Lambda (invoke endpoint) function, invokes the SageMaker Endpoint through Lambda, executes the inference process in SageMaker and returns the inference result.
![](./images/arch-sagemaker.png)