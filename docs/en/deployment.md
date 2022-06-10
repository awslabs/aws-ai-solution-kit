This section describes how to deploy the **AI Solution Kit** solution via **Amazon CloudFormation**. Detailed deployment and usage instructions for the AI applications included in the solution are described in detail in the corresponding. Before deploying the solution, it is recommended that you review the information in this guide regarding architecture diagrams and regional support, and then follow the instructions below to configure the solution and deploy it to your account.

**Deployment time**

- Deploying an AI application based on the Amazon Lambda architecture: approximately **10** minutes

- Deploying an AI application based on the Amazon SageMaker architecture: approximately **20** minutes

!!! Note
    When users activate multiple APIs in Amazon CloudFormation at the same time, the deployment time is the stacked time for each individual API.

## Deployment Overview

**Prerequisites (China region)**

This solution uses Amazon API Gateway to receive API call requests, so if you want to provide API requests without authentication in the Beijing region, you need to apply and ensure that your Amazon Web Services account has been filed with the Internet Content Provider (ICP) and that port 80 For details, please refer to the [ICP filing instructions](https://s3.cn-north-1.amazonaws.com.cn/sinnetcloud/ICP+recordal/ICP%E5%A4%87%E6%A1%88%E8%AF%B4%E6%98%8E.pdf). 8E.pdf).

### Deploy the Amazon CloudFormation template

1. Log in to the Amazon Web Services Management Console and select the link to launch the AWS CloudFormation template.

| Quick Launch Link | Description |
| ---------- | --- |
| [link for Amazon CloudTech China (Beijing) region operated by Halo New Network][template-china1] | Deploy AI Solution Kit in **Beijing** region |
| [Amazon Cloud Technologies China (Ningxia) Regional Link][template-china2] operated by West Cloud Data | Deploying AI Solution Kit in **Ningxia** region
| [global-region link][template-global] | Deploy AI Solution Kit in **Global** region | 2.

2. By default, the template will be launched in the default region after you log in to the console. If you need to launch the solution in the specified Amazon Web Service region, select it from the region drop-down list in the console navigation bar.

3. On the **Create Stack** page, verify that the correct template URL is displayed in the Amazon S3 URL text box, and then select **Next**.

4. On the **Assign Stack Details** page, assign a name to your solution stack that is unique within the account and meets the naming requirements.

5. In the **Parameters** section, there are two sections of parameters, **General Configuration** and **AI Application List**, where you can modify the General Configuration and select the AI applications to be deployed as needed, and then select **Next**.

    #### **Common Configuration Parameters**

    | Parameter Name | Default Value | Description |
    | ---------- | ---------| ----------- |
    | **APIGatewayAuthorization** | AWS_IAM | The authentication method of the API gateway. The default is *AWS_IAM*, which will automatically use the [IAM](https://docs.aws.amazon.com/zh_cn/apigateway/latest/developerguide/permissions.html) permission to control access to the API. You can also choose *NONE* which is the no privilege authentication method (insecure) and the user will need to manually configure the required [Resource Access Policy](https://docs.aws.amazon.com/zh_cn/apigateway/latest/) in the API Gateway console after deploying the solution. developerguide/apigateway-control-access-to-api.html). |
    | **APIGatewayStageName** | prod | The first path field in the API gateway (URI). See also: [stageVariable](https://docs.aws.amazon.com/zh_cn/apigateway/latest/developerguide/stage-variables.html) |
    | **APIExplorer** | yes | Deploys the **API Resource Explorer** based on [Swagger UI](https://swagger.io/tools/swagger-ui/) to visualize and interact with API resources. It is automatically generated based on the OpenAPI (formerly known as Swagger) specification and makes it easy to view API definitions and tests through visual documentation. For more information, see: [API Resource Explorer](api-explorer.md) |

    #### **AI Application List Parameters**

    | Parameter ID | Default | Description |
    | ---------- | ---------| ----------- |
    | **GeneralOCR** | no | Deploy **General OCR**, check 'yes' if you want to deploy, see [General OCR](deploy-general-ocr.md) |
    | **GeneralOCRTraditional** | no | Deploy **GeneralOCR(Traditional Chinese)**, please check 'yes' if you want to deploy, please refer to [GeneralOCR(Traditional Chinese)](deploy-general-ocr-traditional.md) |
    | **CustomOCR** | no | Deploy **Custom Template OCR**, please check 'yes' if you want to deploy, please refer to [Custom Template OCR](deploy-custom-ocr.md) |
    | **CarLicensePlate** | no | Deploy **Car License Plate Recognition**, please check 'yes' if you want to deploy, please see [Car License Plate Recognition](deploy-car-license-plate.md) |
    | **PornographyDetection** | no | deploy**PornographyDetection**, please check 'yes' if you want to deploy, please see [Pornography Detection](deploy-pornography-detection.md) |
    | **ImageSimilarity** | no | Deploy **ImageSimilarity**, check 'yes' if you want to deploy, see [Image Similarity](deploy-image-similarity.md) |
    | **HumanImageSegmentation** | no | Deploy **HumanImageSegmentation**, please check 'yes' if you want to deploy, please see the [Human Image Segmentation](deploy-human-image-segmentation.md) |
    | **ObjectRecognition** | no | Deploy **Object Recognition**, please check 'yes' if you want to deploy, please see [Object Recognition](deploy-object-recognition.md) |
    | **FaceDetection** | no | Deploy **Face Detection**, check 'yes' if you want to deploy, see [Face Detection](deploy-face-detection.md) |
    | **FaceComparison** | no | Deploy **Face Comparison**, please check 'yes' if you want to deploy, see [Face Comparison](deploy-face-comparison.md) |
    | **HumanAttributeRecognition** | no | Deploy **Human Attribute Recognition**, please check 'yes' if you want to deploy, see [Human Attribute Recognition](deploy-human-attribute-recognition.md) |
    | **ImageSuperResolution** | no | Deploy **Image Super Resolution**, check 'yes' if you want to deploy, see [Image Super Resolution](deploy-image-super-resolution.md) |
    | **TextSimilarity** | no | Deploy **Text Similarity**, check 'yes' if you want to deploy, see the [Text Similarity](deploy-text-similarity.md) |

6. On the **Configure Stack Options** page, select **Next**.

7. On the **Review** page, review and confirm the settings. Ensure that the checkbox to confirm that the template will create an Amazon Identity and Access Management (IAM) resource is checked. Select **Next**.

8. Select **Create Stack** to deploy the stack.

You can view the status of the stack in the **Status** column of the AWS CloudFormation console. You can see the status as **CREATE_COMPLETE** when the creation is complete.

!!! Tip
    After successful deployment, you can open the **AI Solution Kit** main stack in AWS CloudFormation's console and switch to the **Outputs** (Outputs) tab to query the Amazon API Gateway-based call URL by the corresponding **Parameter ID**.

### Updating the Amazon CloudFormation Stack

With Amazon CloudFormation, you can change the properties of existing resources in your stack, and if you need to add or remove deployed AI features, you can do so by updating your stack.

In the Amazon CloudFormation console, select the completed AI Solution Kit stack that you created in the Stack list. 2.

In the Stack Details pane, select Update. 3.

In the Template Parameters section, specify the AI feature or parameter information that needs to be added or removed, and then select Next. 4.

4. On the **Configure Stack Options** page, select **Next**. 5.

5. On the **Review** page, review and confirm the settings. Ensure that the checkbox to confirm that the template will create an Amazon Identity and Access Management (IAM) resource is checked. Select **Next**. 6.

6. If you are satisfied with the changes made, select Updata stack.

[template-china1]:https://cn-north-1.console.amazonaws.cn/cloudformation/home?region=cn-north-1#/stacks/create/template?stackName=AIKitsInferOCRStack&templateURL=https://aws-gcr-solutions.s3.cn-north-1.amazonaws.com.cn/Aws-gcr-ai-solution-kit/v1.2.0/AI-Solution-Kit.template

[template-global]: https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/template?stackName=AIKitsInferOCRStack&templateURL=https://aws-gcr-solutions.s3.amazonaws.com/Aws-gcr-ai-solution-kit/v1.2.0/AI-Solution-Kit.template
