## 成本预估

您需要承担运行解决方案时使用亚马逊云科技各个服务的成本费用。截至2022年6月，影响解决方案的成本因素主要包括：

- Amazon API Gateway调用次数
- Amazon API Gateway数据输出量
- Amazon CloudWatch Logs存储量
- Amazon Elastic Container Registry存储量

如果您选择基于Amazon Lambda架构部署，影响成本的因素还包括：
- Amazon Lambda调用次数
- Amazon Lambda运行时间

与之对应的Amazon SageMaker架构部署，影响成本的因素还包括：
- Amazon SageMaker终端节点实例类型
- Amazon SageMaker终端节点数据输入量
- Amazon SageMaker终端节点数据输出量

## 成本预估示例1 

以由西云数据运营的亚马逊云科技中国（宁夏）区域（cn-northwest-1）为例，处理1MB图像，处理时间1秒

使用本方案处理此图像所需的成本费用如下表所示：

| 服务                                  | 用量                  | 费用      |
|-------------------------------------|---------------------|---------|
| Amazon Lambda                     | 调用百万次                 | ¥1.36   |
| Amazon Lambda                     | 内存10240MB，每次运行1秒     | ¥1134.8  |
| Amazon API Gateway                | 调用百万次                 | ¥28.94  |
| Amazon API Gateway             | 数据输出以每次10KB计算，¥0.933/GB | ¥9.33   |
| Amazon CloudWatch Logs              | 每次10KB，¥6.228/GB    | ¥62.28  |
| Amazon Elastic Container Registry | 0.5GB存储，每月每GB¥0.69    | ¥0.35   |
| 合计                                  |   | ¥1237.06 |

## 成本预估示例2

以美国东部（俄亥俄州）区域（us-east-2）为例，处理1MB图像，处理时间1秒

使用本方案处理此图像所需的成本费用如下表所示：

| 服务                                  | 用量                 | 费用     |
|-------------------------------------|--------------------|--------|
| Amazon Lambda                     | 调用百万次                | $0.20  |
| Amazon Lambda                     | 内存10240MB，每次运行1秒    | $166.7  |
| Amazon API Gateway                | 调用百万次                | $3.5   |
| Amazon API Gateway             | 数据输出以每次10KB计算，$0.09/GB | $0.9   |
| Amazon CloudWatch Logs              | 每次10KB，$0.50/GB    | $5     |
| Amazon Elastic Container Registry | 0.5GB存储，每月每GB$0.1    | $0.05  |
| 合计                                  |   | $176.35 |