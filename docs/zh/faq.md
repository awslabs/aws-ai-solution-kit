## 1. 在中国区域部署解决方案如何开通ICP备案？

本解决方案使用Amazon API Gateway来接收API调用请求，所以如果您希望在中国区域提供无需身份验证即可访问的API请求，需要申请并确保您的AWS账号已通过Internet Content Provider (ICP) 备案，80/443端口可以正常开启。具体流程可参见[ICP备案指南](https://www.amazonaws.cn/support/icp/)。

## 2. 部署解决方案时遇到*The account-level service limit 'ml.g4dn.xlarge for endpoint usage' is 0 Instances*，如何解决？

方案中的超分辨率API需要创建一个基于**Amazon SageMaker**的GPU类型实例，如果您AWS账户中对应实例限制不足，则会导致该功能部署异常。您可以在AWS管理控制台上方工具栏点击**支持中心**，创建支持工单，要求提高**Amazon SageMaker**服务的实例限额。具体步骤请参阅[请求提高配额](https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html)。

## 3. 部署解决方案时遇到*Resource handler returned message: "'MemorySize' value failed to satisfy constraint: Member must have value less than or equal to 3008*，如何解决？

方案中默认的**AWS Lambda**内存约为4GB（4096 MB），如果您AWS账户中AWS Lambda函数限制低于4096 MB，则会导致该部署异常。您可以在AWS管理控制台上方工具栏点击**支持中心**，创建支持工单，要求提高 **Lambda**服务的内存限额。具体步骤请参阅[请求提高配额](https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html)。

## 4. 使用解决方案都需要哪些AWS Identity and Access Management (IAM)权限？

您在部署解决方案之后，可以通过Amazon API Gateway调用API，需要的权限如下。其中**sagemaker:**仅限于**图像超分辨率**API。

| Actions |
| ------------------------------------- |
| apigateway:DELETE                     |
| apigateway:GET                        |
| apigateway:PATCH                      |
| apigateway:POST                       |
| apigateway:PUT                        |
| cloudformation:CancelUpdateStack      |
| cloudformation:ContinueUpdateRollback |
| cloudformation:CreateChangeSet        |
| cloudformation:CreateStack            |
| cloudformation:DeleteStack            |
| cloudformation:DescribeChangeSet      |
| cloudformation:DescribeStackEvents    |
| cloudformation:DescribeStackResources |
| cloudformation:DescribeStacks         |
| cloudformation:GetStackPolicy         |
| cloudformation:GetTemplateSummary     |
| cloudformation:ListChangeSets         |
| cloudformation:ListStackResources     |
| cloudformation:ListStacks             |
| cloudformation:RollbackStack          |
| cloudformation:UpdateStack            |
| cloudformation:UpdateStackSet         |
| ecr:BatchCheckLayerAvailability       |
| ecr:BatchDeleteImage                  |
| ecr:BatchGetImage                     |
| ecr:CreateRepository                  |
| ecr:DeleteRepository                  |
| ecr:DescribeRepositories              |
| ecr:GetDownloadUrlForLayer            |
| ecr:GetRepositoryPolicy               |
| ecr:InitiateLayerUpload               |
| ecr:PutImage                          |
| ecr:SetRepositoryPolicy               |
| iam:AttachRolePolicy                  |
| iam:CreateRole                        |
| iam:DeleteRole                        |
| iam:DeleteRolePolicy                  |
| iam:DetachRolePolicy                  |
| iam:GetRole                           |
| iam:ListRoles                         |
| iam:PassRole                          |
| iam:PutRolePolicy                     |
| lambda:AddPermission                  |
| lambda:CreateFunction                 |
| lambda:DeleteFunction                 |
| lambda:GetFunction                    |
| lambda:InvokeFunction                 |
| lambda:RemovePermission               |
| lambda:UpdateFunctionConfiguration    |
| s3:GetObject                          |
| sagemaker:CreateEndpoint              |
| sagemaker:CreateEndpointConfig        |
| sagemaker:CreateModel                 |
| sagemaker:DeleteEndpoint              |
| sagemaker:DeleteEndpointConfig        |
| sagemaker:DeleteModel                 |
| sagemaker:DescribeEndpoint            |
| sagemaker:DescribeEndpointConfig      |
| sagemaker:DescribeModel               |
| sagemaker:InvokeEndpoint              |
| sns:ListTopics                        |

## 5. 如何统一切换Amazon API Gateway中API的访问认证方式？

您可以通过AWS CloudFormation更新堆栈，从而统一修改现有资源的属性。

1. 访问[AWS CloudFormation控制台](https://console.aws.amazon.com/cloudformation/)。

2. 从堆栈列表中选择部署完成的方案根堆栈。

3. 在**堆栈详细信息**页面，选择**更新**。

4. 在**指定模板**页面，选择**使用当前模板**，然后选择**下一步**。

5. 在模板参数部分，修改**API Gateway Authorization**参数，然后选择**下一步**。

6. 在**配置堆栈选项**页面，选择**下一步**。

7. 在**审核**页面，查看并确认设置。确保选中确认模板将创建Amazon Identity and Access Management（IAM）资源的复选框。选择**下一步**。

8. 确认更改，并选择**更新堆栈**。

## 6. 如何单独切换Amazon API Gateway中API的访问认证方式？

按照以下步骤操作：

1. 访问[Amazon API Gateway控制台](https://console.aws.amazon.com/apigateway/)。
2. 从API列表中选择最新创建的方案API，打开API页面。您也可以按**已创建**的时间排序，便于查找。
3. 展开资源树，找到需要修改访问权限的资源路径下的**OPTIONS**节点，点击该节点打开**方法执行**配置页面。
4. 点击下方的**方法请求**链接。
5. 点击**授权**右侧的编辑按钮，展开下拉列表，选择**Amazon IAM**。
6. 点击**更新**按钮完成修改。更新完成后，授权项应显示为**Amazon IAM**。
7. 点击资源树中**OPTIONS**下方**POST**按钮，和修改OPTIONS的方法一样，在方法请求中将授权方式修改为**Amazon IAM**。
8. 点击方法执行左侧的**操作**下拉列表，选择**API操作**中的**部署 API**选项。
9. 在**部署API**对话框，选择**prod**或自定义名称的部署阶段，请不要选择[新阶段]，然后点击下方部署按钮完成部署。

## 7. 如何创建和使用带API密钥的使用计划？
本解决方案支持API使用计划（Usage Plans）。部署解决方案并测试API后，您可以实施API Gateway使用计划，将它们作为面向客户的产品/服务提供。您可以配置使用计划和API密钥，以允许客户按照商定的可满足其业务需求和预算限制的请求速率和配额来访问选定API。

如果需要的话，您可以为API设置默认方法级别限制或为单个API方法设置限制。API调用方必须在API请求的x-api-key标头中提供一个已分配的API密钥。 

如您需要配置*API使用计划*，请参考[配置使用计划](https://docs.aws.amazon.com/zh_cn/apigateway/latest/developerguide/api-gateway-create-usage-plans.html)。

## 8. 部署解决方案时遇到 *The account-level service limit 'ml.g4dn.xlarge for endpoint usage' is * Instances, with current utilization of * Instances and a request delta of * Instances. Please contact AWS support to request an increase for this limit.*，如何解决？
解决方案中使用的 SageMaker 终端节点类型为 `ml.g4dn.xlarge` ，服务限额（也称为限制）是您的账户中使用的服务资源或操作的最大数量，在终端节点数量超过了服务限额后，系统将会提示您这个错误信息，大多数区域支持的服务端点类型为 `ml.m4.xlarge` 的数量默认为4个，您可以按照 [提升服务配额](https://docs.amazonaws.cn/sagemaker/latest/dg/regions-quotas.html#service-limit-increase-request-procedure) 指引提高限制 SageMaker 服务配额。