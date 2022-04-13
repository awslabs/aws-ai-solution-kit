---
title: Deploy OWASP Juice Shop 
weight: 3
---

In this section you will deploy the OWASP Juice Shop by CloudFormation stack, first please deploy the Juice Shop Web Application in **US East (N. Virginia)** (us-east-1) region.
[![Deploy OWASP Juice Shop](/images/deploy_to_aws.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=WAFWorkshopSampleWebApp&templateURL=https%3a%2f%2faws-waf-workshop-v2-us-east-1.s3.us-east-1.amazonaws.com%2faws-waf-v2-workshop%2flatest%2fmain.template)


This CloudFormation stack will take approximately 5 minutes to complete.
Step by step instructions:
* Provide your stack with a unique name. *Note: Be careful not to exceed the 64-character stack name limit*
* Click the “Next” button at the bottom of the remaining pages, using the default values.
* On the final page, ensure the tickboxes allowing AWS CloudFormation to create IAM resources with custom names are ticked.
* Click the orange "Create stack" button at the bottom-right of the page to deploy the stack into your account.

CloudFormation will now deploy the Juice Shop application into your account. Wait until all stacks are shown in a CREATE_COMPLETE state.

* Find the `JuiceShopUrl` value in the CloudFormation template output. This is the address of your Juice Shop site.![JuiceShop URL](/images/juiceshop_url.png?width=50pc)


