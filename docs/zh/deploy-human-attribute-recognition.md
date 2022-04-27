---
feature_id: HumanAttributeRecognition
feature_name: 自定义模板文字识别
feature_endpoint: custom_ocr
deployment_time: 15 分钟
destroy_time: 10 分钟
sample_image: https://demo.solutions.aws.a2z.org.cn/image/sample.png
feature_description: 识别输入图片中的人体区域，并返回每个区域人体位置坐标及属性分析，如性别、年龄、服饰等16种属性的语义信息。

feature_scenario: 可应用于智慧安防、智慧零售、行人搜索等场景。
---

{%
  include "include-deploy-description.md"
%}

## 属性说明

| 名称     | 语义值          |
| ------ | ------------ |
| 上身服饰   | 短袖、长袖        |
| 下身服饰   | 短裤/裙、长裤/裙    |
| 上身服饰纹理 | 图案、纯色、格子/条纹  |
| 背包     | 无包、有包        |
| 是否戴眼镜  | 无、有          |
| 是否戴帽子  | 无、有          |
| 人体朝向   | 正面、背面、左面、右面  |
| 上方截断   | 无、有          |
| 下方截断   | 无、有          |
| 遮挡情况   | 无、轻、重        |
| 是否戴口罩  | 无、有          |
| 性别     | 男、女          |
| 年龄     | 幼儿、青少年、中年、老年 |
| 吸烟     | 无、有          |
| 电话     | 无、有          |
| 拿东西    | 无、有          |

{%
  include "include-deploy-lambda.md"
%}

{%
  include "include-deploy-cost.md"
%}

{%
  include "include-deploy.md"
%}

## 开始使用

{%
  include "include-call-url.md"
%}

### REST API接口参考

- HTTP 方法: `POST`

- Body 请求参数

| **名称**  | **类型**  | **是否必选** |  **说明**  |
|----------|-----------|------------|------------|
| url | *String* |与 img 参数二选一，优先级高于 img|图像的 URL 地址。支持 HTTP/HTTPS 和 S3 协议。要求图像格式为 jpg/jpeg/png/bmp ，最长边不超过 4096px。|
| img | *String* |与 url 参数二选一|进行 base64 编码的图像数据|

- 请求 Body 示例

``` json
{
  "url": "{{page.meta.sample_image}}"
}
```

``` json
{
  "img": "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/……"
}
```

- 返回参数

| **名称**  | **类型**  |  **说明**  |
|----------|-----------|------------|
|Labels    |*List*   |图像中找到的人体列表|
|+upper_wear    |*Dict*   |短袖、长袖|
|+upper_wear_texture    |*Dict*   |图案、纯色、条纹/格子|
|+lower_wear    |*Dict*   |短裤/裙、长裤/裙|
|+glasses    |*Dict*   |有眼镜、无眼镜|
|+bag    |*Dict*   |有背包、无背包|
|+headwear    |*Dict*   |有帽、无帽|
|+orientation    |*Dict*   |左侧面、背面、正面、右侧面|
|+upper_cut    |*Dict*   |有截断、无截断|
|+lower_cut    |*Dict*   |有截断、无截断|
|+occlusion    |*Dict*   |无遮挡、轻度遮挡、重度遮挡|
|+face_mask    |*Dict*   |戴口罩、无口罩|
|+gender    |*Dict*   |男性、女性|
|+age    |*Dict*   |幼儿、青少年、中年、老年|
|+smoke    |*Dict*   |吸烟、未吸烟|
|+cellphone    |*Dict*   |使用手机、未使用手机|
|+carrying_item    |*Dict*   |有手提物、无手提物|
|+BoundingBox |*Dict*     |人体在图像中的的坐标值，包含top，left，width，height相对全画面的百分比|
|LabelModelVersion    |*String*   |当前模型版本号|

- 返回示例

``` json
{
    "Labels": [
        {
            "upper_wear": {
                "短袖": 0.01, 
                "长袖": 99.99
            }, 
            "upper_wear_texture": {
                "图案": 0, 
                "纯色": 99.55, 
                "条纹/格子": 0.45
            }, 
            "lower_wear": {
                "短裤/裙": 0.15, 
                "长裤/裙": 99.85
            }, 
            "glasses": {
                "有眼镜": 57.74, 
                "无眼镜": 42.26
            }, 
            "bag": {
                "有背包": 0.69, 
                "无背包": 99.31
            }, 
            "headwear": {
                "有帽": 97.02, 
                "无帽": 2.98
            }, 
            "orientation": {
                "左侧面": 99.99, 
                "背面": 0, 
                "正面": 0, 
                "右侧面": 0.01
            }, 
            "upper_cut": {
                "有截断": 0, 
                "无截断": 100
            }, 
            "lower_cut": {
                "无截断": 0.18, 
                "有截断": 99.82
            }, 
            "occlusion": {
                "无遮挡": 100, 
                "重度遮挡": 0, 
                "轻度遮挡": 0
            }, 
            "face_mask": {
                "无口罩": 100, 
                "戴口罩": 0
            }, 
            "gender": {
                "男性": 100, 
                "女性": 0
            }, 
            "age": {
                "幼儿": 0, 
                "青少年": 100, 
                "中年": 0, 
                "老年": 0
            }, 
            "smoke": {
                "吸烟": 0, 
                "未吸烟": 100
            }, 
            "cellphone": {
                "使用手机": 0, 
                "未使用手机": 100
            }, 
            "carrying_item": {
                "有手提物": 0.03, 
                "无手提物": 99.97
            }, 
            "BoundingBox": {
                "Width": 0.11781848725818456, 
                "Height": 0.43450208474661556, 
                "Left": 0.5310931977771577, 
                "Top": 0.45263674786982644
            }
        }, 
        ...
    ], 
    "LabelModelVersion": "1.2.0"
}
```

{%
  include-markdown "include-deploy-code.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}