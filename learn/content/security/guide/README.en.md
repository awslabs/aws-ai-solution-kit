---
title: Deployment
weight: 2
---

* [Source code](https://github.com/awslabs/aws-cloudfront-extensions/tree/main/templates/aws-cloudfront-waf)
* [CloudFormation template](https://aws-gcr-solutions.s3.amazonaws.com/aws-cloudfront-extensions/latest/AwsCloudfrontWafStack.template)

Estimated deployment time: 10 min

### Deploy by CloudFormation 
1. The template launches in the US East (N. Virginia) Region by default. You can deploy the WAF&Shield Automcation Solution with existing AWS CloudFormation templates.[![Deploy WAF&Shield](/images/deploy_to_aws.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=WAFWorkshopSampleWebApp&templateURL=https://aws-gcr-solutions.s3.amazonaws.com/aws-cloudfront-extensions/latest/AwsCloudfrontWafStack.template)

2. Under Parameters, review the parameters for the template, and modify them as necessary. To opt out of a particular feature, choose none or no as applicable. 
![Architecture](/images/waf_params.png)
{{% notice note %}}
Specifies whether this is for an AWS CloudFront distribution or for a regional application. A regional application can be an Application Load Balancer (ALB), an Amazon API Gateway REST API, or an AWS AppSync GraphQL API. Valid Values are CLOUDFRONT and REGIONAL. For CLOUDFRONT, you must create your WAFv2 resources in the US East (N. Virginia) Region, us-east-1.
{{% /notice%}}

3. Choose **Next**. 
4. On the **Configure stack options** page, you can specify tags (key-value pairs) for resources in your stack and set additional options, and then choose **Next**. 
5. On the **Review** page, review and confirm the settings. Check the boxes acknowledging that the template will create AWS Identity and Access Management (IAM) resources and any additional capabilities required. 
6. Choose **Create** to deploy the stack. 
7. To see details for the stack resources, choose the **Outputs** tab. 

### Associate the Web ACL with Your Web Application
Update your Amazon CloudFront distribution(s) to activate AWS WAF and logging using the resources you generated. 

### Configure Web Access Logging
Configure Amazon CloudFront to send web access logs to the appropriate Amazon S3 bucket so that this data is available for the Log Parser AWS Lambda function.
Store Web Access Logs from a CloudFront Distribution
1. Open the [Amazon CloudFront console](https://console.aws.amazon.com/cloudfront/).
2. Select your web application’s distribution, and choose **Distribution Settings**.
3. On the **General** tab, choose **Edit**.
4. For **AWS WAF Web ACL**, choose the web ACL the solution created (the same name you assigned to the stack during initial configuration).
5. For **Logging**, choose **On**.
6. For **Bucket for Logs**, choose the Amazon S3 bucket that you want use to store web access logs (Defined in the parameter). The drop-down list enumerates the buckets associated with the current AWS account.
7. Set the log prefix as `AWSLogs/`. If you enter `AWSLogs` as the prefix but get a message saying **prefix cannot start with ‘AWSLogs’**, then remove the prefix. Application Load Balancer will use `AWSLogs` as the default prefix.
8. Choose **Yes**, **edit** to save your changes.

For more information, see [Access Logs](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/AccessLogs.html) in the Amazon CloudFront Developer Guide. 

### Uninstall Solution
To uninstall the solution, delete the CloudFormation stacks:
1. Sign in to the [AWS CloudFormation console](https://console.aws.amazon.com/cloudformation/home?).
2. Select the solution’s parent stack. All other solution stacks will be deleted automatically.
3. Choose **Delete**.

{{% notice note %}}
Uninstalling the solution deletes all the AWS resources used by the solution except for the Amazon S3 buckets. If some IP sets fail to delete due to rate exceeded throttling issue caused by the AWA WAF API limits, manually delete those IP sets and then delete the stack. 
{{% /notice%}}