## 在中国区域部署解决方案如何开通ICP备案？

本解决方案使用Amazon API Gateway来接收API调用请求，所以如果您希望在中国区域提供无需身份验证即可访问的API请求，需要申请并确保您的AWS账号已通过Internet Content Provider (ICP) 备案，80/443端口可以正常开启。具体流程可参见[ICP备案说明](https://s3.cn-north-1.amazonaws.com.cn/sinnetcloud/ICP+recordal/ICP%E5%A4%87%E6%A1%88%E8%AF%B4%E6%98%8E.pdf)。

## 部署解决方案时遇到*The account-level service limit 'ml.g4dn.xlarge for endpoint usage' is 0 Instances*，如何解决？

方案中的超分辨率API需要创建一个基于**Amazon SageMaker**的GPU类型实例，如果您AWS账户中对应实例限制不足，则会导致该功能部署异常。您可以在AWS管理控制台上方工具栏点击**支持中心**，创建支持工单，要求提高**Amazon SageMaker**服务的实例限额。具体步骤请参阅：[请求提高配额（目前此内容仅使用英语显示）](https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html)

## 部署解决方案时遇到*Resource handler returned message: "'MemorySize' value failed to satisfy constraint: Member must have value less than or equal to 3008*，如何解决？

方案中默认的**AWS Lambda**内存约为4GB（4096 MB），如果您AWS账户中AWS Lambda函数限制低于4096 MB，则会导致该部署异常。您可以在AWS管理控制台上方工具栏点击**支持中心**，创建支持工单，要求提高 **Lambda**服务的内存限额。具体步骤请参阅：[请求提高配额（目前此内容仅使用英语显示）](https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html)

## 使用解决方案都需要哪些AWS Identity and Access Management (IAM)权限？

您在部署解决方案之后，可以通过Amazon API Gateway调用API，需要的权限如下。其中**sagemaker:**仅限于**图像超分辨率**API。

| Actions |
| ------------------------------------- |
| apigateway:DELETE                     |
| apigateway:GET                        |
| apigateway:PATCH                      |
| apigateway:POST                       |
| apigateway:PUT                        |
| cloudformation:CancelUpdateStack      |
| cloudformation:ContinueUpdateRollback |
| cloudformation:CreateChangeSet        |
| cloudformation:CreateStack            |
| cloudformation:DeleteStack            |
| cloudformation:DescribeChangeSet      |
| cloudformation:DescribeStackEvents    |
| cloudformation:DescribeStackResources |
| cloudformation:DescribeStacks         |
| cloudformation:GetStackPolicy         |
| cloudformation:GetTemplateSummary     |
| cloudformation:ListChangeSets         |
| cloudformation:ListStackResources     |
| cloudformation:ListStacks             |
| cloudformation:RollbackStack          |
| cloudformation:UpdateStack            |
| cloudformation:UpdateStackSet         |
| ecr:BatchCheckLayerAvailability       |
| ecr:BatchDeleteImage                  |
| ecr:BatchGetImage                     |
| ecr:CreateRepository                  |
| ecr:DeleteRepository                  |
| ecr:DescribeRepositories              |
| ecr:GetDownloadUrlForLayer            |
| ecr:GetRepositoryPolicy               |
| ecr:InitiateLayerUpload               |
| ecr:PutImage                          |
| ecr:SetRepositoryPolicy               |
| iam:AttachRolePolicy                  |
| iam:CreateRole                        |
| iam:DeleteRole                        |
| iam:DeleteRolePolicy                  |
| iam:DetachRolePolicy                  |
| iam:GetRole                           |
| iam:ListRoles                         |
| iam:PassRole                          |
| iam:PutRolePolicy                     |
| lambda:AddPermission                  |
| lambda:CreateFunction                 |
| lambda:DeleteFunction                 |
| lambda:GetFunction                    |
| lambda:InvokeFunction                 |
| lambda:RemovePermission               |
| lambda:UpdateFunctionConfiguration    |
| s3:GetObject                          |
| sagemaker:CreateEndpoint              |
| sagemaker:CreateEndpointConfig        |
| sagemaker:CreateModel                 |
| sagemaker:DeleteEndpoint              |
| sagemaker:DeleteEndpointConfig        |
| sagemaker:DeleteModel                 |
| sagemaker:DescribeEndpoint            |
| sagemaker:DescribeEndpointConfig      |
| sagemaker:DescribeModel               |
| sagemaker:InvokeEndpoint              |
| sns:ListTopics                        |

## 如何统一切换Amazon API Gateway中API的访问认证方式？

您可以通过AWS CloudFormation更新堆栈，从而统一修改现有资源的属性。

1. 访问[AWS CloudFormation控制台](https://console.aws.amazon.com/cloudformation/)。

2. 从堆栈列表中选择部署完成的方案根堆栈。

3. 在**堆栈详细信息**页面，选择**更新**。

4. 在**指定模板**页面，选择**使用当前模板**，然后选择**下一步**。

5. 在模板参数部分，修改**API Gateway Authorization**参数，然后选择**下一步**。

6. 在**配置堆栈选项**页面，选择**下一步**。

7. 在**审核**页面，查看并确认设置。确保选中确认模板将创建Amazon Identity and Access Management（IAM）资源的复选框。选择**下一步**。

8. 确认更改，并选择**更新堆栈**。

## 如何单独切换Amazon API Gateway中API的访问认证方式？

1. 访问[Amazon API Gateway控制台](https://console.aws.amazon.com/apigateway/)。
2. 从API列表中选择最新创建的方案API，打开API页面。您也可以按**已创建**的时间排序，便于查找。
3. 展开资源树，找到需要修改访问权限的资源路径下的**OPTIONS**节点，点击该节点打开**方法执行**配置页面。
4. 点击下方的**方法请求**链接。
5. 点击**授权**右侧的编辑按钮，展开下拉列表，选择**Amazon IAM**。
6. 点击**更新**按钮完成修改。更新完成后，授权项应显示为**Amazon IAM**。
7. 点击资源树中**OPTIONS**下方**POST**按钮，和修改OPTIONS的方法一样，在方法请求中将授权方式修改为**Amazon IAM**。
8. 点击方法执行左侧的**操作**下拉列表，选择**API操作**中的**部署 API**选项。
9. 在**部署API**对话框，选择**prod**或自定义名称的部署阶段，请不要选择[新阶段]，然后点击下方部署按钮完成部署。

## 如何创建和使用带API密钥的使用计划？
本解决方案支持API使用计划（Usage Plans）。部署解决方案并测试API后，您可以实施API Gateway使用计划，将它们作为面向客户的产品/服务提供。您可以配置使用计划和API密钥，以允许客户按照商定的可满足其业务需求和预算限制的请求速率和配额来访问选定API。

如果需要的话，您可以为API设置默认方法级别限制或为单个API方法设置限制。API调用方必须在API请求的x-api-key标头中提供一个已分配的API密钥。 

如您需要配置*API使用计划*，请参考[配置使用计划](https://docs.aws.amazon.com/zh_cn/apigateway/latest/developerguide/api-gateway-create-usage-plans.html)。

## 通用目标检测 API 目前支持哪些目标识别？

以下为目标检测支持的实体列表：

| ID                    | 名称                |
| ---------------------------- | ------------------ |
| accordion                    | 手风琴                |
| airplane                     | 飞机                 |
| alligator                    | 鳄鱼                 |
| apple                        | 苹果                 |
| army\_tank                   | 军队坦克               |
| awning                       | 棚                  |
| backpack                     | 背包                 |
| ball                         | 球                  |
| balloon                      | 气球                 |
| banana                       | 香蕉                 |
| barrel                       | 桶                  |
| baseball                     | 棒球                 |
| baseball\_bat                | 棒球棒                |
| baseball\_glove              | 棒球手套               |
| basket                       | 篮子                 |
| bathtub                      | 浴缸                 |
| bear                         | 熊                  |
| bed                          | 床                  |
| bee                          | 蜜蜂                 |
| beer\_bottle                 | 啤酒瓶                |
| bell\_pepper                 | 灯笼椒                |
| belt                         | 腰带                 |
| bench                        | 长椅                 |
| bicycle                      | 自行车                |
| billboard                    | 广告牌                |
| bird                         | 鸟                  |
| blackboard                   | 黑板                 |
| boat                         | 船                  |
| book                         | 书                  |
| bookcase                     | 书柜                 |
| boot                         | 开机                 |
| bottle                       | 瓶子                 |
| bowl                         | 碗                  |
| bowling\_ball                | 保龄球                |
| box                          | 盒子                 |
| bracelet                     | 手镯                 |
| brassiere                    | 乳罩                 |
| bread                        | 面包                 |
| broccoli                     | 西兰花                |
| building                     | 建造                 |
| bus\_(vehicle)               | 公共汽车\_（车辆）         |
| butterfly                    | 蝴蝶                 |
| cabinet                      | 内阁                 |
| cake                         | 蛋糕                 |
| camel                        | 骆驼                 |
| camera                       | 相机                 |
| can                          | 能够                 |
| candle                       | 蜡烛                 |
| candy\_bar                   | 糖果条                |
| cannon                       | 大炮                 |
| canoe                        | 独木舟                |
| car\_(automobile)            | car\_(汽车)          |
| carrot                       | 胡萝卜                |
| cart                         | 大车                 |
| castle                       | 城堡                 |
| cat                          | 猫                  |
| caterpillar                  | 毛虫                 |
| cello                        | 大提琴                |
| cellular\_telephone          | 蜂窝电话               |
| chair                        | 椅子                 |
| chicken\_(animal)            | 鸡\_（动物）            |
| chopping\_board              | 切菜板                |
| chopstick                    | 筷子                 |
| christmas\_tree              | 圣诞树                |
| clock                        | 钟                  |
| coat                         | 外套                 |
| cocktail                     | 鸡尾酒                |
| coffee\_table                | 咖啡桌                |
| coin                         | 硬币                 |
| computer\_keyboard           | 计算机键盘              |
| computer\_monitor            | 电脑显示器              |
| cone                         | 锥体                 |
| cookie                       | 曲奇饼                |
| cow                          | 牛                  |
| cowboy\_hat                  | 牛仔帽                |
| crab\_(animal)               | 螃蟹\_（动物）           |
| crown                        | 王冠                 |
| cucumber                     | 黄瓜                 |
| cup                          | 杯子                 |
| cupboard                     | 橱柜                 |
| curtain                      | 窗帘                 |
| deer                         | 鹿                  |
| desk                         | 桌子                 |
| dessert                      | 甜点                 |
| dinosaur                     | 恐龙                 |
| dog                          | 狗                  |
| doll                         | 玩具娃娃               |
| dolphin                      | 海豚                 |
| door                         | 门                  |
| doorknob                     | 门把手                |
| doughnut                     | 甜甜圈                |
| dragonfly                    | 蜻蜓                 |
| drawer                       | 抽屉                 |
| dress                        | 裙子                 |
| drum\_(musical\_instrument)  | 鼓\_（音乐乐器）          |
| duck                         | 鸭                  |
| duffel\_bag                  | 行李袋                |
| eagle                        | 鹰                  |
| earring                      | 耳环                 |
| egg                          | 蛋                  |
| elephant                     | 大象                 |
| fan                          | 扇子                 |
| faucet                       | 龙头                 |
| fireplace                    | 壁炉                 |
| fireplug                     | 火塞                 |
| fish                         | 鱼                  |
| flag                         | 旗帜                 |
| flower\_arrangement          | 插花                 |
| flowerpot                    | 花盆                 |
| football\_helmet             | 足球头盔               |
| fork                         | 叉                  |
| fountain                     | 喷泉                 |
| french\_fries                | 炸薯条                |
| frisbee                      | 飞盘                 |
| frog                         | 青蛙                 |
| fruit                        | 水果                 |
| fruit\_juice                 | 果汁                 |
| frying\_pan                  | 平底锅                |
| gazelle                      | 羚羊                 |
| giraffe                      | 长颈鹿                |
| glass\_(drink\_container)    | 玻璃\_（饮料容器）         |
| glove                        | 手套                 |
| goat                         | 山羊                 |
| goggles                      | 风镜                 |
| goose                        | 鹅                  |
| grape                        | 葡萄                 |
| guitar                       | 吉他                 |
| gun                          | 枪                  |
| hamburger                    | 汉堡包                |
| hamster                      | 仓鼠                 |
| handbag                      | 手提包                |
| handle                       | 处理                 |
| harbor\_seal                 | 港口密封               |
| hat                          | 帽子                 |
| headset                      | 耳机                 |
| helicopter                   | 直升机                |
| helmet                       | 头盔                 |
| high\_heels                  | 高跟鞋                |
| hog                          | 猪                  |
| horse                        | 马                  |
| house                        | 屋                  |
| icecream                     | 冰淇淋                |
| insect                       | 昆虫                 |
| jacket                       | 夹克                 |
| jaguar                       | 捷豹                 |
| jean                         | 牛仔布                |
| jellyfish                    | 海蜇                 |
| kitchen\_table               | 厨房的桌子              |
| kite                         | 风筝                 |
| knife                        | 刀                  |
| ladder                       | 梯子                 |
| lamp                         | 灯                  |
| lantern                      | 灯笼                 |
| laptop\_computer             | 笔记本电脑              |
| lavender                     | 薰衣草                |
| lemon                        | 柠檬                 |
| lettuce                      | 莴苣                 |
| license\_plate               | 车牌                 |
| life\_jacket                 | 救生衣                |
| lightbulb                    | 灯泡                 |
| lighthouse                   | 灯塔                 |
| lily                         | 百合                 |
| lion                         | 狮子                 |
| lizard                       | 蜥蜴                 |
| maple                        | 枫                  |
| mask                         | 面具                 |
| microphone                   | 麦克风                |
| microwave\_oven              | 微波炉                |
| minivan                      | 小型货车               |
| mirror                       | 镜子                 |
| monkey                       | 猴                  |
| motorcycle                   | 摩托车                |
| mouse\_(computer\_equipment) | 鼠标\_（计算机\_设备）      |
| muffin                       | 松饼                 |
| mug                          | 马克杯                |
| mushroom                     | 蘑菇                 |
| musical\_instrument          | 乐器                 |
| napkin                       | 餐巾                 |
| necklace                     | 项链                 |
| necktie                      | 领带                 |
| nightstand                   | 床头柜                |
| onion                        | 洋葱                 |
| orange\_(fruit)              | 橙子\_（水果）           |
| oven                         | 烤箱                 |
| owl                          | 猫头鹰                |
| paddle                       | 桨                  |
| painting                     | 绘画                 |
| palm\_tree                   | 棕榈树                |
| parachute                    | 降落伞                |
| parking\_meter               | 停车收费表              |
| parrot                       | 鹦鹉                 |
| pasta                        | 意大利面               |
| pastry                       | 糕点                 |
| pen                          | 笔                  |
| penguin                      | 企鹅                 |
| person                       | 人                  |
| piano                        | 钢琴                 |
| pillow                       | 枕头                 |
| pizza                        | 比萨                 |
| plastic\_bag                 | 塑料袋                |
| plate                        | 盘子                 |
| polar\_bear                  | 北极熊                |
| pool\_table                  | 池表                 |
| porch                        | 门廊                 |
| poster                       | 海报                 |
| potted\_plant                | 盆栽植物               |
| pumpkin                      | 南瓜                 |
| rabbit                       | 兔子                 |
| refrigerator                 | 冰箱                 |
| remote\_control              | 遥控                 |
| ring                         | 戒指                 |
| roller\_skate                | 溜冰鞋                |
| rose                         | 玫瑰                 |
| salad                        | 沙拉                 |
| sandal\_(type\_of\_shoe)     | 凉鞋\_（类型\_of\_shoe） |
| sandwich                     | 三明治                |
| saucer                       | 碟子                 |
| saxophone                    | 萨克斯管               |
| scarf                        | 围巾                 |
| scissors                     | 剪刀                 |
| sculpture                    | 雕塑                 |
| sheep                        | 羊                  |
| shirt                        | 衬衫                 |
| shoe                         | 鞋                  |
| short\_pants                 | 短裤                 |
| shrimp                       | 虾                  |
| sink                         | 下沉                 |
| skateboard                   | 滑板                 |
| ski                          | 滑雪                 |
| skirt                        | 短裙                 |
| skullcap                     | 黄芩                 |
| snake                        | 蛇                  |
| snowboard                    | 滑雪板                |
| soccer\_ball                 | 足球                 |
| sock                         | 短袜                 |
| sofa                         | 沙发                 |
| sofa\_bed                    | 沙发床                |
| sparrow                      | 麻雀                 |
| speaker\_(stero\_equipment)  | 扬声器\_（立体声设备）       |
| spectacles                   | 眼镜                 |
| spider                       | 蜘蛛                 |
| spoon                        | 勺子                 |
| sportswear                   | 运动服                |
| squirrel                     | 松鼠                 |
| stool                        | 凳子                 |
| stop\_sign                   | 停止标志               |
| stove                        | 火炉                 |
| straw\_(for\_drinking)       | 稻草\_（喝）            |
| strawberry                   | 草莓                 |
| street\_sign                 | 街道路标               |
| streetlight                  | 路灯                 |
| suit\_(clothing)             | 套装\_（服装）           |
| suitcase                     | 手提箱                |
| sunflower                    | 向日葵                |
| sunglasses                   | 太阳镜                |
| sunhat                       | 太阳帽                |
| surfboard                    | 冲浪板                |
| sushi                        | 寿司                 |
| swimming\_pool               | 游泳池                |
| swimsuit                     | 泳装                 |
| table                        | 桌子                 |
| tablet\_computer             | 平板电脑               |
| taxi                         | 出租车                |
| teddy\_bear                  | 玩具熊                |
| telephone                    | 电话                 |
| television\_set              | 电视机                |
| tennis\_ball                 | 网球                 |
| tennis\_racket               | 网球拍                |
| tent                         | 帐篷                 |
| tiger                        | 老虎                 |
| toilet                       | 洗手间                |
| toilet\_tissue               | 卫生纸                |
| tomato                       | 番茄                 |
| toothbrush                   | 牙刷                 |
| towel                        | 毛巾                 |
| tower                        | 塔                  |
| toy                          | 玩具                 |
| traffic\_light               | 红绿灯                |
| train\_(railroad\_vehicle)   | 火车\_（铁路\_车辆）       |
| trash\_can                   | 垃圾箱                |
| tray                         | 托盘                 |
| tree                         | 树                  |
| tripod                       | 三脚架                |
| trousers                     | 裤子                 |
| truck                        | 卡车                 |
| trumpet                      | 喇叭                 |
| turtle                       | 龟                  |
| umbrella                     | 伞                  |
| vase                         | 花瓶                 |
| vegetables                   | 蔬菜                 |
| violin                       | 小提琴                |
| wall\_socket                 | 墙上的插座              |
| watch                        | 手表                 |
| water\_jug                   | 水壶                 |
| whale                        | 鲸                  |
| wheel                        | 车轮                 |
| wheelchair                   | 轮椅                 |
| window                       | 窗户                 |
| wineglass                    | 红酒杯                |
| zebra                        | 斑马                 |