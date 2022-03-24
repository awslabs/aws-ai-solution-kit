# OCR for Shipped From

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
npx cdk deploy AIKits-OCR-Shipped-From-Stack
```

Set NONE as the authorization for API Gateway
```
npx cdk deploy AIKits-OCR-Shipped-From-Stack --parameters customAuthType=NONE
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
|**MODEL_NAME**    |*String*   |OCR model name |
|**MODEL_PATH**    |*String*   |OCR model path, default: /opt/program/model/ |

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
  "url": "https://aikits.demo.solutions.aws.a2z.org.cn/img/samplejpg",
  "table": [
    {
        "crop": [
            2000,
            100,
            1400,
            1400
        ],
        "names": [
            "Carrier",
            "Invoice Number"
        ]
    }
  ]
}
```

``` json
{
  "img": "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/……"
  "table": [
    {
        "crop": [
            2000,
            100,
            1400,
            1400
        ],
        "names": [
            "Carrier",
            "Invoice Number"
        ]
    }
  ]
}
```

## License

This project is licensed under the Apache-2.0 License.