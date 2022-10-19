---
feature_id: CustomOCR
feature_name: Custom OCR
feature_endpoint: custom_ocr
deployment_time: 18 Minutes
destroy_time: 20 Minutes
sample_image: Image URL address
feature_description: You can customize the OCR template, extract the structured text information in cards and tickets, and display the results in the key-value format.
feature_scenario: Applicable to structured recognition of cards and tickets, such as logistics documents, invoices, business licenses, itineraries, and train tickets.
---

{%
  include "include-deploy-description.md"
%}

## API reference

### Add templates

Before text recognition, you need to create a template through the **Add Template API**. In order to improve the accuracy of text recognition, the image for template creation should have similar details to the recognized image and clear text content. The same template can contain multiple recognition areas.

To create a template, each area to be recognized needs to specify the four coordinate points of the rectangular frame and the name of the area. You can use common image processing software to assist in obtaining coordinate points, or use this solution tool to create templates.

The following is a description of this solution tool:

1. Click tool [link](../tools/custom-template/index.htm)。
2. Click **Local file**。
3. Move the mouse over the picture to identify the content, click the upper left corner, slide the mouse to the lower right corner, release the mouse, and enter the identification name in the pop-up dialog box.
4. If there are multiple items to be identified, repeat step 3.
5. Click**Copy to clipboard**.This content is the request body.Refer to the Add Template API Request Body example to create a custom template and record the template ID after successful creation.
6. After creating the template, perform a text recognition test with the original image and template ID to ensure that the template can accurately recognize the required information.
7. (Optional) If you found that the extracted information is incomplete, confirm that the coordinate points are marked correctly and recreate the template by expanding the recognition area appropriately. 

!!! Important "Important"
    The rectangular box area must completely cover the text content to be recognized. Leave enough space for error tolerance on all sides of the recognition area without covering other recognition rectangular areas for accurate recognition.

The following describe the API reference:

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| url | *String* |Choose url or img.|Image URL address, which supports HTTP/HTTPS and S3 protocols. Supported image formats are jpg/jpeg/png/bmp, with the longest side not exceeding 4096px.|
| img | *String* |Choose url or img.|Base64-encoded image data.|
| type | *String* | Fixed value is `add`.|
| template | *List* |Each element corresponds to the coordinates of an area to be extracted and its name.|

- Example JSON request

``` json
{
    "type": "add", 
    "url": "Image URL address", 
    "template": [
        [
            [[421, 465], [909, 471], [911, 503], [419, 495]], "名称"
        ], 
        [
            [[419, 495], [911, 503], [909, 533], [415, 527]], "识别号"
        ], 
        [
            [[345, 339], [595, 343], [583, 397], [341, 385]], "发票号"
        ]
    ]
}
```

``` json
{
  "type": "add", 
  "img": "Base64-encoded image data",
  "template": [
        [
            [[421, 465], [909, 471], [911, 503], [419, 495]], "名称"
        ], 
        [
            [[419, 495], [911, 503], [909, 533], [415, 527]], "识别号"
        ], 
        [
            [[345, 339], [595, 343], [583, 397], [341, 385]], "发票号"
        ]
    ]
}
```

- Response parameters

| **Name** | **Type** | **Description**  |
|----------|-----------|------------|
|template_id    |*String*   |Template ID|

- Example JSON response

``` json
{
    "template_id": "模板的ID",
}
```

### Content recognition

After the template is created, you can use the corresponding template ID to perform text recognition on the image, and the returned value is the name and text content of the recognized area in the template.

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| url | *String* |Choose url or img.|Image URL address, which supports HTTP/HTTPS and S3 protocols. Supported image formats are jpg/jpeg/png/bmp, with the longest side not exceeding 4096px.|
| img | *String* |Choose url or img.|Base64 encoded image data.|
| type | *String* |Fixed value is `query`.|
| template_id | *String* |Existing template ID.|

- Example JSON request

``` json
{
  "template_id": "已存在的模板ID", 
  "url": "Image URL address"
}
```

- Response parameters

| **Name** | **Type** | **Description**  |
|----------|-----------|------------|
|key    |*String*   |Field name.|
|value    |*String*   |Extracted value.|
|score    |*Float*   |Confidence score.|

- Example JSON response

``` json
[
    {
        "key": "名称", 
        "value": "亚马逊通技术服务(北京)有限公司", 
        "score": 97.98
    }, 
    {
        "key": "识别号", 
        "value": "91110116592334142D", 
        "score": 99.62
    }, 
    {
        "key": "发票号", 
        "value": "4403212222", 
        "score": 96.58
    }
]
```

### Remove templates

If you need to delete a template, you can delete it by specifying the template ID to be deleted. Note that a template cannot be recovered after it has been deleted.

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Required** |  **Description**  |
|----------|-----------|------------|------------|
| template_id | *List* |Existing template ID.|
| type | *String* |Fixed value is `del`.|

- Example JSON request

``` json
{
    "type": "del", 
    "template_id": "已存在模板ID"
}
```

- Response parameters

| **Name** | **Type** | **Description**  |
|----------|-----------|------------|
|template_id    |*String*   |Removed template ID.|

- Example JSON response

``` json
{
    "template_id": "已删除模板的ID",
}
```

### List all templates

The created templates can be listed by ID.

- HTTP request method: `POST`

- Request body parameters

| **Name**  | **Type**  | **Description** |
|----------|-----------|------------|
| type | *String* |Fixed value is `list`.|

- Example JSON request

``` json
{
    "type": "list", 
}
```

- Response parameters

| **Name** | **Type** | **Description**  |
|----------|-----------|------------|
|template_id_list    |*List*   |List of existing templates.|

- Example JSON response

``` json
{
    "template_id_list": ["已存在模板的列表"],
}
```


{%
  include-markdown "include-deploy-code.md"
%}

{%
  include "include-deploy-cost-8GB.md"
%}

{%
  include-markdown "include-deploy-uninstall.md"
%}