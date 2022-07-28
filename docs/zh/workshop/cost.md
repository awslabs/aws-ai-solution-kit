您需要承担运行解决方案时使用亚马逊云科技各个服务的成本费用。截至2022年6月，影响解决方案的成本因素主要包括：

* AWS Lambda调用次数
* AWS Lambda运行时间
* Amazon API Gateway调用次数
* Amazon API Gateway数据输出量
* Amazon CloudWatch Logs存储量
* Amazon OpenSearch Service运行费用
* AI Solution Kit运行时费用

以由西云数据运营的亚马逊云科技中国（宁夏）区域（cn-northwest-1）为例，处理1MB图像，通用物体识别处理时间0.8秒，图片相似度处理时间0.2秒，本workshop运行时间1秒
使用本方案处理此图像所需的成本费用如下表所示

| 服务                                  | 用量                  | 费用      |
|-------------------------------------|---------------------|---------|
| AWS Lambda                     | 调用百万次                 | ¥1.36   |
| AWS Lambda                     | 内存10240MB，每次运行1秒     | ¥1134.8  |
| Amazon API Gateway                | 调用百万次                 | ¥28.94  |
| Amazon API Gateway             | 数据输出以每次10KB计算，¥0.933/GB | ¥9.33   |
| Amazon CloudWatch Logs              | 每次10KB，¥6.228/GB    | ¥62.28  |
| Amazon OpenSearch Service	|实例，c6g.large.searc，¥0.650/小时，按30天计算	|¥468|
| Amazon OpenSearch Service	|EBS，每月每 GB ¥0.896，需要10GB	|¥8.96|
| AI Solution Kit通用物体识别 | 每次处理时间按0.8秒计算	|¥1010.10|
| AI Solution Kit图片相似度	| 每次处理时间按0.2秒计算	|¥329.22|
| 合计                                  |   | ¥3052.99 |