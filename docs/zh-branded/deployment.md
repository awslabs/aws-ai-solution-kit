在部署解决方案之前，建议您先查看本指南中有关架构图和区域支持等信息，然后按照下面的说明配置解决方案并将其部署到您的帐户中。

**部署时间**

- 部署基于Amazon Lambda架构的功能：约**10**分钟

- 部署基于Amazon SageMaker架构的功能：约**20**分钟

## 前提条件

如果您选择从中国区域启动堆栈，请确认已有ICP备案的域名。详情可参考[ICP备案指南](https://www.amazonaws.cn/support/icp/)。

## 启动堆栈

1. 登录到亚马逊云科技管理控制台，选择链接创建Amazon CloudFormation模板。

    - [从中国区域启动堆栈][template-china1]
    - [从全球区域启动堆栈][template-global]

2. 默认情况下，该模板将在您登录控制台后默认的区域启动。若需在指定的Amazon Web Service区域中启动该解决方案，请在控制台导航栏中的区域下拉列表中选择。

3. 在**创建堆栈**页面上，确认Amazon S3 URL文本框中显示正确的模板URL，然后选择**下一步**。

4. 在**指定堆栈详细信息**页面，为您的解决方案堆栈分配一个账户内唯一且符合命名要求的名称。

5. 在**参数**部分，根据需要修改通用配置并选择需要部署的AI功能，然后选择**下一步**。
    
    - 您可以选择是否部署API资源浏览器，并选择API网关的认证方式。

        |  参数名称   |  默认值 |  描述 |
        |  ----------  | ---------| -----------  |
        | **APIExplorer**  | yes  | 默认值为yes，部署**API资源浏览器**，通过可视化文档便于查看API定义与测试。详情可参见[API参考指南](api-explorer.md)。如果选择no，则API资源浏览器中只能看到API的参考定义，而不能进行在线测试等操作。 |
        | **APIGatewayAuthorization**  | NONE  | API网关的认证方式。默认为*NONE*，即无权限认证方式。您还可以选择使用[IAM](https://docs.aws.amazon.com/zh_cn/apigateway/latest/developerguide/permissions.html)权限控制对API的访问。|
        | **APIGatewayStageName**    | prod    | API网关（URI）中的第一个路径字段。详情可参见[阶段变量](https://docs.aws.amazon.com/zh_cn/apigateway/latest/developerguide/stage-variables.html)。 |

    - 请您在需要使用的功能的下拉列表中选择所需实例类型进行部署，您可以通过选择 **yes-lambda** 或者 **yes-sagemaker** 来部署所需要的功能。所有功能的参数默认值均为 **no**。

        |  参数名称   |  默认值 |  描述 |
        |  ----------  | ---------| -----------  |
        | **General OCR - Simplified Chinese**  | no  | 部署[通用文字识别（简体中文）](deploy-general-ocr.md) |
        | **General OCR - Traditional Chinese**  | no  | 部署[通用文字识别（繁体中文）](deploy-general-ocr-traditional.md) |
        | **Custom Template OCR**  | no  | 部署[自定义模板文字识别](deploy-custom-ocr.md) |
        | **Car License Plate**  | no  | 部署[车牌信息识别](deploy-car-license-plate.md) |
        | **Face Comparison**  | no  | 部署[人脸相似度比对](deploy-face-comparison.md) |
        | **Face Detection**  | no  | 部署[人脸识别](deploy-face-detection.md) |
        | **Human Attribute Recognition**  | no  | 部署[人体结构化属性](deploy-human-attribute-recognition.md) |
        | **Human Image Segmentation**  | no  | 部署[智能人像分割](deploy-human-image-segmentation.md) |
        | **Image Similarity**  | no  | 部署[图片相似度](deploy-image-similarity.md) |
        | **Object Recognition**  | no  | 部署[通用物体识别](deploy-object-recognition.md) |
        | **Pornography Detection**  | no  | 部署[色情内容审核](deploy-pornography-detection.md) |
        | **Image Super Resolution**  | no  | 部署[图像超分辨率](deploy-image-super-resolution.md) |
        | **Text Similarity**  | no  | 部署[文本相似度](deploy-text-similarity.md) |

6. 在**配置堆栈选项**页面，选择**下一步**。

7. 在**审核**页面，查看并确认设置。确保选中确认模板将创建Amazon Identity and Access Management（IAM）资源的复选框。并确保选中Amazon CloudFormation需要的其它功能的复选框。选择**下一步**。

8. 选择**创建堆栈**以部署堆栈。

您可以在Amazon CloudFormation控制台的**状态**列中查看堆栈的状态。创建完成后即可看到状态为**CREATE_COMPLETE**。

## 后续操作

堆栈创建成功后，您可以在Amazon CloudFormation的**输出（Outputs）**标签页中通过对应**参数ID**查询基于Amazon API Gateway的调用URL。

![](./images/output.png)

然后，您可以进行以下操作：

- 查看API并测试API调用。详情可参见[API参考指南](api-explorer.md)。
- 添加或删除AI功能。详情可参见[更新CloudFormation堆栈](deploy-add-delete-api.md)。



[template-china1]:https://cn-north-1.console.amazonaws.cn/cloudformation/home?region=cn-north-1#/stacks/create/template?stackName=AI-Solution-Kit&templateURL=https://aws-gcr-solutions.s3.cn-north-1.amazonaws.com.cn/Aws-gcr-ai-solution-kit/v1.4.0/AI-Solution-Kit.template

[template-global]: https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/template?stackName=AI-Solution-Kit&templateURL=https://aws-gcr-solutions.s3.amazonaws.com/Aws-gcr-ai-solution-kit/v1.4.0/AI-Solution-Kit.template
