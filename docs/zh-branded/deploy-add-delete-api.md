## 添加或删除AI功能

您可以通过修改Amazon CloudFormation堆栈中现有资源的属性，添加新的AI功能或删除已经部署的AI功能。

1. 访问[Amazon CloudFormation控制台](https://console.aws.amazon.com/cloudformation/)。

2. 从堆栈列表中选择部署完成的解决方案根堆栈，注意不要选择嵌套堆栈（NESTED）。

3. 在**堆栈详细信息**页面，选择**更新**。

    ![](./images/update.png)

4. 在**指定模板**页面，选择**使用当前模板**，然后选择**下一步**。

5. 在参数部分，更改相应的参数信息，然后选择**下一步**。例如，如果**Custom Template OCR**原来为no，可以更改设置为yes-Lambda或yes-SageMaker，从而添加**自定义模板文字识别**功能。

6. 在**配置堆栈选项**页面，选择**下一步**。

7. 在**审核**页面，查看并确认设置。确保选中确认模板将创建Amazon Identity and Access Management（IAM）资源的复选框。选择**下一步**。

8. 确认更改，并选择**更新堆栈**。

[template-china1]:https://cn-north-1.console.amazonaws.cn/cloudformation/home?region=cn-north-1#/stacks/create/template?stackName=AIKitsInferOCRStack&templateURL=https://aws-gcr-solutions.s3.cn-north-1.amazonaws.com.cn/Aws-gcr-ai-solution-kit/v1.2.0/AI-Solution-Kit.template

[template-global]: https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/template?stackName=AIKitsInferOCRStack&templateURL=https://aws-gcr-solutions.s3.amazonaws.com/Aws-gcr-ai-solution-kit/v1.2.0/AI-Solution-Kit.template
