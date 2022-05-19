---
feature_id: ObjectRecognition
feature_name: 通用物体识别
feature_endpoint: object_recognition
deployment_time: 15 分钟
destroy_time: 10 分钟
sample_image: 图像的URL地址
feature_description: 检测图像中的通用对象主体，返回该对象主体的区域信息与置信度。支持识别300类物体。
feature_scenario: 可应用于IPC图像检测、交通、安防等行业中图像场景的目标检测与跟踪。
---

{%
  include "include-deploy-description.md"
%}

## API参数说明

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| url | *String* |与 img 参数二选一|图像的 URL 地址。支持 HTTP/HTTPS 和 S3 协议。要求图像格式为 jpg/jpeg/png/bmp ，最长边不超过 4096px。|
| img | *String* |与 url 参数二选一|进行 Base64 编码的图像数据|

- 请求 Body 示例

``` json
{
"url": "{{page.meta.sample_image}}"
}
```

``` json
{
"img": "Base64编码的图像数据"
}
```

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|Labels    |*List*   |图像中找到的目标列表|
|+Name    |*String*   |目标类别名|
|+Instances    |*List*   |类别实例列表|
|++BoundingBox |*JSON*     |实例在图像中的的坐标值，包含top，left，width，height相对全画面的百分比|
|++Confidence    |*Float*   |实例的置信度，0-100|
|+Confidence    |*Int*   |当前类别实例置信度的最大值|
|LabelModelVersion    |*String*   |当前模型版本号|

- 返回示例
``` json
{
    "Labels": [
        {
            "Name": "car_(automobile)", 
            "Confidence": 67.87780523300171, 
            "Instances": [
                {
                    "BoundingBox": {
                        "Width": 1.0013043403596384, 
                        "Height": 0.9958885181613408, 
                        "Left": -0.00021715163893532008, 
                        "Top": 0.00033918747441136817
                    }, 
                    "Confidence": 67.87780523300171
                }
            ]
        }, 
        {
            "Name": "mirror", 
            "Confidence": 59.2678964138031, 
            "Instances": [
                {
                    "BoundingBox": {
                        "Width": 0.14041614532470703, 
                        "Height": 0.29166373257057565, 
                        "Left": 0.2743588984012604, 
                        "Top": 0.2794425819140053
                    }, 
                    "Confidence": 59.2678964138031
                }
            ]
        }, 
        {
            "Name": "window", 
            "Confidence": 16.396354138851166, 
            "Instances": [
                {
                    "BoundingBox": {
                        "Width": 0.44319993257522583, 
                        "Height": 0.6673663154702585, 
                        "Left": 0.5509995222091675, 
                        "Top": 0.015529238811174562
                    }, 
                    "Confidence": 16.396354138851166
                }
            ]
        }
    ], 
    "LabelModelVersion": "1.2.0"
}
```

{%
  include-markdown "include-deploy-code.md"
%}

## 支持的目标识别实体列表

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
| mouse\_(computer\_equipment) | 鼠标\_（计算机设备）      |
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
| sandal\_(type\_of\_shoe)     | 凉鞋                 |
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
| speaker\_(stero\_equipment)  | 扬声器\_（音响设备）   |
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

{%
  include "include-deploy-cost.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}
