API资源浏览器为一个显示框架，提供基于[Swagger UI](https://swagger.io/tools/swagger-ui/)的交互式文档网站，方便用户读取基于OpenAPI规范定义的AI应用接口规范文档并支持集成测试。

下面以通用文本识别为例，介绍如何使用API资源浏览器查看API并测试API调用。
## 前提条件

通过AWS CloudFormation[部署解决方案](deployment.md#amazon-cloudformation)时，您需要：

- 设置参数 **API Explorer**为*yes*。
- 设置参数**API Gateway Authorization**为*NONE*。

否则，在API Explorer中只能看到该API的参考定义，而不能进行在线测试等操作。

## 查看API

1. 访问[AWS CloudFormation控制台](https://console.aws.amazon.com/cloudformation/)。
2. 从堆栈列表中选择方案的根堆栈。
3. 打开**输出**标签页，找到**APIExplorer**对应的URL。
4. 点击URL访问API资源浏览器。
5. 查看所有基于OpenAPI规范定义的API交互文档。

    本方案提供的API按功能类型划分为五类：

    - Optical Character Recognition(OCR)（文字识别）
    - Facial & Body（人脸和人体识别）
    - Image Understanding（图像理解）
    - Computer Vision（视觉内容生产）
    - Natural Language（自然语言理解）

6. 展开对应类型查看API的请求方法与模式定义。

    !!! Note "说明"
        
        对于部署解决方案时选中的API，您可以点击右侧的测试（Try it out）按钮并在Request body中输入正确的Body请求数据进行测试，并查看测试结果。

## 测试API调用

1. 依次展开**Optical Character Recognition(OCR)**标签里的 **/general-ocr-standard** 路径，可以看到通用文字识别（简体中文）API标准模型的请求方法。
2. 点击**Try it out**，在**Request body**下方的空白栏处输入用于测试的样本数据。例如：

``` json
{
"url": "https://images-cn.ssl-images-amazon.cn/images/G/28/AGS/LIANG/Deals/2020/Dealpage_KV/1500300.jpg"
}
```

3. 确认格式正确后，点击下方的**Execute**。运行结束后即可在**Responses body**中看到返回的文字识别JSON结果。您还可以通过右侧复制或下载按钮保存处理结果。
4. 在**Response headers**中查看响应头信息的细节内容。
5. （可选）点击**Execute**右侧**Clear**按钮，即可清空**Request body**与**Responses**测试结果。