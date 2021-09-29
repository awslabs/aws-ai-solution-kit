import {
    Construct,
    CfnOutput,
    Aws,
    Fn,
    CfnCondition,
    CfnParameter
} from "@aws-cdk/core";
import {
    RestApi,
    Resource,
    MethodLoggingLevel,
    EndpointType,
    LambdaIntegration,
    AuthorizationType,
    LogGroupLogDestination,
    Method,
    CfnMethod,
    Deployment,
    Stage,
    Cors,
    CfnResource
} from '@aws-cdk/aws-apigateway';
import {Function} from '@aws-cdk/aws-lambda';
import * as lambda from "@aws-cdk/aws-lambda";
import * as logs from '@aws-cdk/aws-logs';
import * as cloudtrail from "@aws-cdk/aws-cloudtrail";

export interface AiKitsApiProps {
    readonly apiName: string;
    readonly stageName: string;
    readonly resourcePath: string;
    readonly authType?: AuthorizationType;
    readonly postFunction: lambda.IFunction
}

export class AiKitsRestApi extends Construct {
    readonly api: RestApi;
    readonly resource: Resource;
    readonly authType: AuthorizationType;

    constructor(scope: Construct, id: string, props: AiKitsApiProps) {
        super(scope, id);

        const customStageName = new CfnParameter(this, "customStageName", {
            default: props.stageName,
            type: 'String',
            description: `Custom Stage Name, default value is: ${props.stageName}`
        });
        // const customResourcePath = new CfnParameter(this, "customResourcePath", {
        //     default: props.resourcePath,
        //     type: 'String',
        //     description: `Custom Resource Path, default value is: ${props.resourcePath}`
        // });
        const customAuthType = new CfnParameter(this, "customAuthType", {
            default: 'AWS_IAM',
            type: 'String',
            description: `Custom Authorization Type, default value is: AWS_IAM`,
            allowedValues: ['NONE', 'AWS_IAM']
        });

        this.authType = props.authType || AuthorizationType.IAM;
        const apigatewayLogGroup = new logs.LogGroup(scope, "AiKitsApiAccessLogs", {
            retention: logs.RetentionDays.THREE_MONTHS,
        });
        this.api = new RestApi(this, 'AiKitsApi', {
            restApiName: props.apiName,
            description: `AI Solutions Kits REST API (${props.apiName})`,
            deploy: false,

            defaultCorsPreflightOptions: {
                allowHeaders: [
                    'Content-Type',
                    'X-Amz-Date',
                    'Authorization',
                    'X-Api-Key',
                ],
                allowMethods: ['POST'],
                allowCredentials: true,
                allowOrigins: Cors.ALL_ORIGINS,
            },
            endpointConfiguration: {
                types: [EndpointType.REGIONAL],
            },
        });

        const deployment = new Deployment(this, 'Deployment', {
            api: this.api,
        });

        this.api.deploymentStage = new Stage(this, 'stage_aikits', {
            stageName: customStageName.valueAsString,
            deployment,
            dataTraceEnabled: true,
            loggingLevel: MethodLoggingLevel.INFO,
        });

        this.resource = this.api.root.addResource(props.resourcePath);

        const post = this.addMethod('POST', props.postFunction) as Method

        const methodResource = post.node.findChild('Resource') as CfnMethod
        methodResource.addPropertyOverride('AuthorizationType', customAuthType.valueAsString)
        // methodResource.addPropertyOverride('pathPart', customResourcePath.valueAsString)

        new CfnOutput(this, 'InvokeURLArn', {value: post.methodArn});

        const inCnCondition = new CfnCondition(this,
            'IsChinaRegionCondition',
            {expression: Fn.conditionEquals(Aws.PARTITION, 'aws-cn')});
        const invokeUrl = Fn.conditionIf(
            inCnCondition.logicalId,
            `https://${post.api.restApiId}.execute-api.${Aws.REGION}.amazonaws.com.cn/${customStageName.valueAsString}/${props.resourcePath}`,
            `https://${post.api.restApiId}.execute-api.${Aws.REGION}.amazonaws.com/${customStageName.valueAsString}/${props.resourcePath}`
        );
        new CfnOutput(this, 'InvokeURL', {value: invokeUrl.toString()});

        const deploymentRes = deployment.node.defaultChild as CfnResource
        deploymentRes.addMetadata('cfn_nag',{
            rules_to_suppress: [
                {
                    "id": "W68",
                },
                {
                    "id": "W5",
                }
            ]
        });

        const stageRes = this.api.deploymentStage.node.defaultChild as CfnResource
        stageRes.addMetadata('cfn_nag',{
            rules_to_suppress: [
                {
                    "id": "W69",
                },
                {
                    "id": "W64",
                }
            ]
        });

        const logGroup = apigatewayLogGroup.node.defaultChild as CfnResource
        logGroup.addMetadata('cfn_nag',{
            rules_to_suppress: [
                {
                    "id": "W84",
                }
            ]
        });
    }

    public addMethod(method: string, lambda_function: lambda.IFunction) {
        return this.resource.addMethod(
            method,
            new LambdaIntegration(lambda_function, {proxy: true}),
            {
                authorizationType: this.authType,
            });
    }
}
