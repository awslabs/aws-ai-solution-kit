## 成本预估 

您需要承担运行 AI Solution Kit 解决方案时使用亚马逊云科技各个服务的成本费用。截至2022年4月，影响解决方案的成本因素主要包括：

- Amazon Lambda调用
- Amazon Lambda运行
- Amazon API Gateway调用
- Amazon API Gateway数据输出
- Amazon CloudWatch Logs
- Amazon Elastic Container Registry存储

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