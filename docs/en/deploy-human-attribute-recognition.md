---
feature_id: HumanAttributeRecognition
feature_name: Human Attribute Recognition
feature_endpoint: custom_ocr
deployment_time: 15 Minutes
destroy_time: 10 Minutes
sample_image: Image URL address
feature_description: Recognize the attributes of the human body in the image, and return the human body position coordinates and attribute analysis in each area, such as the semantic information of 16 attributes such as gender, age, and clothing.

feature_scenario: Applicable to scenarios such as smart security, smart retail, and pedestrian search.
---

{%
  include "include-deploy-description.md"
%}

## List of attributes

| Name     | Semantic          |
| ------ | ------------ |
| Upper wear | Short sleeve, Long sleeve |
| Lower wear | Shorts/Skirts, Pants/Skirts |
| Upper wear texture | Pattern, Solid, Stripe/Check |
| Backpack | Without bag, With bag |
| Whether to wear glasses | No, Yes |
| Whether to wear a hat | No, Yes |
| Body orientation | Front, Back, Left, Right |
| Truncate above | No, Yes |
| Truncate below | No, Yes |
| Occlusion | None, Light, Heavy |
| Whether to wear a mask | No, Yes |
| Gender | Male, Female |
| Age | Children, teenager, middle-aged, elderly |
| Smoking | No, Yes |
| Telephone | No, Yes |
| Whether to carry things | No, Yes |

## REST API Reference

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| url | *String* |Choose url or img.|Image URL address, which supports HTTP/HTTPS and S3 protocols. Supported image formats are jpg/jpeg/png/bmp, with the longest side not exceeding 4096px.|
| img | *String* |Choose url or img.|Base64 encoded image data.|

- Example JSON request

``` json
{
  "url": "{{page.meta.sample_image}}"
}
```

``` json
{
  "img": "Base64-encoded image data"
}
```

- Response parameters

| **Name** | **Type** | **Description**  |
|----------|-----------|------------|
|Labels |*List* |List of human bodies recognized in the image.|
|+upper_wear |*Dict* |Short Sleeve, Long Sleeve|
|+upper_wear_texture |*Dict* |Pattern, Solid, Stripe/Check|
|+lower_wear |*Dict* |Shorts/Skirts, Pants/Skirts|
|+glasses |*Dict* |With glasses, without glasses|
|+bag |*Dict* |With backpack, without backpack|
|+headwear |*Dict* |With hat, without hat|
|+orientation |*Dict* |left side, back side, front side, right side|
|+upper_cut |*Dict* |with truncation, without truncation|
|+lower_cut |*Dict* |with truncation, without truncation|
|+occlusion |*Dict* |No Occlusion, Light Occlusion, Heavy Occlusion|
|+face_mask |*Dict* |With mask, without mask|
|+gender |*Dict* |Male, Female|
|+age |*Dict* |Children, Teens, Middle-aged, Seniors|
|+smoke |*Dict* |Smoking, non-smoking|
|+cellphone |*Dict* |with telephone, without telephone|
|+carrying_item |*Dict* |With or without carry|
|+BoundingBox |*Dict* |Coordinate values of the human body in the image, including the percentage of top, left, width, height relative to the full screen|
|LabelModelVersion |*String* |Current model version number|

- Example JSON response

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
  include "include-deploy-cost.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}