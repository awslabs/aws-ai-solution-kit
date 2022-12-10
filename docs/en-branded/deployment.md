Before you launch the solution, review the architecture, supported regions, and other considerations discussed in this guide. Follow the step-by-step instructions in this section to configure and deploy the solution into your account.

**Deployment time**

- Approximately **10** minutes for deploying an AI feature based on the Amazon Lambda architecture 

- Approximately **20** minutes for deploying an AI feature based on the Amazon SageMaker architecture 

## Prerequisite

If you choose to launch the stack from Amazon Web Services China Regions, make sure a domain registered by ICP is available. For more information, see [ICP Recordal](https://www.amazonaws.cn/en/support/icp/?nc1=h_ls).

## Launch the stack

1. Log in to the Amazon Web Services Management Console and select the link to launch the Amazon CloudFormation stack.

    - [Launch the stack in Global Regions][template-global]
    - [Launch the stack in China Regions][template-china1]
 
2. The template is launched in the default region after you log in to the console. To launch the solution in a different Amazon Web Services Region, use the Region selector in the console navigation bar.

3. On the **Create Stack** page, verify that the correct template URL is displayed in the Amazon S3 URL text box, and choose **Next**.

4. On the **Specify stack details** page, assign a name to your solution stack. For information about naming character limitations, refer to [IAM and STS Limits](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-limits.html) in the *Amazon Web Services Identity and Access Management User Guide*.

5. Under **Parameters**, modify the General Configuration and select the AI features to be deployed, and choose **Next**.

    - You can choose whether to deploy API explorer, and the authentication method of the API gateway.

        | Parameter Name | Default Value | Description |
        | ---------- | ---------| ----------- |
        | **APIExplorer** | yes | Deploys the **API Explorer** to visualize and interact with API resources. See [API Reference Guide](api-explorer.md) for details. If you choose **no**, you can only view the API definitions in API explorer, but cannot perform online test.  |
        | **APIGatewayAuthorization** | NONE | The authentication method of the API gateway. The default is *NONE*, which means no privilege authentication method. You can also choose to use the [IAM](https://docs.aws.amazon.com/zh_cn/apigateway/latest/developerguide/permissions.html) permission to control access to the API. |
        | **APIGatewayStageName** | prod | The first path field in the API gateway (URI). For more information, see [stageVariable](https://docs.aws.amazon.com/en_us/apigateway/latest/developerguide/stage-variables.html). | 

    - You can select the instance type from the list of the feature. The default value for all feature parameters is no.

        | Parameter ID | Default | Description |
        | ---------- | ---------| ----------- |
        | **GeneralOCR** | no | Deploy [General OCR (Simplified Chinese)](deploy-general-ocr.md) |
        | **GeneralOCRTraditional** | no | Deploy [General OCR (Traditional Chinese)](deploy-general-ocr-traditional.md) |
        | **CustomOCR** | no | Deploy [Custom OCR](deploy-custom-ocr.md) |
        | **CarLicensePlate** | no | Deploy [Car License Plate](deploy-car-license-plate.md) |
        | **FaceComparison** | no | Deploy [Face Comparison](deploy-face-comparison.md) |
        | **FaceDetection** | no | Deploy [Face Detection](deploy-face-detection.md) |
        | **HumanAttributeRecognition** | no | Deploy [Human Attribute Recognition](deploy-human-attribute-recognition.md) |
        | **HumanImageSegmentation** | no | Deploy [Human Image Segmentation](deploy-human-image-segmentation.md)|
        | **ImageSimilarity** | no | Deploy [Image Similarity](deploy-image-similarity.md) |
        | **ObjectRecognition** | no | Deploy [Object Recognition](deploy-object-recognition.md) |
        | **PornographyDetection** | no | Deploy [Pornography Detection](deploy-pornography-detection.md) |   
        | **ImageSuperResolution** | no | Deploy [Image Super Resolution](deploy-image-super-resolution.md) |
        | **TextSimilarity** | no | Deploy [Text Similarity](deploy-text-similarity.md) |

6. On the **Configure Stack Options** page, choose **Next**.

7. On the **Review** page, review and confirm the settings. Check the box acknowledging that the template creates Amazon Identity and Access Management (IAM) resources. Choose **Next**.

8. Choose **Create Stack** to deploy the stack.

You can view the status of the stack in the **Status** column of the Amazon CloudFormation console. You should receive a **CREATE_COMPLETE** status when the creation is complete.


## Follow-up actions

After successful deployment, go to the **Outputs** tab in Amazon CloudFormation's console to find the invoke URL based on Amazon API Gateway according to **Parameter ID**.

![](./images/output.png)

Next, you can perform the following operations:

- Check API and test calling API. For more information, see [API Reference Guide](api-explorer.md).
- Add or remove AI features. For more information, see [Update CloudFormation stack](deploy-add-delete-api.md).


[template-china1]:https://cn-north-1.console.amazonaws.cn/cloudformation/home?region=cn-north-1#/stacks/create/template?stackName=AIKitsInferOCRStack&templateURL=https://aws-gcr-solutions.s3.cn-north-1.amazonaws.com.cn/Aws-gcr-ai-solution-kit/v1.2.0/AI-Solution-Kit.template

[template-china2]:https://cn-northwest-1.console.amazonaws.cn/cloudformation/home?region=cn-northwest-1#/stacks/create/template?stackName=AIKitsInferOCRStack&templateURL=https://aws-gcr-solutions.s3.cn-north-1.amazonaws.com.cn/Aws-gcr-ai-solution-kit/v1.2.0/AI-Solution-Kit.template

[template-global]: https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/template?stackName=AIKitsInferOCRStack&templateURL=https://aws-gcr-solutions.s3.amazonaws.com/Aws-gcr-ai-solution-kit/v1.2.0/AI-Solution-Kit.template


