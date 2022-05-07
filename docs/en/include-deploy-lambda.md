## 解决方案架构
用户基于 Amazon Cloudformartion 部署后可以通过调用 HTTP(s) 或 API接口等 方式使用。其中，通过 Amazon API Gateway 创建的 REST API 接口向用户提供 AI 调用服务，用户可以将请求（图片或文本）通过  **HTTP POST**  方式发送请求到 Amazon API Gateway，之后由 Amazon API Gateway 调用 Lambda 完成 AI 文字识别过程并将识别文字及坐标等结果（JSON格式数据）返回给调用端。
本方案使用 Lambda 、 Amazon API Gateway 等无服务架构方案，用户无需担心在云中或本地管理和运行服务器或运行时。只需按实际使用量支付费用。

架构图请参考 **[架构概览: 基于 Lambda 实现](design.md#基于lambda-实现)**
