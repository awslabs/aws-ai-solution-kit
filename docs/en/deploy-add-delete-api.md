## Add or remove AI features

You can update the AWS CloudFormation stack to add new AI features or remove the AI feature already deployed. 

1. Sign in to the [AWS CloudFormation console](https://console.aws.amazon.com/cloudformation/).

2. Select the root stack of this solution, not the nested stack. 

3. Choose **Update**.

    ![](./images/update.png)

4. Select **Use current template**, and choose **Next**.

5. Update the parameters as needed, and choose **Next**. For example, if you have chosen `no` for **Custom Template OCR**, you can change it to `yes-Lambda` or `yes-SageMaker` to add this feature.

6. On the **Configure stack options** page, choose **Next**.

7. On the **Review** page, review and confirm the settings. Check the box acknowledging that the template will create AWS Identity and Access Management (IAM) resources.

8. Choose **Update stack** to update the stack.

[template-china1]:https://cn-north-1.console.amazonaws.cn/cloudformation/home?region=cn-north-1#/stacks/create/template?stackName=AIKitsInferOCRStack&templateURL=https://aws-gcr-solutions.s3.cn-north-1.amazonaws.com.cn/Aws-gcr-ai-solution-kit/v1.2.0/AI-Solution-Kit.template

[template-china2]:https://cn-northwest-1.console.amazonaws.cn/cloudformation/home?region=cn-northwest-1#/stacks/create/template?stackName=AIKitsInferOCRStack&templateURL=https://aws-gcr-solutions.s3.cn-north-1.amazonaws.com.cn/Aws-gcr-ai-solution-kit/v1.2.0/AI-Solution-Kit.template

[template-global]: https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/template?stackName=AIKitsInferOCRStack&templateURL=https://aws-gcr-solutions.s3.amazonaws.com/Aws-gcr-ai-solution-kit/v1.2.0/AI-Solution-Kit.template
