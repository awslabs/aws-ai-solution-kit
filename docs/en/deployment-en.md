本部分介绍如何通过 **Amazon CloudFormation** 部署 **AI Solution Kit** 解决方案。对于解决方案中包含的 AI 应用的详细部署与使用说明，在对应的技术手册中有详细说明。在部署解决方案之前，建议您先查看本指南中有关架构图和区域支持等信息，然后按照下面的说明配置解决方案并将其部署到您的帐户中。

**部署时间**

- 部署基于 Amazon Lambda 架构的 AI 应用：约**10**分钟

- 部署基于 Amazon SageMaker 架构的 AI 应用：约**20**分钟

!!! 注意
    以上为部署 AI 应用的平均时间，具体信息请参考各个应用对应的技术手册

## 部署概述

**前提条件（中国区域）**

本解决方案使用 Amazon API Gateway来接收 API 调用请求，所以如果您希望在 北京区域 提供无需身份验证即可访问的 API 请求，则需要申请并确保您的Amazon Web Services账号已通过Internet Content Provider (ICP) 备案，80/443端口可以正常开启，具体流程参见[ICP备案说明](https://s3.cn-north-1.amazonaws.com.cn/sinnetcloud/ICP+recordal/ICP%E5%A4%87%E6%A1%88%E8%AF%B4%E6%98%8E.pdf)。

### 部署 Amazon CloudFormation 模板

1. 登录到Amazon Web Services管理控制台，选择链接启动 AWS CloudFormation 模板。

| 快速启动链接 | 描述 |
| ---------- | --- |
| [由光环新网运营的亚马逊云科技中国（北京）区域链接][template-china1] |  在**北京**区域部署 AI Solution Kit |
| [由西云数据运营的亚马逊云科技中国（宁夏）区域链接][template-china2] |  在**宁夏**区域部署 AI Solution Kit |
| [全球区域链接][template-global] |  在**全球**区域部署 AI Solution Kit  |

2. 默认情况下，该模板将在您登录控制台后默认的区域启动。若需在指定的Amazon Web Service区域中启动该解决方案，请在控制台导航栏中的区域下拉列表中选择。

3. 在**创建堆栈**页面上，确认Amazon S3 URL文本框中显示正确的模板URL，然后选择**下一步**。

4. 在**指定堆栈详细信息**页面，为您的解决方案堆栈分配一个账户内唯一且符合命名要求的名称。

5. 在**参数**部分，包含**通用配置**和 **AI 应用列表**两部分参数内容，您可以并根据需要进行修改通用配置并选择需要部署的 AI 应用，然后选择**下一步**。

    #### **通用配置参数**

    |  参数名称   |  默认值 |  描述 |
    |  ----------  | ---------| -----------  |
    | **APIGatewayAuthorization**  | AWS_IAM  | API网关的认证方式. 默认为 *AWS_IAM* ，将自动使用 [IAM](https://docs.aws.amazon.com/zh_cn/apigateway/latest/developerguide/permissions.html) 权限控制对 API 的访问。也可选择 *NONE* 即无权限认证方式（不安全的），在部署解决方案后用户需要手动在 API Gateway 控制台配置所需的[资源访问策略](https://docs.aws.amazon.com/zh_cn/apigateway/latest/developerguide/apigateway-control-access-to-api.html)。|
    | **APIGatewayStageName**    | prod    | API网关（URI）中的第一个路径字段。请参考：[阶段变量](https://docs.aws.amazon.com/zh_cn/apigateway/latest/developerguide/stage-variables.html) |
    | **APIExplorer**  | yes  | 部署基于 [Swagger UI](https://swagger.io/tools/swagger-ui/) 的**API 资源浏览器**，可视化 API 资源并与之交互。它是根据 OpenAPI（以前称为 Swagger）规范自动生成的，通过可视化文档使查看 API 定义与测试变得容易。详情请见：[API 资源浏览器](api-explorer-en.md) |

    #### **AI 应用列表参数**

    |  参数名称   |  默认值 |  描述 |
    |  ----------  | ---------| -----------  |
    | **GeneralOCR**  | no  | 部署**通用文字识别**，如需部署请选中'yes'，详情请见[通用文字识别技术手册](deploy-general-ocr-en.md) |
    | **ImageSuperResolution**  | no  | 部署**图像超分辨率**，如需部署请选中'yes'，详情请见[图像超分辨率技术手册](deploy-image-super-resolution-en.md) |
    | **HumanImageSegmentation**  | no  | 部署**智能人像分割**，如需部署请选中'yes'，详情请见[智能人像分割技术手册](deploy-human-image-segmentation-en.md) |
    | **NudityDetection**  | no  | 部署**色情内容审核**，如需部署请选中'yes'，详情请见[色情内容审核技术手册](deploy-nudity-detection-en.md) |
    | **GeneralOCRTraditional**  | no  | 部署**通用文字识别（繁体中文）**，如需部署请选中'yes'，详情请见[通用文字识别（繁体中文）技术手册](deploy-general-ocr-traditional-en.md) |
    | **CustomOCR**  | no  | 部署**自定义模板文字识别**，如需部署请选中'yes'，详情请见[自定义模板文字识别技术手册](deploy-custom-ocr-en.md) |
    | **ObjectRecognition**  | no  | 部署**通用物体识别**，如需部署请选中'yes'，详情请见[通用文字识别技术手册](deploy-object-recognition-en.md) |
    | **FaceDetection**  | no  | 部署**人脸识别**，如需部署请选中'yes'，详情请见[通用物体识别技术手册](deploy-face-detection-en.md) |
    | **FaceComparison**  | no  | 部署**人脸相似度比对**，如需部署请选中'yes'，详情请见[人脸识别技术手册](deploy-face-comparison-en.md) |
    | **HumanAttributeRecognition**  | no  | 部署**人体结构化属性**，如需部署请选中'yes'，详情请见[人体结构化属性技术手册](deploy-human-attribute-recognition-en.md) |
    | **CarLicensePlate**  | no  | 部署**车牌信息识别**，如需部署请选中'yes'，详情请见[车牌信息识别技术手册](deploy-car-license-plate-en.md) |
    | **TextSimilarity**  | no  | 部署**文本相似度**，如需部署请选中'yes'，详情请见[文本相似度技术手册](deploy-text_similarity-en.md) |

6. 在**配置堆栈选项**页面，选择**下一步**。

7. 在**审核**页面，查看并确认设置。确保选中确认模板将创建Amazon Identity and Access Management（IAM）资源的复选框。选择**下一步**。

8. 选择**创建堆栈**以部署堆栈。

您可以在AWS CloudFormation控制台的**状态**列中查看堆栈的状态。创建完成后即可看到状态为**CREATE_COMPLETE**。

### 更新 Amazon CloudFormation 堆栈

借助 Amazon CloudFormation，您可以更改堆栈中现有资源的属性，如果您需要添加或删除已经部署的 AI 功能，可以通过更新堆栈的方式完成。

1. 在 Amazon CloudFormation 控制台上，选择堆栈列表中创建完成的 AI Solution Kit 堆栈。

2. 在堆栈详细信息窗格中，选择 Update (更新)。

3. 在模板参数部分，指定需要添加或删除的 AI 功能或参数信息，然后选择 Next (下一步)。

4. 在**配置堆栈选项**页面，选择**下一步**。

5. 在**审核**页面，查看并确认设置。确保选中确认模板将创建Amazon Identity and Access Management（IAM）资源的复选框。选择**下一步**。

6. 如果您对所做更改表示满意，请选择 Updata stack (更新堆栈)。

[template-china1]:https://cn-north-1.console.amazonaws.cn/cloudformation/home?region=cn-north-1#/stacks/create/template?stackName=AIKitsInferOCRStack&templateURL=https://aws-gcr-solutions.s3.cn-north-1.amazonaws.com.cn/Aws-gcr-ai-solution-kit/v1.2.0/AI-Solution-Kit.template

[template-china2]:https://cn-northwest-1.console.amazonaws.cn/cloudformation/home?region=cn-northwest-1#/stacks/create/template?stackName=AIKitsInferOCRStack&templateURL=https://aws-gcr-solutions.s3.cn-north-1.amazonaws.com.cn/Aws-gcr-ai-solution-kit/v1.2.0/AI-Solution-Kit.template

[template-global]: https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/template?stackName=AIKitsInferOCRStack&templateURL=https://aws-gcr-solutions.s3.amazonaws.com/Aws-gcr-ai-solution-kit/v1.2.0/AI-Solution-Kit.template
