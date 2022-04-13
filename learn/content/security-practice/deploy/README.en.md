---
title: Deploy WAF & Shield Automations
weight: 5
---

## Deploy WAF & Shield Automations
Please follow this previous step to [Upload CloudFront Extensions code into CloudShell](https://awslabs.github.io/aws-cloudfront-extensions/develop/download-code/readme/) if have not unzipped the CloudFront Extensions repository in the CloudShell.

After unzipping the aws-cloudfront-extensions archive, you can deploy the WAF & Shield Automations in the CloudShell by the next commands:


1. Create a symbolic link to [PIP](https://pypi.org/project/pip/) from PIP3

       sudo ln -s /usr/bin/pip3 /usr/bin/pip

2. Change the current directory to 'aws-cloudfront-waf/deployment'

       cd aws-cloudfront-extensions-main/templates/aws-cloudfront-waf/deployment/
3. Package all required AWS Lambda functions

        ./build-s3-dist.sh

4. Navigate to the aws-cloudfront-waf directory and deploy the WAF & Shield Automations app by AWS CDK
        
        cd ..
        cdk deploy

This CDK app uses the following default values, you can modify them by --parameters flags at deployment.
|Parameter|Default |Description|
|---------|--------|-----------|
|appAccessLogBucket|access-log-bucket-cloudfront|The name for the Amazon S3 bucket where you want to store Cloud Front access logs for your CloudFront distribution.|
|wafLogBucketName  |waf-log-bucket-cloudfront   |The name for the Amazon S3 bucket where you want to store WAF access Cloud Front logs.|
|errorThreshold    |50                          |The maximum acceptable bad requests per minute per IP.|
|requestThreshold  |100                         |The maximum acceptable requests per FIVE-minute period per IP address.|
|blockPeriod       |240                         |The period (in minutes) to block applicable IP addresses.|
|waf2Scope         |CLOUDFRONT                  |Specifies whether this is for an AWS CloudFront distribution or for a regional application. A regional application can be an Application Load Balancer (ALB), an Amazon API Gateway REST API, or an AWS AppSync GraphQL API. Valid Values are CLOUDFRONT and REGIONAL. For CLOUDFRONT, you must create your WAFv2 resources in the US East (N. Virginia) Region, us-east-1.|

Enter **y** to deploy the stack and create the resources.

The output should look like the following:

    ✅  AwsCloudfrontWafStack

    Outputs:
    AwsCloudfrontWafStack.ApiGatewayBadBotEndpointDEAB6B1B = https://************us-east-1amazonawcom/prod/
    AwsCloudfrontWafStack.AppAccessLogBucketName = ************
    AwsCloudfrontWafStack.WAFWebACLArn arn:aws:wafv2:us-east-1:************:globalwebaclCloudFront-Web-WAF/************
    AwsCloudfrontWafStack.WAFWebACLName = ************
    AwsCloudfrontWafStack.WafLogBucketName = ************
    Stack ARN:
    arn:aws:cloudformation:us-east-1:************:stack/AwsCloudfrontWafStack/************

In the CloudFormation Console, you will see the CDK apps are deployed through AWS CloudFormation.
   ![CloudFormation Console](/images/cdk_cloudformation_completed.png)

## Configure Web Access Logging
Configure Juice Shop web application’s distribution in Amazon CloudFront to send web access logs to the appAccessLogBucket in Amazon S3 bucket so that this data is available for the Log Parser AWS Lambda function.

1)	Open the Amazon CloudFront console
2)	Select your Juice Shop web application's distribution, and choose Distribution Settings. 
3)	On the General tab, choose Edit. 
4)	For AWS WAF Web ACL, choose the web ACL just created (you can find the `WAFWebACLName` in the CloudShell output).
5)	For Logging, choose On. 
6)	For Bucket for Logs, choose the `appAccessLogBucket` bucket to store web access logs. 
7)	Set the log prefix as AWSLogs/. 
8)	Click 'Yes, Edit' to save changes. 
![Config Logging](/images/config_waf_log.png?width=50pc)

## AWS Shield Deployment
In the AWS Lambda console, update the `ShieldAdvancedLambda` function with the ARN of the Juice Shop CloudFront distribution.

1) Open the Amazon CloudFront console
2) Select your Juice Shop web application's distribution and copy the ARN in the General tab
![Juice Shop ARN](/images/juice_shop_arn.png?width=50pc)
3) Open the Amazon Lambda console, on the Functions list, open the `ShieldAdvancedLambda` Lambda function, click the Lambda item in the Designer and open the shield-protection.py source code in the 'Function code', replace the `CloudFrontARN` variable in line 31 with the copied ARN.
![Replace ARN](/images/replace_arn.png?width=50pc)
4) Click the Deploy button until you see the 'Changes deployed' notice, then click the Test button to launch the function with the default testing event, after testing, you will see the success execution result in the summary.

So far, the deployment of AWF WAF and Shield has been finished and associated with the Juice Shop CloudFront distribution. Let's start testing in the [next step](/security/rule-testing/readme/).