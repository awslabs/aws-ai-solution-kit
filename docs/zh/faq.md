# 常见问题

### 部署解决方案都需要哪些AWS Identity and Access Management (IAM)权限？

部署解决方案并在部署后通过API Gateway调用 API 需要如下权限，其中**sagemaker:**仅限于**图像超分辨率** API：

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

### 部署解决方案时遇到 *The account-level service limit 'ml.g4dn.xlarge for endpoint usage' is 0 Instances* 如何解决？

1. visit aws console https://console.aws.amazon.com/
2. click on support on the top right corner
3. click create a case (orange button)
4. select Service Limit Increase radio button
5. For Limit Type, Search and Select SageMaker Notebook Instances
6. Write a short Use case description
7. For Limit, Select ml.[x].[x] (in your case, ml.g4dn.xlarge)

### 部署解决方案时遇到 *Resource handler returned message: "'MemorySize' value failed to satisfy constraint: Member must have value less than or equal to 3008*如何解决？

//TODO

### 如何统一切换 Amazon API Gateway 中 API 的访问认证方式？

借助 Amazon CloudFormation，您可以更改堆栈中现有资源的属性，如果您需要添加或删除已经部署的 AI 功能，可以通过更新堆栈的方式完成。

1. 在 Amazon CloudFormation 控制台上，选择堆栈列表中创建完成的 AI Solution Kit 堆栈。

2. 在堆栈详细信息窗格中，选择 Update (更新)。

3. 在模板参数部分，修改**API Gateway Authorization**参数，然后选择 Next (下一步)。

4. 在**配置堆栈选项**页面，选择**下一步**。

5. 在**审核**页面，查看并确认设置。确保选中确认模板将创建Amazon Identity and Access Management（IAM）资源的复选框。选择**下一步**。

6. 如果您对所做更改表示满意，请选择 Updata stack (更新堆栈)即可完成访问权限更新。

### 如何单独切换 Amazon API Gateway 中 API 的访问认证方式？
1. 打开Amazon Web Service控制台（console）的服务面板，在里面找到 应用程序服务（Application Services），点击API Gateway
2. 在 API 列表中选择最新创建的AI Solution Kit API，也可按 ‘已创建’ 的时间排序，便于查找，然后点击名称链接打开 API详细页
3. 展开资源树，找到需要修改访问权限的资源路径下的 ‘OPTIONS’节点，点击该节点显示方法执行配置页面。点击方法执行下方的方法请求链接
4. 然后点击 授权 右侧的编辑按钮后，展开下拉列表，选择 ‘Amazon IAM’，选好之后点击 更新 按钮完成修改
5. 更新后，授权项应显示为 ‘Amazon IAM’
6. 接下来点击资源树中OPTIONS下方 POST按钮，和修改OPTIONS的方法一样，在方法请求中将授权方式修改为 Amazon IAM，然后点击更新按钮
7. 点击方法执行左侧的 ‘操作’ 下拉按钮，点击 API操作下方 ‘部署 API’ 选项
8. 在部署 API 对话框选择 ‘prod’或自定义名称的 部署阶段，请不要选择 [新阶段]，然后点击下方部署按钮完成部署

### 创建和使用带 API 密钥的使用计划
本解决方案支持 API 使用计划（Usage Plans）。部署本解决方案并测试 API 后，您可以实施 API Gateway 使用计划，将它们作为面向客户的产品/服务提供。您可以配置使用计划和 API 密钥，以允许客户按照商定的可满足其业务需求和预算限制的请求速率和配额来访问选定 API。如果需要，您可以为 API 设置默认方法级别限制或为单个 API 方法设置限制。 API 调用方必须在 API 请求的 x-api-key 标头中提供一个已分配的 API 密钥。 

如您需要配置 *API 使用计划* 请参考：[配置使用计划](https://docs.aws.amazon.com/zh_cn/apigateway/latest/developerguide/api-gateway-create-usage-plans.html)

### 通用目标检测 API 目前支持哪些目标识别？
如下为目标检测支持实体列表：

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