登陆亚马逊云科技控制台<https://cn-north-1.console.amazonaws.cn/console>，
然后点击此[链接](https://cn-north-1.console.amazonaws.cn/cloudformation/home?region=cn-north-1#/stacks/create/template?stackName=AI-Solution-Kit&templateURL=https://aws-gcr-solutions.s3.cn-north-1.amazonaws.com.cn/Aws-gcr-ai-solution-kit/v1.2.0/AI-Solution-Kit.template)进入CloudFormation部署页面，在页面底部右下角选择**下一步**。
![](images/deploy-ask-1.png)
在**指定堆栈详细信息**页面的参数部分对API的部署进行配置。把图片相似度（Image Similarity）和对象检测（Object Recognition）的参数设置为“yes”，其他保持默认不变，在页面底部右下角选择**下一步**。
![](images/deploy-ask-2.png)
在**配置堆栈选项**页面，选择保留已成功预置的资源，其他保持默认，在页面底部右下角选择**下一步**。
![](images/deploy-ask-3.png)
在**审核**页面，查看并确认设置。在页面底部，确保选中确认模板将创建Amazon Identity and Access Management（IAM）资源的复选框。并确保选中Amazon CloudFormation需要的其它功能的复选框。选择右下角橙色**创建堆栈**按钮。
![](images/deploy-ask-4.png)
整个堆栈的创建过程预计将花费大约*五分钟*。可以在CloudFormation控制台的*状态*列中查看堆栈的状态。创建完成后即可看到状态为*CREATE_COMPLETE*。
![](images/deploy-ask-5.png)
堆栈创建成功后，您可以在AI Solution Kit的堆栈输出（Outputs）标签页中通过对应键查看基于Amazon API Gateway的调用URL。记录下**StagebaseURL**的值，后续实验会使用
![](images/deploy-ask-6.png)