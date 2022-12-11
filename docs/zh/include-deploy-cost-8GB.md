## 成本预估

您需要承担运行解决方案时使用亚马逊云科技各个服务的成本费用。截至2022年6月，影响解决方案的成本因素主要包括：

- AWS Lambda调用次数
- AWS Lambda运行时间
- Amazon API Gateway调用次数
- Amazon API Gateway数据输出量
- Amazon CloudWatch Logs存储量
- Amazon Elastic Container Registry存储量

## 成本预估示例1 

以由西云数据运营的亚马逊云科技中国（宁夏）区域（cn-northwest-1）为例，处理1MB图像，处理时间1秒

使用本方案处理此图像所需的成本费用如下表所示：

| 服务                                  | 用量                  | 费用      |
|-------------------------------------|---------------------|---------|
| AWS Lambda                     | 调用百万次                 | ¥1.36   |
| AWS Lambda                     | 内存8192MB，每次运行1秒     | ¥907.8  |
| Amazon API Gateway                | 调用百万次                 | ¥28.94  |
| Amazon API Gateway             | 数据输出以每次10KB计算，¥0.933/GB | ¥9.33   |
| Amazon CloudWatch Logs              | 每次10KB，¥6.228/GB    | ¥62.28  |
| Amazon Elastic Container Registry | 0.5GB存储，每月每GB¥0.69    | ¥0.35   |
| 合计                                  |   | ¥1010.06 |

## 成本预估示例2

以美国东部（俄亥俄州）区域（us-east-2）为例，处理1MB图像，处理时间1秒

使用本方案处理此图像所需的成本费用如下表所示：

| 服务                                  | 用量                 | 费用     |
|-------------------------------------|--------------------|--------|
| AWS Lambda                     | 调用百万次                | $0.20  |
| AWS Lambda                     | 内存8192MB，每次运行1秒    | $133.3  |
| Amazon API Gateway                | 调用百万次                | $3.5   |
| Amazon API Gateway             | 数据输出以每次10KB计算，$0.09/GB | $0.9   |
| Amazon CloudWatch Logs              | 每次10KB，$0.50/GB    | $5     |
| Amazon Elastic Container Registry | 0.5GB存储，每月每GB$0.1    | $0.05  |
| 合计                                  |   | $142.95 |

### 成本预估示例3

以美国东部（俄亥俄州）区域（us-east-2）为例，用户一整天都有稳定的图像流，所需QPS约为2。其中Amazon SageMaker终端节点实例开启时会一直计费。

使用本方案的成本费用如下表所示：

| 服务                                  | 用量                                 | 费用      |
|-------------------------------------|------------------------------------|---------|
| Amazon API Gateway                | 调用5 百万次                                | $17.5    |
| Amazon API Gateway              | 数据输出以每次10KB计算，$0.09/GB                  | $4.5    |
| Amazon CloudWatch Logs              | 每次10KB，$0.50/GB                    | $25   |
| Amazon Elastic Container Registry | 0.5GB存储，每月每GB$0.1                    | $0.05   |
| Amazon SageMaker           | 终端节点实例运行1个月，730小时，ml.g4dn.xlarge $0.736/小时 | $537.28  |
| Amazon SageMaker          | 终端节点数据输入以每次1MB计算，$0.016/GB                 | $16     |
| Amazon SageMaker         | 终端节点数据输出以每次10KB计算，$0.016/GB                 | $78.13     |
| 合计                                  |   | $678.46 |