### Frequently Asked Questions

### What AWS Identity and Access Management (IAM) permissions are required to deploy the solution?

The following permissions are required to deploy the solution and invoke the API via API Gateway after deployment, with **sagemaker:** only applicable to the **Image Super Resolution** API.

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

### How to resolve *The account-level service limit 'ml.g4dn.xlarge for endpoint usage' is 0 Instances* encountered when deploying the solution?

1. Sign into the [AWS console][https://console.aws.amazon.com/].
2. click on support on the top right corner
3. click create a case (orange button)
4. select Service Limit Increase radio button
5. For Limit Type, Search and Select SageMaker Notebook Instances
6. Write a short Use case description
7. For Limit, Select ml.[x]. [x] (in your case, ml.g4dn.xlarge)

### Deploying solution encountered *Resource handler returned message: "'MemorySize' value failed to satisfy constraint: Member must have value less than or equal to 3008*. How do I resolve this?

//TODO

### How do I consistently switch how APIs are authenticated for access in Amazon API Gateway?

With Amazon CloudFormation, you can change the properties of existing resources in your stack, and if you need to add or remove deployed AI features, you can do so by updating your stack.

1. On the Amazon CloudFormation console, select the completed AI Solution Kit stack in the Stack list. 2.

In the stack details pane, select Update. 3.

In the Template Parameters section, modify the **API Gateway Authorization** parameter, and select Next. 4.

4. On the **Configure Stack Options** page, select **Next**. 5.

5. On the **Audit** page, review and confirm the settings. Ensure that the checkbox to confirm that the template will create an Amazon Identity and Access Management (IAM) resource is checked. Select **Next**. 6.

6. If you are satisfied with the changes you have made, select Updata stack to complete the access rights update.

### How do I individually switch the access authentication method for APIs in Amazon API Gateway?
1. Open the Services panel in the Amazon Web Service console, find Application Services, and click API Gateway. 2.
2. Select the most recently created AI Solution Kit API in the API list, or sort by 'Created' to make it easier to find, then click the name link to open the API details page
3. Expand the resource tree, find the 'OPTIONS' node under the path of the resource you need to modify the access rights, and click it to display the method execution configuration page. Click the Method Request link under Method Execution
4. Then click the Edit button on the right side of the authorization, expand the drop-down list, select 'Amazon IAM', select it and click the Update button to complete the modification.
5. After updating, the authorization item should be displayed as 'Amazon IAM'. 6.
6. Next, click the POST button under OPTIONS in the resource tree, and modify the method of OPTIONS, change the authorization method to Amazon IAM in the method request, and then click the Update button.
7. Click on the 'Actions' drop-down button on the left side of the method execution, and click on the 'Deploy API' option under API Actions
8. In the Deploy API dialog box, select 'prod' or a custom name for the deployment phase, do not select [New Phase], and then click the Deploy button below to complete the deployment

### Create and use a usage plan with API key
This solution supports API Usage Plans. After deploying the solution and testing the APIs, you can implement API Gateway Usage Plans and offer them as a customer-facing product/service. You can configure usage plans and API keys to allow customers to access selected APIs at agreed request rates and quotas that meet their business needs and budget constraints, and you can set default method level limits for APIs or set limits for individual API methods if desired. The API caller must provide an assigned API key in the x-api-key header of the API request. 

If you need to configure an *API usage plan* please refer to: [Configure Usage Plan](https://docs.aws.amazon.com/zh_cn/apigateway/latest/developerguide/api-gateway-create-usage-plans.html )

### What target identification is currently supported by the Universal Target Detection API?
The following is a list of supported entities for target detection.

| ID                    |
| ---------------------------- |
| accordion                    |
| airplane                     |
| alligator                    |
| apple                        |
| army\_tank                   |
| awning                       |
| backpack                     |
| ball                         |
| balloon                      |
| banana                       |
| barrel                       |
| baseball                     |
| baseball\_bat                |
| baseball\_glove              |
| basket                       |
| bathtub                      |
| bear                         |
| bed                          |
| bee                          |
| beer\_bottle                 |
| bell\_pepper                 |
| belt                         |
| bench                        |
| bicycle                      |
| billboard                    |
| bird                         |
| blackboard                   |
| boat                         |
| book                         |
| bookcase                     |
| boot                         |
| bottle                       |
| bowl                         |
| bowling\_ball                |
| box                          |
| bracelet                     |
| brassiere                    |
| bread                        |
| broccoli                     |
| building                     |
| bus\_(vehicle)               |
| butterfly                    |
| cabinet                      |
| cake                         |
| camel                        |
| camera                       |
| can                          |
| candle                       |
| candy\_bar                   |
| cannon                       |
| canoe                        |
| car\_(automobile)            |
| carrot                       |
| cart                         |
| castle                       |
| cat                          |
| caterpillar                  |
| cello                        |
| cellular\_telephone          |
| chair                        |
| chicken\_(animal)            |
| chopping\_board              |
| chopstick                    |
| christmas\_tree              |
| clock                        |
| coat                         |
| cocktail                     |
| coffee\_table                |
| coin                         |
| computer\_keyboard           |
| computer\_monitor            |
| cone                         |
| cookie                       |
| cow                          |
| cowboy\_hat                  |
| crab\_(animal)               |
| crown                        |
| cucumber                     |
| cup                          |
| cupboard                     |
| curtain                      |
| deer                         |
| desk                         |
| dessert                      |
| dinosaur                     |
| dog                          |
| doll                         |
| dolphin                      |
| door                         |
| doorknob                     |
| doughnut                     |
| dragonfly                    |
| drawer                       |
| dress                        |
| drum\_(musical\_instrument)  |
| duck                         |
| duffel\_bag                  |
| eagle                        |
| earring                      |
| egg                          |
| elephant                     |
| fan                          |
| faucet                       |
| fireplace                    |
| fireplug                     |
| fish                         |
| flag                         |
| flower\_arrangement          |
| flowerpot                    |
| football\_helmet             |
| fork                         |
| fountain                     |
| french\_fries                |
| frisbee                      |
| frog                         |
| fruit                        |
| fruit\_juice                 |
| frying\_pan                  |
| gazelle                      |
| giraffe                      |
| glass\_(drink\_container)    |
| glove                        |
| goat                         |
| goggles                      |
| goose                        |
| grape                        |
| guitar                       |
| gun                          |
| hamburger                    |
| hamster                      |
| handbag                      |
| handle                       |
| harbor\_seal                 |
| hat                          |
| headset                      |
| helicopter                   |
| helmet                       |
| high\_heels                  |
| hog                          |
| horse                        |
| house                        |
| icecream                     |
| insect                       |
| jacket                       |
| jaguar                       |
| jean                         |
| jellyfish                    |
| kitchen\_table               |
| kite                         |
| knife                        |
| ladder                       |
| lamp                         |
| lantern                      |
| laptop\_computer             |
| lavender                     |
| lemon                        |
| lettuce                      |
| license\_plate               |
| life\_jacket                 |
| lightbulb                    |
| lighthouse                   |
| lily                         |
| lion                         |
| lizard                       |
| maple                        |
| mask                         |
| microphone                   |
| microwave\_oven              |
| minivan                      |
| mirror                       |
| monkey                       |
| motorcycle                   |
| mouse\_(computer\_equipment) |
| muffin                       |
| mug                          |
| mushroom                     |
| musical\_instrument          |
| napkin                       |
| necklace                     |
| necktie                      |
| nightstand                   |
| onion                        |
| orange\_(fruit)              |
| oven                         |
| owl                          |
| paddle                       |
| painting                     |
| palm\_tree                   |
| parachute                    |
| parking\_meter               |
| parrot                       |
| pasta                        |
| pastry                       |
| pen                          |
| penguin                      |
| person                       |
| piano                        |
| pillow                       |
| pizza                        |
| plastic\_bag                 |
| plate                        |
| polar\_bear                  |
| pool\_table                  |
| porch                        |
| poster                       |
| potted\_plant                |
| pumpkin                      |
| rabbit                       |
| refrigerator                 |
| remote\_control              |
| ring                         |
| roller\_skate                |
| rose                         |
| salad                        |
| sandal\_(type\_of\_shoe)     |
| sandwich                     |
| saucer                       |
| saxophone                    |
| scarf                        |
| scissors                     |
| sculpture                    |
| sheep                        |
| shirt                        |
| shoe                         |
| short\_pants                 |
| shrimp                       |
| sink                         |
| skateboard                   |
| ski                          |
| skirt                        |
| skullcap                     |
| snake                        |
| snowboard                    |
| soccer\_ball                 |
| sock                         |
| sofa                         |
| sofa\_bed                    |
| sparrow                      |
| speaker\_(stero\_equipment)  |
| spectacles                   |
| spider                       |
| spoon                        |
| sportswear                   |
| squirrel                     |
| stool                        |
| stop\_sign                   |
| stove                        |
| straw\_(for\_drinking)       |
| strawberry                   |
| street\_sign                 |
| streetlight                  |
| suit\_(clothing)             |
| suitcase                     |
| sunflower                    |
| sunglasses                   |
| sunhat                       |
| surfboard                    |
| sushi                        |
| swimming\_pool               |
| swimsuit                     |
| table                        |
| tablet\_computer             |
| taxi                         |
| teddy\_bear                  |
| telephone                    |
| television\_set              |
| tennis\_ball                 |
| tennis\_racket               |
| tent                         |
| tiger                        |
| toilet                       |
| toilet\_tissue               |
| tomato                       |
| toothbrush                   |
| towel                        |
| tower                        |
| toy                          |
| traffic\_light               |
| train\_(railroad\_vehicle)   |
| trash\_can                   |
| tray                         |
| tree                         |
| tripod                       |
| trousers                     |
| truck                        |
| trumpet                      |
| turtle                       |
| umbrella                     |
| vase                         |
| vegetables                   |
| violin                       |
| wall\_socket                 |
| watch                        |
| water\_jug                   |
| whale                        |
| wheel                        |
| wheelchair                   |
| window                       |
| wineglass                    |
| zebra                        |