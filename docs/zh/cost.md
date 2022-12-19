## 成本预估

您需要承担运行解决方案时使用亚马逊云科技各个服务的成本费用。截至2022年12月，影响解决方案的成本因素主要包括：

- Amazon API Gateway调用次数
- Amazon API Gateway数据输出量
- Amazon CloudWatch Logs存储量
- Amazon Elastic Container Registry存储量

如果您选择基于AWS Lambda架构部署，影响成本的因素还包括：

- AWS Lambda调用次数
- AWS Lambda运行时间

与之对应的Amazon SageMaker架构部署，影响成本的因素还包括：

- Amazon SageMaker终端节点实例类型
- Amazon SageMaker终端节点数据输入量
- Amazon SageMaker终端节点数据输出量

您可以查看每个API对应的成本预估章节，了解每个API应用的部署与实际使用成本。


|    **名称**   |    **成本预估**   |
|--------------|--------------|
|通用文字识别（简体中文）|[查看](deploy-general-ocr.md#_3)|
|通用文字识别（繁体中文）|[查看](deploy-general-ocr-traditional.md#_3)|
|自定义模板文字识别|[查看](deploy-custom-ocr.md#_3)|
|车牌信息识别|[查看](deploy-car-license-plate.md#_3)|
|人脸识别|[查看](deploy-face-detection.md#_3)|
|人脸相似度比对|[查看](deploy-face-comparison.md#_3)|
|人体结构化属性|[查看](deploy-human-attribute-recognition.md#_3)|
|智能人像分割|[查看](deploy-human-image-segmentation.md#_3)|
|图像相似度|[查看](deploy-image-similarity.md#_3)|
|通用物体识别|[查看](deploy-object-recognition.md#_3)|
|色情内容检测|[查看](deploy-pornography-detection.md#_3)|
|图像超分辨率|[查看](deploy-image-super-resolution.md#_3)|
|文本相似度|[查看](deploy-text-similarity.md#_3)|
