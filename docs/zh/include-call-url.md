### 调用URL

您可以在AWS CloudFormation的**输出**标签页中查看以 **{{ page.meta.feature_id }}** 为前缀的URL。

调用URL有两种方式：

- 如果您在部署解决方案时，将参数**APIGatewayAuthorization**设置为`NONE`，API将允许匿名访问。
- 如果您在部署解决方案时，将参数**APIGatewayAuthorization**设置为`AWS_IAM`，将被要求使用AWS IAM身份验证的调用API。详情可参见[在Amazon API Gateway中调用REST API](https://docs.aws.amazon.com/zh_cn/apigateway/latest/developerguide/how-to-call-api.html)。