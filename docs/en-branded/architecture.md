This solution architecture has two types of AI feature implementations: architecture based on Amazon Lambda and architecture based on Amazon SageMaker.

## Architecture based on Amazon Lambda

![](./images/arch-lambda-cn.png)

1. The user or application sends an API request to the Amazon API Gateway. The request payload needs to contain information about the image or text to be processed.

2. Amazon API Gateway sends the incoming user request directly to the Amazon Lambda function. 

3. The Amazon Lambda function returns the result to the invoker.

## Architecture based on Amazon SageMaker

![](./images/arch-sagemaker-cn.png)

1. The user or application sends an API request to the Amazon API Gateway. The request payload needs to contain the image or text information to be processed.

2. Amazon API Gateway sends the request to Amazon Lambda (invoke endpoint) function.

3. Amazon Lambda invokes Amazon SageMaker Endpoint, which performs the inference process in Amazon SageMaker and returns the inference result (usually in JSON format data).
