您需要承担运行 AI Solution Kit 解决方案时使用亚马逊云科技各个服务的成本费用。截至2022年4月，影响解决方案的成本因素主要包括：

- 向Amazon API Gateway发送请求的次数。
- 调用AWS Lambda的次数。

详情请参阅对应 AI 应用技术手册中的成本预估章节，了解各 AI 应用的部署与使用成本。

# 费用
## OCR
以图像大小1MB，处理时间1秒进行估算
### 宁夏
| 服务                                  | 用量                  | 费用      |
|-------------------------------------|---------------------|---------|
| Amazon Lambda调用                     | 百万次                 | ¥1.36   |
| Amazon Lambda运行                     | 内存4096MB，每次运行1秒     | ¥453.9  |
| Amazon API Gateway调用                | 百万次                 | ¥28.94  |
| Amazon API Gateway数据输出              | 以每次10KB计算,¥0.933/GB | ¥9.33   |
| Amazon CloudWatch Logs              | 每次10KB,¥6.228/GB    | ¥62.28  |
| Amazon Elastic Container Registry存储 | 0.5GB,每月每GB¥0.69    | ¥0.35   |
| 合计                                  |   | ¥556.16 |
​
### 美国东部(俄亥俄)
| 服务                                  | 用量                 | 费用     |
|-------------------------------------|--------------------|--------|
| Amazon Lambda调用                     | 百万次                | $0.20  |
| Amazon Lambda运行                     | 内存4096MB，每次运行1秒    | $66.7  |
| Amazon API Gateway调用                | 百万次                | $3.5   |
| Amazon API Gateway数据输出              | 以每次10KB计算,$0.09/GB | $0.9   |
| Amazon CloudWatch Logs              | 每次10KB,$0.50/GB    | $5     |
| Amazon Elastic Container Registry存储 | 0.5GB,每月每GB$0.1    | $0.05  |
| 合计                                  |   | $76.35 |
​
## 人像扣图
以图像大小1MB，处理时间4秒进行估算
### 宁夏
| 服务 | 用量                   | 费用       |
| ---- |----------------------|----------|
|Amazon Lambda调用 | 百万次                  | ¥1.36    |
|Amazon Lambda运行| 内存4096MB，每次运行4秒      | ¥1815.6  |
|Amazon API Gateway调用| 百万次                  | ¥28.94   |
|Amazon API Gateway数据输出| 以每次100KB计算,¥0.933/GB | ¥93.3    |
|Amazon CloudWatch Logs| 每次10KB,¥6.228/GB     | ¥62.28   |
|Amazon Elastic Container Registry存储| 0.5GB,每月每GB¥0.69     | ¥0.35    |
| 合计                                  |   | ¥2001.83 |
### 美国东部(俄亥俄)
| 服务                                  | 用量                  | 费用      |
|-------------------------------------|---------------------|---------|
| Amazon Lambda调用                     | 百万次                 | $0.20   |
| Amazon Lambda运行                     | 内存4096MB，每次运行4秒     | $266.8  |
| Amazon API Gateway调用                | 百万次                 | $3.5    |
| Amazon API Gateway数据输出              | 以每次100KB计算,$0.09/GB | $9      |
| Amazon CloudWatch Logs              | 每次10KB,$0.50/GB     | $5      |
| Amazon Elastic Container Registry存储 | 待定GB,每月每GB$0.1      | $0.05   |
| 合计                                  |   | $284.55 |
​
## 超分
### 美国东部(俄亥俄)
处理一张图按1秒计算，Amazon SageMaker 终端节点实例开启时会一直计费，这里仅计算处理完1百万图片需要消耗时长对应的实例费用
​
| 服务                                  | 用量                                 | 费用      |
|-------------------------------------|------------------------------------|---------|
| Amazon Lambda调用                     | 百万次                                | $0.20   |
| Amazon Lambda运行                     | 内存4096MB，每次运行1秒                    | $66.7   |
| Amazon API Gateway调用                | 百万次                                | $3.5    |
| Amazon API Gateway数据输出              | 以每次4MB计算,$0.09/GB                  | $360    |
| Amazon CloudWatch Logs              | 每次10KB,$0.50/GB                    | $0.05   |
| Amazon Elastic Container Registry存储 | 0.5GB,每月每GB$0.1                    | $0.05   |
| Amazon SageMaker 终端节点实例           | 需要运行278小时，ml.inf1.xlarge $0.297/小时 | $82.57  |
| Amazon SageMaker 终端节点数据输入         | 以每次1MB计算，$0.016/GB                 | $16     |
| Amazon SageMaker 终端节点数据输出         | 以每次4MB计算，$0.016/GB                 | $64     |
| 合计                                  |   | $593.07 |