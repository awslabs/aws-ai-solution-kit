# OCR for CN Business License

## Deployment

### Parameters

This solution uses the following default values, you can modify them as necessary.

|  Parameter   |  Default |  Description |
|  ----------  | ---------| -----------  |
| **customStageName**  | prod | The name of the stage, which API Gateway uses as the first path segment in the invoked Uniform Resource Identifier (URI).|
| **customAuthType**    | AWS_IAM    | Authorization for API Gateway. Valid Values are *AWS_IAM* and *NONE*. |

```
npm install
```

Set AWS_IAM as the authorization for API Gateway
```
npx cdk deploy AIKits-OCR-CN-Business-License-Stack
```

Set NONE as the authorization for API Gateway
```
npx cdk deploy AIKits-OCR-CN-Business-License-Stack --parameters customAuthType=NONE
```

### Outputs

|  Name   |  Description |
|  -------|  ----------- |
| **InvokeURL**  | REST API invoke URL. |
| **InvokeURLArn** | REST API ARN. |

## Get Started

###  Lambda function Environment variables
After the deployment, the variable for OCR can be adjusted by Lambda function variables

| **Name**  | **Type**  |  **Description**  |
|----------|-----------|------------|
|**LICENSE_ID**    |*bool*   |Whether including License ID in response JSON, default: true |
|**COMPANY_NAME**    |*bool*   |Whether including company name in response JSON, default: true |
|**DURATION**    |*bool*   |Whether including duration seconds in response JSON, default: true |
|**MODEL_NAME**    |*String*   |OCR model name, default: standard_cn_business_license |
|**MODEL_PATH**    |*String*   |OCR model path, default: /opt/program/model/ |
|**REFERECNE_SCORE**    |*float*   |Reference score for accurate detection, default: 0.90|
|**AUTO_ROTATION**    |*bool*   |Auto retation for input image, default: true |
|**ENHANCE_MODE**    |*bool*   |Enhance the detail for input image, default: true |

### Invoking URL

You can see the URL of the record prefixed with **aikitsInvokeURL** in the Outputs tab of Amazon CloudFormation.

### REST API Reference

- HTTP Method: `POST`

- Body Parameters

| **Name**  | **Type**  | **Optional** |  **Description**  |
|----------|-----------|------------|------------|
|url&nbsp;&nbsp;&nbsp;&nbsp;       |*String*     |Use *img* or *url* | URL address of the image. Supports HTTP/HTTPS and S3 protocols. Required image format jpg / jpeg / png / bmp, not exceeding the longest side 4096px.|
|img       |*String*     |Use *img* or *url*|Base64-encoded image data|

![Sample Image](doc/ocr-sample-cn-license.jpg)

- Sample Request Body 

``` json
{
  "url": "https://aikits.demo.solutions.aws.a2z.org.cn/img/sample-cn-business-license.jpg"
}
```

``` json
{
  "img": "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/……"
}
```

- Response Prarameters

| **Name**  | **Type**  |  **Description**  |
|----------|-----------|------------|
|license_id    |*String*   |License ID in CN Business License |
|company_name |*String*     |Company Name in CN Business License|
|duration    |*Float*   |The confidence of the recognized text|

- Sample Response
``` json
{
    "license_id": "91xxxxxxxxxx",
    "company_name": "xx有限公司",
    "duration": "1.086"
}
```

###  Sample Request Code

**cURL**
``` bash
curl --location --request POST 'https://xxxxxxxxxxx.execute-api.xxxxxxxxx.amazonaws.com/prod/business-license' \
--header 'Content-Type: application/json' \
--data-raw '{
  "url":"https://aikits.demo.solutions.aws.a2z.org.cn/img/sample-cn-business-license.jpg"
}'
```

**Python (requests)**
``` python
import requests
import json

url = "https://xxxxxxxxxxx.execute-api.xxxxxxxxx.amazonaws.com/prod/business-license"

payload = json.dumps({
  "url": "https://aikits.demo.solutions.aws.a2z.org.cn/img/sample-cn-business-license.jpg"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)

```

## License

This project is licensed under the Apache-2.0 License.