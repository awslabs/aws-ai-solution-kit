# Inappropriate Image Detection

## Description

Based on AI/ML image recognition technology, automatically audits pictures, identifies and obtains multidimensional pornographic quantitative information (normal, sexy, porn).

## Deployment

```
# Require to install AWS CDK
$ cdk deploy AIKits-Porn-Image-Detection-Stack
```

### Parameters

This solution uses the following default values, you can modify them as necessary.

|  Parameter   |  Default |  Description |
|  ----------  | ---------| -----------  |
| **customStageName**  | prod | The name of the stage, which API Gateway uses as the first path segment in the invoked Uniform Resource Identifier (URI).|
| **customAuthType**    | AWS_IAM    | Authorization for API Gateway. Valid Values are *AWS_IAM* and *NONE*. |

### Outputs

|  Name   |  Description |
|  -------|  ----------- |
| **aikits InvokeURL**  | REST API invoke URL. |
| **aikits InvokeURLArn** | REST API ARN. |

## Get Started

### Invoking URL

You can see the URL of the record prefixed with **aikitsInvokeURL** in the Outputs tab of Amazon CloudFormation.

### REST API Reference

- HTTP Method: `POST`

- Body Parameters

| **Name**  | **Type**  | **Optional** |  **Description**  |
|----------|-----------|------------|------------|
|url&nbsp;&nbsp;&nbsp;&nbsp;       |*String*     |Use *img* or *url* | URL address of the image. Supports HTTP/HTTPS and S3 protocols. Required image format jpg / jpeg / png / bmp, not exceeding the longest side 4096px.|
|img       |*String*     |Use *img* or *url*|Base64-encoded image data|

- Sample Request Body 

``` json
{
  "url": "https://aikits.demo.solutions.aws.a2z.org.cn/img/detect-2.jpg"
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
|normal    |*Float*   |Identify the image’s normal dimensions|
|sexy      |*Float*   |Identify the image’s sexy dimension|
|porn      |*Float*   |Identify the image’s pornographic dimension|

- Sample Response
``` json
{ 
   “normal”  : 0.15993066132068634,
   “sexy”    : 0.5451669692993164, 
   “porn”    : 0.2949024438858032 
}
```

###  Sample Request Code

**cURL**
``` bash
curl --location --request POST 'https://xxxxxxxxxxx.execute-api.xxxxxxxxx.amazonaws.com/prod/porn' \
--header 'Content-Type: application/json' \
--data-raw '{
  "url":"https://aikits.demo.solutions.aws.a2z.org.cn/img/detect-2.jpg"
}'
```

**Python (requests)**
``` python
import requests
import json

url = "https://xxxxxxxxxxx.execute-api.xxxxxxxxx.amazonaws.com/prod/porn"

payload = json.dumps({
  "url": "https://aikits.demo.solutions.aws.a2z.org.cn/img/detect-2.jpg"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)

```

**Java (OkHttp)**
``` java
OkHttpClient client = new OkHttpClient().newBuilder()
  .build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\n  \"url\":\"https://aikits.demo.solutions.aws.a2z.org.cn/img/detect-2.jpg\"\n}");
Request request = new Request.Builder()
  .url("https://xxxxxxxxxxx.execute-api.xxxxxxxxx.amazonaws.com/prod/porn")
  .method("POST", body)
  .addHeader("Content-Type", "application/json")
  .build();
Response response = client.newCall(request).execute();
```

**PHP (curl)**
``` php
<?php

$curl = curl_init();

curl_setopt_array($curl, array(
  CURLOPT_URL => 'https://xxxxxxxxxxx.execute-api.xxxxxxxxx.amazonaws.com/prod/porn',
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_ENCODING => '',
  CURLOPT_MAXREDIRS => 10,
  CURLOPT_TIMEOUT => 0,
  CURLOPT_FOLLOWLOCATION => true,
  CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
  CURLOPT_CUSTOMREQUEST => 'POST',
  CURLOPT_POSTFIELDS =>'{
  "url":"https://aikits.demo.solutions.aws.a2z.org.cn/img/detect-2.jpg"
}',
  CURLOPT_HTTPHEADER => array(
    'Content-Type: application/json'
  ),
));

$response = curl_exec($curl);

curl_close($curl);
echo $response;
```

## License

This project is licensed under the Apache-2.0 License.