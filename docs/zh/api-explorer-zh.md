当您通过 Amazon CloudFormation [部署解决方案](deployment-zh.md#amazon-cloudformation)，并将参数 **APIExplorer** 设置为 *yes*，即可在方案部署结束后在 Amazon CloudFormation 的 Outputs 标签页中看到以 **AIExplorer** 为前缀的URL，通过该URL即可访问基于 [Swagger UI](https://swagger.io/tools/swagger-ui/) 的API 资源浏览器。

API 资源浏览器提供了一个显示框架，提供基于 [Swagger UI](https://swagger.io/tools/swagger-ui/) 的交互式文档网站，方便用户读取基于 OpenAPI 规范定义的 AI 应用接口规范文档并支持集成测试。下面以**通用文本识别**为例，介绍如何使用 **API 资源浏览器**查看并测试 API 调用。

//TODO