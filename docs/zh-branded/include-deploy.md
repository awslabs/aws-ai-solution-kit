## 快速部署

1. 登录[亚马逊云科技管理控制台](https://console.aws.amazon.com/)。 

2. 通过Amazon CloudFormation部署 **{{ page.meta.feature_name }}**功能，具体步骤可参见 [**部署解决方案**](deployment.md)。请务必确认在**参数**部分将 **{{ page.meta.feature_id }}** 参数设置为 *yes* 。

3. 访问[Amazon CloudFormation控制台](https://console.aws.amazon.com/cloudformation/)。

4. 从堆栈列表中查看包含 **{{ page.meta.feature_id }}** 名称的嵌套堆栈（Nested Stack）。

部署时间：**{{ page.meta.deployment_time }}**

