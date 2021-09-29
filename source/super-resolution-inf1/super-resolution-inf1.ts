import * as cdk from '@aws-cdk/core';
import * as sagemaker from "@aws-cdk/aws-sagemaker";
import * as iam from "@aws-cdk/aws-iam";
import * as agw from "@aws-cdk/aws-apigateway";

export class SuperResolutionInf1Stack extends cdk.Stack {

    constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);
        this.templateOptions.description = '(SO8023-sr) - AI Solution Kits - Super Resolution with Amazon SageMaker Inferentia Instance. Template version v1.0.0';

        const deployInstanceType = new cdk.CfnParameter(this, 'deployInstanceType', {
            description: 'Please specify the instance type for hosting inference service',
            type: 'String',
            default: 'ml.inf1.xlarge',
            allowedValues: [
                'ml.inf1.xlarge',
                'ml.inf1.2xlarge',
                'ml.inf1.6xlarge'
            ]
        });

        const customStageName = new cdk.CfnParameter(this, "customStageName", {
            default: 'prod',
            type: 'String',
            description: 'Custom Stage Name, default value is: prod'
        });

        const customAuthType = new cdk.CfnParameter(this, "customAuthType", {
            default: 'AWS_IAM',
            type: 'String',
            description: `Custom Authorization Type, default value is: AWS_IAM`,
            allowedValues: ['NONE', 'AWS_IAM']
        });

        // /*-------------------------------------------------------------------------------*/
        // /*---------  Sagemaker Model/Endpoint Configuration/Endpoint Provision  ---------*/
        // /*-------------------------------------------------------------------------------*/
        const sagemakerExecuteRole = new iam.Role(
            this,
            'sagemakerExecuteRole',
            {
                roleName: `ai-kits-super-resolution-sagemaker-execution-role-cdk`,
                assumedBy: new iam.ServicePrincipal('sagemaker.amazonaws.com'),
                managedPolicies: [
                    iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonS3FullAccess'),
                    iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonEC2ContainerRegistryFullAccess'),
                    iam.ManagedPolicy.fromAwsManagedPolicyName('CloudWatchLogsFullAccess'),
                ]
            }
        );

        // configure container image name
        new cdk.CfnCondition(this,
            'IsChinaRegionCondition',
            { expression: cdk.Fn.conditionEquals(cdk.Aws.PARTITION, 'aws-cn') });

        const imageUrl = cdk.Fn.conditionIf(
            'IsChinaRegionCondition',
            `753680513547.dkr.ecr.${cdk.Aws.REGION}.amazonaws.com.cn/ai-kits-super-resolution:latest`,
            `753680513547.dkr.ecr.${cdk.Aws.REGION}.amazonaws.com/ai-kits-super-resolution:latest`
        );

        // create model
        const sagemakerEndpointModel = new sagemaker.CfnModel(
            this,
            'sagemakerEndpointModel',
            {
                modelName: `ai-kits-super-resolution-endpoint-model`,
                executionRoleArn: sagemakerExecuteRole.roleArn,
                containers: [
                    {
                        image: imageUrl.toString(),
                        mode: 'SingleModel',
                        environment: {}
                    }
                ],
            }
        );

        // create endpoint configuration
        const sagemakerEndpointConfig = new sagemaker.CfnEndpointConfig(
            this,
            'sagemakerEndpointConfig',
            {
                endpointConfigName: `ai-kits-super-resolution-endpoint-config`,
                productionVariants: [{
                    initialInstanceCount: 1,
                    initialVariantWeight: 1,
                    instanceType: `${deployInstanceType.valueAsString}`,
                    modelName: sagemakerEndpointModel.attrModelName,
                    variantName: 'AllTraffic',
                }]
            }
        );

        // create endpoint
        const sagemakerEndpoint = new sagemaker.CfnEndpoint(
            this,
            'sagemakerEndpoint',
            {
                endpointName: `ai-kits-super-resolution-endpoint`,
                endpointConfigName: sagemakerEndpointConfig.attrEndpointConfigName
            }
        );

        const policyResource = cdk.Fn.conditionIf(
            'IsChinaRegionCondition',
            `arn:aws-cn:sagemaker:${cdk.Aws.REGION}:${cdk.Aws.ACCOUNT_ID}:endpoint/${sagemakerEndpoint.endpointName}`,
            `arn:aws:sagemaker:${cdk.Aws.REGION}:${cdk.Aws.ACCOUNT_ID}:endpoint/${sagemakerEndpoint.endpointName}`
        );

        const apiGatewayAccessToSageMakerRole = new iam.Role(
            this,
            'apiGatewayAccessToSageMakerRole',
            {
                roleName: `ai-kits-super-resolution-sagemaker-access-role`,
                assumedBy: new iam.ServicePrincipal('apigateway.amazonaws.com'),
                managedPolicies: [iam.ManagedPolicy.fromAwsManagedPolicyName("service-role/AmazonAPIGatewayPushToCloudWatchLogs")],
                inlinePolicies: {
                    'SageMakerEndpointInvokeAccess': new iam.PolicyDocument({
                        statements: [new iam.PolicyStatement({
                            actions: ['sagemaker:InvokeEndpoint'],
                            resources: [policyResource.toString()],
                            effect: iam.Effect.ALLOW
                        })]
                    })
                }
            }
        );

        // api gateway provision
        const apiRouter = new agw.RestApi(
            this,
            'SuperResolutionInf1RESTAPI',
            {
                deploy: false,
                endpointConfiguration: {
                    types: [agw.EndpointType.REGIONAL]
                },
                defaultCorsPreflightOptions: {
                    allowHeaders: [
                        'Content-Type',
                        'X-Amz-Date',
                        'Authorization',
                        'X-Api-Key',
                    ],
                    allowMethods: ['POST'],
                    allowCredentials: true,
                    allowOrigins: agw.Cors.ALL_ORIGINS,
                },
            }
        );

        const deployment = new agw.Deployment(this, 'Deployment', {
            api: apiRouter,
        });

        apiRouter.deploymentStage = new agw.Stage(this, 'stage_aikits', {
            stageName: customStageName.valueAsString,
            deployment,
            dataTraceEnabled: true,
            loggingLevel: agw.MethodLoggingLevel.INFO,
        });

        const sageMakerIntegration = new agw.AwsIntegration({
            service: 'runtime.sagemaker',
            region: `${cdk.Aws.REGION}`,
            path: `endpoints/${sagemakerEndpoint.endpointName}/invocations`,
            integrationHttpMethod: 'POST',
            options: {
                credentialsRole: apiGatewayAccessToSageMakerRole,
                integrationResponses: [
                    {
                        statusCode: '200'
                    },
                ],
            }
        });

        const post = apiRouter.root.addResource('resolution').addMethod('POST',
            sageMakerIntegration,
            {
                methodResponses: [{ statusCode: '200' }],
            }
        );

        new cdk.CfnOutput(this, 'InvokeURLArn', {value: post.methodArn});

        const invokeUrl = cdk.Fn.conditionIf(
            'IsChinaRegionCondition',
            `https://${post.api.restApiId}.execute-api.${cdk.Aws.REGION}.amazonaws.com.cn/${customStageName.valueAsString}/resolution`,
            `https://${post.api.restApiId}.execute-api.${cdk.Aws.REGION}.amazonaws.com/${customStageName.valueAsString}/resolution`
        );
        new cdk.CfnOutput(this, 'InvokeURL', {value: invokeUrl.toString()});
    }
}

