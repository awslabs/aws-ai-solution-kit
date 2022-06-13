本方案架构中包含两类AI功能的实现方式：基于AWS Lambda的架构和基于Amazon SageMaker的架构。

!!! Note "说明"
    基于Amazon SageMaker的架构仅适用于**图像超分辨率方案**。

## 基于AWS Lambda的架构

![](./images/arch-lambda.png)

1. 用户或程序发送API请求至Amazon API Gateway。请求payload中需要包含被处理的图片或文字信息。

2. Amazon API Gateway将接收到的用户请求直接发送给AWS Lambda函数。

3. AWS Lambda函数将结果返回给调用端。

## 基于Amazon SageMaker的架构

![](./images/arch-sagemaker.png)

1. 用户或程序发送API请求至Amazon API Gateway。请求payload中需要包含被处理的图片或文字信息。

2. Amazon API Gateway将请求发送到AWS Lambda（invoke endpoint）函数。

3. AWS Lambda调用Amazon SageMaker Endpoint，在Amazon SageMaker中执行推理过程并返回推理结果（通常为JSON格式数据）。
