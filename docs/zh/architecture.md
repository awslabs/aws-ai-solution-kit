# 架构概览

用户或程序发送 API 请求至 Amazon API Gateway，请求 payload 中需要包含被处理的图片或文字信息，Amazon API Gateway 接收到 HTTP 到请求后，将请求数据发送给对应的 Amazon Lambda 函数或 Amazon SageMaker Endpoint，从而实现推理过程，并将推理结果（通常为JSON格式数据）返回。

本解决方案架构中包含两类 AI 功能的实现方式（版本1.2.0中 *Amazon SageMaker* 架构只适用于**图像超分辨率方案**）

## 基于 Amazon Lambda 架构
Amazon API Gateway 将接收到的用户请求直接发送给 Lambda 函数，由 Lambda 函数将结果返回给调用端。
![](./images/arch-lambda.png)

## 基于 Amazon SageMaker 架构
首先 API Gateway 将用户请求发送到 Lambda（invoke endpoint）函数，通过 Lambda 调用 SageMaker Endpoint，在 SageMaker 中执行推理过程并返回推理结果。
![](./images/arch-sagemaker.png)
