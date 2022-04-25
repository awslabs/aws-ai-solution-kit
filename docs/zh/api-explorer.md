API 资源浏览器提供了一个显示框架，提供基于 [Swagger UI](https://swagger.io/tools/swagger-ui/) 的交互式文档网站，方便用户读取基于 OpenAPI 规范定义的 AI 应用接口规范文档并支持集成测试。下面以**通用文本识别**为例，介绍如何使用 **API 资源浏览器**查看并测试 API 调用。

当您通过 Amazon CloudFormation [部署解决方案](deployment.md#amazon-cloudformation)，并将参数 **APIExplorer** 设置为 *yes*，即可在方案部署结束后在 Amazon CloudFormation 的 Outputs 标签页中看到以 **AIExplorer** 对应的URL，点击URL即可访问基于 [Swagger UI](https://swagger.io/tools/swagger-ui/) 的API 资源浏览器。

打开该页面后，即可看到所有基于 **OpenAPI** 定义的 API 交互文档，如果用户在部署方案时没有激活（active）交互文档中对应的 API，则在 API Explorer 中只能看到该 API 的参考定义，而不能进行在线测试等操作。API 已经按功能类型分为Optical Character Recognition(OCR)（文字识别），Facial & Body（人脸和人体识别），Image Understanding（图像理解），Computer Vision Production（视觉内容生产），Natural Language Understanding（自然语言理解）五类，在展开对应类型后，即可查看到 API 的请求方法与模式定义，如果用户部署了该 API，还可以点击右侧的测试（Try it out）按钮并在 Request body 中 输入正确的 Body 请求数据进行测试，并看到结果。目前该测试功能仅适用于 API Gateway 认证方式为 NONE 的情况。

这里以**通用文字识别** API 为例，介绍 API 测试方式。

-  依次展开 **Optical Character Recognition(OCR)** 标签里的 **/general-ocr-standard** 路径，即可以看到**通用文字识别（简体中文）** API 标准模型的请求方法。
-  点击 **Try it out**，在 **Request body** 下方的空白栏处输入用于测试的样本数据，如：
``` json
{
"url": "https://images-cn.ssl-images-amazon.cn/images/G/28/AGS/LIANG/Deals/2020/Dealpage_KV/1500300.jpg"
}
```
-  确认格式正确后，点击下方蓝色 **Execute** （运行），运行结束后即可在 **Responses body** （响应）中看到处返回的文字识别JSON结果，可以通过右侧复制或下载按钮链接保存处理结果。
- 在 **Response headers** （响应头信息）中可以查看响应头信息的细节内容。
- 点击蓝色 **Execute** （运行）右侧 **Clear**（清空）按钮，即可清空 **Request body** 与 **Responses** 测试结果。