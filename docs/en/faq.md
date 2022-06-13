## 1. How to make ICP recordal when deploying the solution in AWS China Regions?

This solution uses Amazon API Gateway to receive API call requests. If you want to provide API requests that can be accessed without authentication in the AWS China Regions, you need to apply for and ensure that your AWS account has been registered with the Internet Content Provider (ICP), and 80 /443 port can be enabled normally. For more information, refer to [ICP Recordal](https://www.amazonaws.cn/support/icp/).

## 2. When deploying the solution, I encountered *The account-level service limit 'ml.g4dn.xlarge for endpoint usage' is 0 Instances*. How to resolve it?

This API needs to create a GPU instance based on Amazon SageMaker. If the corresponding instance limit in your AWS account is insufficient, the API feature will be deployed abnormally. You can click **Support Center** on the toolbar at the top of the AWS Management Console to create a support ticket to request an increase in the instance limit of the Amazon SageMaker service. For more information, see [AWS service quotas](https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html).

## 3. When deploying the solution, I encountered *Resource handler returned message: "'MemorySize' value failed to satisfy constraint: Member must have value less than or equal to 3008*. How to resolve it?

The default **AWS Lambda** memory is about 4GB (4096 MB). If the AWS Lambda function limit in your AWS account is lower than 4096 MB, the API feature will be deployed abnormally. You can click **Support Center** on the toolbar at the top of the AWS Management Console to create a support ticket and request to increase the memory limit of the AWS Lambda service. For more information, see [AWS service quotas](https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html).

## 4. What AWS Identity and Access Management (IAM) permissions are required to deploy the solution?

The following permissions are required to deploy the solution and invoke the API via API Gateway after deployment. **sagemaker:** is only applicable to the **Image Super Resolution** API.

| Actions |
| ------------------------------------- |
| apigateway:DELETE |
| apigateway:GET |
| apigateway:PATCH |
| apigateway:POST |
| apigateway:PUT |
| cloudformation:CancelUpdateStack |
| cloudformation:ContinueUpdateRollback |
| cloudformation:CreateChangeSet |
| cloudformation:CreateStack |
| cloudformation:DeleteStack |
| cloudformation:DescribeChangeSet | cloudformation:DescribeChangeSet
| cloudformation:DescribeStackEvents |
| cloudformation:DescribeStackResources |
| cloudformation:DescribeStackStacks |
| cloudformation:GetStackPolicy | | cloudformation:GetStackPolicy
| cloudformation:GetTemplateSummary |
| cloudformation:ListChangeSets |
| cloudformation:ListStackResources |
| cloudformation:ListStacks |
| cloudformation:RollbackStack |
| cloudformation:UpdateStack | cloudformation:UpdateStack
| cloudformation:UpdateStackSet |
| cloudformation:UpdateStackSet | cloudformation:UpdateStackSet | cloudformation:BatchCheckLayerAvailability |
| ecr:BatchDeleteImage |
| ecr:BatchGetImage |
| ecr:CreateRepository |
| ecr:DeleteRepository |
| ecr:DescribeRepositories |
| ecr:GetDownloadUrlForLayer |
| ecr:GetRepositoryPolicy |
| ecr:InitiateLayerUpload |
| ecr:PutImage |
| ecr:SetRepositoryPolicy |
| iam:AttachRolePolicy |
| iam:CreateRole |
| iam:DeleteRole |
| iam:DeleteRolePolicy | iam:DeleteRolePolicy
| iam:DetachRolePolicy | iam:GetRolePolicy
| iam:GetRole |
| iam:ListRoles |
| iam:PassRole |
| iam:PutRolePolicy |
| lambda:AddPermission |
| lambda:CreateFunction |
| lambda:DeleteFunction |
| lambda:GetFunction |
| lambda:InvokeFunction |
| lambda:RemovePermission |
| lambda:UpdateFunctionConfiguration |
| s3:GetObject |
| sagemaker:CreateEndpoint |
| sagemaker:CreateEndpointConfig |
| sagemaker:CreateModel |
| sagemaker:DeleteEndpoint | | sagemaker:DeleteEndpoint
| sagemaker:DeleteEndpointConfig | sagemaker:DeleteEndpointConfig |
| sagemaker:DeleteModel |
| sagemaker:DescribeEndpoint | | sagemaker:DescribeEndpoint
| sagemaker:DescribeEndpointConfig |
| sagemaker:DescribeModel |
| sagemaker:InvokeEndpoint |
| sns:ListTopics |

## 5. How to universally switch the way APIs are authenticated for access in Amazon API Gateway?

With AWS CloudFormation, you can update the stack to change the properties of existing resources in your stack.

1. Sign in to the [AWS CloudFormation console](https://console.aws.amazon.com/cloudformation/).
2. On the **Stacks** page, select the solution’s root stack.
3. On the **Stack details** page, choose **Update**.
4. Select **Use current template**, and choose **Next**.
5. Update the parameter **API Gateway Authorization**, and choose **Next**. 
6. On the **Configure stack options** page, choose **Next**.
7. On the **Review** page, review and confirm the settings. Check the box acknowledging that the template will create AWS Identity and Access Management (IAM) resources. Choose **Next**.
8. Choose **Update stack** to update the stack.

## 6. How to individually switch the way APIs are authenticated for access in Amazon API Gateway?

Follow the steps below:

1. Access [Amazon API Gateway console](https://console.aws.amazon.com/apigateway/).

2. Select the most recently created AI Solution Kit API in the API list, and open the API details page. You can sort by **Created** to facilitate the search.
3. Expand the resource tree, find the **OPTIONS** node under the path of the resource you need to modify the access rights, and click it to display the method execution configuration page. 
4. Click the **Method Request** link under Method Execution.
5. Choose the Edit button on the right side of the authorization, expand the drop-down list, and select **Amazon IAM**. 
6. Choose the **Update** button to complete the modification. After the update, the authorization item should be displayed as 'Amazon IAM'. 6.
7. Choose the **POST** button under **OPTIONS** in the resource tree, and modify the method of OPTIONS, change the authorization method to **Amazon IAM** in the method request, and then choose the **Update** button.
8. Choose the **Actions** drop-down button on the left side of the method execution, and click on the **Deploy API** option under API Actions.
9. In the **Deploy API** dialog box, select **prod** or a custom name for the deployment phase (do not select [New Phase]), and then click the Deploy button below to complete the deployment.

## 7. How to create and use a usage plan with API key?

This solution supports API Usage Plans. After deploying the solution and testing the APIs, you can implement API Gateway Usage Plans and offer them as a customer-facing product/service. You can configure usage plans and API keys to allow customers to access selected APIs at agreed request rates and quotas that meet their business needs and budget constraints.

You can set default method level limits for APIs or set limits for individual API methods if desired. The API caller must provide an assigned API key in the x-api-key header of the API request. 

To configure an *API usage plan*, refer to [Configure Usage Plan](https://docs.aws.amazon.com/en_us/apigateway/latest/developerguide/api-gateway-create-usage-plans.html).

