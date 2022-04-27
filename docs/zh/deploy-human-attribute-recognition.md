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
|words    |*String*   |识别文本字符串内容|
|location |*JSON*     |识别文本在图像中的的坐标值，包含 top，left，width，height的整数值|
|score    |*Float*   |识别文本的置信度值，为0到1区间内 Float 型数值|

- 返回示例

``` json
[
    {
        "words": "香港永久性居民身份證",
        "location": {
            "top": 18,
            "left": 148,
            "width": 169,
            "height": 17
        },
        "score": 0.9923796653747559
    },
    {
        "words": "HONG KONG PERMANENTIDENTITYCARD",
        "location": {
            "top": 36,
            "left": 71,
            "width": 321,
            "height": 17
        },
        "score": 0.9825196266174316
    }

]
```

{%
  include-markdown "include-deploy-code.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}