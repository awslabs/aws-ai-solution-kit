# AI Solution Kit

## Description
The AI and ML driven applications are maturing rapidly and creating new demands on enterprises, the AI Solution Kit provides diversified leading AI/ML solutions that are easy to use. Customers can easily work with the REST API or software development kit (SDK) provided by AI/ML solution.
 
The AI Kits solution creates RESTful API for the AI features, such as SageMaker well-trained models or Lambda functions, by this solution, customers can easily pick and test a specific AI feature they like and make deployment into their account.

## Architecture

Amazon API Gateway acts as a traffic router, it creates RESTful APIs for each AI feature. The API user can invoke the RESTful APIs through the HTTPS Invoking URL endpoint, the API Gateway maps the request to the required format by the Lambda function or Amazon SageMaker endpoint, and invokes the endpoint to obtain an inference from the model, finally, it sends the prediction response(JSON format) back to the API user(client).

1. Lambda Integration

![Architecture](docs/zh/images/arch-lambda.png)

Starting from the API User(s) side, the API user sends an HTTP request to Amazon API Gateway to pass payload parameters. The API Gateway is a layer that provides the RESTful API to the client for the AI applications, ML models are stored in Amazon EFS, the AI algorithm are implemented in the Lambda function, the Lambda function parses the values from API Gateway and performs model in EFS. After that, it returns a value (JSON format) and sends it back to the API Gateway.

2. SageMaker Integration

![Architecture](docs/zh/images/arch-sagemaker.png)

The Lambda function (invoke endpoint) parses the value and sends it to the Amazon SageMaker model endpoint, the SageMaker model performs the prediction and returns the predicted value to the Lambda. The same with the Lambda implementations, the Amazon API Gateway subsequently receives the response from the Lambda function and maps it to a response that is sent back to the client.

## APIs

### **Optical Character Recognition(OCR) APIs**
|    **API Name**   | **Description**    |  |
|--------------|------------|-------------|
|General OCR (Simplified Chinese)|Recognize and extract Simplified Chinese, numbers, alphabetical characters and symbols|[Get started](deploy-general-ocr.md)|
|General OCR (Traditional Chinese)|Recognize and extract Traditional Chinese, numbers, alphabetical characters and symbols|[Get started](deploy-general-ocr-traditional.md)|
|Custom OCR|Recognize and extract estructured text by predefined OCR templates|[Get started](deploy-custom-ocr.md)|
|Car License Plate|Recognize text on Chinese car license plate|[Get started](deploy-car-license-plate.md)|

### **Facial & Body APIs**
|    **API Name**   | **Description**    |  |
|--------------|------------|-------------|
|Face Comparison|Compare two faces of same person and return a confidence score of the similarity|[Get started](deploy-face-comparison.md)|
|Face Detection|Detect the face in a image and return coordinate information of the face|[Get started](deploy-face-detection.md)|
|Human Attribute Recognition |Recognize the attributes of the human body in the image|[Get started](deploy-human-attribute-recognition.md)|
|Human Image Segmentation|Segment human bodies from background and return the alpha channel|[Get started](deploy-human-image-segmentation.md)|

### **Image Understanding APIs**
|    **API Name**   | **Description**    |  |
|--------------|------------|-------------|
|Image Similarity|Compare two images and return similarity score|[Get started](deploy-text-similarity.md)|
|Object Recognition|Segment human bodies from background and return the alpha channel|[Get started](deploy-object-recognition.md)|
|Pornography Detection|Detect pornographic image in three dimensions (normal, sexy, porn) and return confidence scores|[Get started](deploy-nudity-detection.md)|

### **Computer Vision Production APIs**
|    **API Name**   | **Description**    |  |
|--------------|------------|-------------|
|Image Super Resolution|Upscale the resolution and enhance details in the images|[Get started](deploy-image-super-resolution.md)|

### **Natural Language Understanding(NLU) APIs**
|    **API Name**   | **Description**    |  |
|--------------|------------|-------------|
|Text Similarity|Compare two Chinese words or sentences and return similarity score|[Get started](deploy-text-similarity.md)|

## CloudFormation Deployment

[AI Solution Kit Deployment Guide](https://aws-samples.github.io/aws-ai-solution-kit/zh/)

## Authorization and Security

By default, the AI Gateway will enable the IAM authorization and Enable the CloudWatch Logs for accessing and debugging.

## License
This project is licensed under the Apache-2.0 License.
