[English](README.md) | 简体中文

<p align="center">
    <h3 align="center">AI Solution Kit</h3>
  </a>
</p>

<p align="center">
  基于 Amazon Web Services (AWS) 的通用深度学习解决方案合集
</p>

<p align="center">
  <a href="https://awslabs.github.io/aws-ai-solution-kit/zh/"><strong>使用手册</strong></a> ·
  <a href="https://github.com/awslabs/aws-ai-solution-kit/releases"><strong>更新记录</strong></a> ·
  <a href="#feature-list"><strong>功能列表</strong></a>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg" alt="Apache 2.0 License"></a>
  <a href="https://github.com/awslabs/aws-ai-solution-kit/actions/workflows/build-template.yml"><img src="https://github.com/awslabs/aws-ai-solution-kit/actions/workflows/build-template.yml/badge.svg" alt="Build badge"></a>
  <a href="https://github.com/awslabs/aws-ai-solution-kit/actions/workflows/build-container.yml"><img src="https://github.com/awslabs/aws-ai-solution-kit/actions/workflows/build-container.yml/badge.svg" alt="Build badge"></a>
  <a href="https://github.com/awslabs/aws-ai-solution-kit/releases"><img src="https://img.shields.io/github/v/release/awslabs/aws-ai-solution-kit?include_prereleases"></a>
</p>

<br/>

## 简介

AI Solution Kit 提供一系列基于深度学习的云上机器学习功能，您可以通过调用API，轻松使用这些功能，同时这些功能可与 AWS 供的其它服务无缝集成。这个代码库包含了一系列基于 AWS Lambda 和 Amazon SageMaker 的预训练的深度学习模型，例如：通用OCR、文本相似度、人脸检测、人像分割、图像相似度、通用物体识别、图像超分辨率等（见下面的完整列表）。本工程可以帮助您可以从 Amazon Elastic Container Registry(ECR) 部署这些容器化的模型，并在 Amazon API Getaway 上创建 REST API。在工程部署完成后，您就可以调用 REST API 来轻松使用这些功能。

<div align="center">
    <img src="./docs/imgs/ocr_1.png" width="400">
    <img src="./docs/imgs/object_1.png" width="400">
    <img src="./docs/imgs/similarity_1.png" width="400">
    <img src="./docs/imgs/resolution_1.png" width="400">
    <img src="./docs/imgs/segmentation_1.png" width="400">
    <img src="./docs/imgs/face_1.png" width="400">
</div>

## 功能列表

本方案通过[Amazon API Gateway](https://aws.amazon.com/api-gateway/)自动创建REST API，您在部署解决方案后即可调用所需的AI功能。下表列出了支持的API，您可以点击详情链接查看API接口的测试方法和示例代码。更多信息可参见[API参考指南](https://awslabs.github.io/aws-ai-solution-kit/zh/api-explorer/)。

### 文字识别
|    **名称**   | **描述**    |
|--------------|------------|
|通用文字识别（简体中文）|通用场景文字提取，通过返回在图片中文字内容与坐标位置等信息，便于客户进行比对或结构化操作。支持识别简体中文、英文、数字和常用符号。|
|通用文字识别（繁体中文）|通用场景文字提取，通过返回图片中文字内容与坐标位置等信息，便于客户进行比对或结构化操作。支持识别繁体中文、英文、数字和常用符号。|
|自定义模板文字识别|客户可自定义OCR模板，提取卡证票据中结构化文字信息，并以键值对应关系的形式展现结果。|
|车牌信息识别|检测中华人民共和国境内常见机动车号牌，并识别其中的车牌号。|

### 人脸与人体
|    **名称**   | **描述**    |
|--------------|------------|
|人脸识别|检测和定位图片或视频流中的人脸，并返回高精度的人脸框坐标信息。|
|人脸相似度比对|通过两张人脸图片中的特征向量计算余弦相似度作为置信度，根据置信度比较，从而判断是否为同一个人。|
|人体结构化属性|识别输入图片中的人体区域，并返回每个区域人体位置坐标及属性分析，如性别、年龄、服饰等16种属性的语义信息。|
|智能人像分割|基于AI深度学习框架识别图像中的人体轮廓，实现高精度分割，使之与背景进行分离。|

### 图像理解
|    **名称**   | **描述**    |
|--------------|------------|
|图像相似度|比较两幅图片是否相似，通过图片特征向量计算余弦距离，并转化为置信度，根据置信度比较两张图片的相似性。|
|通用物体识别|检测图像中的通用对象主体，返回该对象主体的区域信息与置信度。支持识别300类物体，详情可参见本文中支持的目标识别实体列表。|
|色情内容审核|自动对图片进行审核，获取多维度色情量化信息，如：normal，sexy，porn，实现精准快速的色情倾向判断。|

### 视觉内容生产
|    **名称**   | **描述**    |
|--------------|------------|
|图像超分辨率|可将图片智能放大2或4倍，从而获取清晰度更高、细节丰富的图像。|

### 自然语言理解
|    **名称**   | **描述**    |
|--------------|------------|
|文本相似度|比较两段不同文本之间相似度，并输出一个介于0到1之间的置信度，根据置信度比较两段文字的相似性。|


## 快速部署

这个代码库包含了完整的用 Typescript 语言编写的 AWS CDK 工程，如果您想使用上述深度学习功能而不在本地重新编译整个工程源代码，您可以选择使用 AWS CloudFormation 模板来快速部署，编译好的 CloudFormation 模板可通过如下链接获取：https://aws-gcr-solutions.s3.amazonaws.com/Aws-gcr-ai-solution-kit/v1.3.0/AI-Solution-Kit.template

更多信息可参考[CloudFormation概念](https://docs.aws.amazon.com/zh_cn/zh_cn/AWSCloudFormation/latest/UserGuide/cfn-whatis-concepts.html)。

您可以通过如下链接启动AWS CloudFormation模板

- [中国区域链接][template-china1]
- [全球区域链接][template-global]

在堆栈创建成功后，您可以在AWS CloudFormation的**输出**标签页中通过对应**参数ID**查询基于Amazon API Gateway的调用URL。详细部署方式请参阅: https://awslabs.github.io/aws-ai-solution-kit/zh/deployment/


## 通过源代码构建

你也可以从源代码构建这个工程。

#### 前提条件

- 一个AWS账户
- 配置[aws cli的凭证](https://docs.aws.amazon.com/zh_cn/cli/latest/userguide/cli-chap-configure.html)
- 安装node.js LTS版本，如v14.x
- 安装Docker引擎
- 通过执行命令安装解决方案的依赖项 

```shell
yarn install && npx projen
```

- 将CDK工具包栈初始化到AWS环境中（仅适用于首次通过**AWS CDK**部署的情况）。

```shell
yarn cdk-init
```

#### 编译源代码
请将本代码库克隆到本地，并通过yarn在根目录下构建这个项目。

- [可选] 通过 yarn 构建docker镜像并推送到Amazon ECR仓库

```shell
yarn build-containers
```

您可以将docker镜像推送到Amazon ECR仓库，详细步骤请参与：https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html

在docker镜像推送成功后，请替换根目录下*.projenrc.js*文件中的*ecr registry*。

```
context: {
    ecrRegistry: 'your-ECR-registry',
}
```

- 构建 CDK 工程

```shell
yarn build
```

- 部署 CDK 工程

*说明* 如果不构建docker镜像，ECR registry将使用默认的'public.ecr.aws/gcr-solutions/aws-gcr-ai-solution-kit' 。

请通过如下命令部署您的工程

```shell
yarn deploy
```

部署结束后，请登录您的AWS控制台，通过更新Amazon CloudFormation栈选择激活您需要的功能。详细步骤请参与：https://awslabs.github.io/aws-ai-solution-kit/en/deploy-add-delete-api/

## 架构设计

解决方案在架构上包含两种类型的实现。分别是基于AWS Lambda构建和基于Amazon SageMaker构建。

*说明* Amazon SageMaker类型的实现只适用于图像超分辨率功能。

- 基于AWS Lambda构建

![Architecture](docs/zh/images/arch-lambda.png)

1. 向Amazon API Gateway发送API请求，请求内容需要图像或文本。

2. Amazon API Gateway 将收到的用户请求直接发送到AWS Lambda函数。

3. AWS Lambda函数将结果（JSON格式）返回给调用者。

- 基于Amazon SageMaker构建

![Architecture](docs/zh/images/arch-sagemaker.png)

1. 向Amazon API Gateway发送一个API请，请求内容需要图像或文本。

2. Amazon API Gateway将请求发送至AWS Lambda函数。

3. AWS Lambda调用Amazon SageMaker Endpoint，在Amazon SageMaker中执行推理并返回结果（JSON格式）。


## API 参考手册

请参考 [API 参考手册](https://awslabs.github.io/aws-ai-solution-kit/zh/api-explorer/)

## 安全与权限

当您在亚马逊云科技基础设施上构建解决方案时，安全责任由您和亚马逊云科技共同承担。此[责任共担模型](https://aws.amazon.com/compliance/shared-responsibility-model/)减少了您的操作负担，这是由于亚马逊云科技操作、管理和控制组件，包括主机操作系统、虚拟化层以及服务运行所在设施的物理安全性。有关亚马逊云科技安全的更多信息，请访问亚马逊云科技[云安全](http://aws.amazon.com/security/)。

## 许可证信息
本 AI Solution Kit 工程遵循Apache-2.0许可证发布。

[template-china1]:https://cn-north-1.console.amazonaws.cn/cloudformation/home?region=cn-north-1#/stacks/create/template?stackName=AI-Solution-Kit&templateURL=https://aws-gcr-solutions.s3.cn-north-1.amazonaws.com.cn/Aws-gcr-ai-solution-kit/v1.3.0/AI-Solution-Kit.template

[template-global]: https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/template?stackName=AI-Solution-Kit&templateURL=https://aws-gcr-solutions.s3.amazonaws.com/Aws-gcr-ai-solution-kit/v1.3.0/AI-Solution-Kit.template
