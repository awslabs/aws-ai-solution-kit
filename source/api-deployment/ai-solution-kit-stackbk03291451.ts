import {
    AuthorizationType, CfnMethod, Cors, Deployment, EndpointType,
    LambdaIntegration, Method, MethodLoggingLevel, RestApi, Stage, CfnStage, CfnDeployment, CfnRestApi
} from '@aws-cdk/aws-apigateway';
import { Repository } from "@aws-cdk/aws-ecr";
import { DockerImageCode, DockerImageFunction } from "@aws-cdk/aws-lambda";
import {
    Aws, CfnCondition, CfnMapping, CfnOutput, CfnParameter, Construct, Duration, Fn, RemovalPolicy, Stack,
    StackProps, CustomResource, CfnStack, NestedStack, CfnResource,
} from "@aws-cdk/core";
import { CfnBucket } from '@aws-cdk/aws-s3';
import { CfnInclude, CfnIncludeProps } from "@aws-cdk/cloudformation-include";
import { Runtime, Tracing } from '@aws-cdk/aws-lambda';
import { NodejsFunction } from '@aws-cdk/aws-lambda-nodejs';
import * as cr from '@aws-cdk/custom-resources';
import * as iam from '@aws-cdk/aws-iam';
import * as path from 'path';
import { PythonFunction } from "@aws-cdk/aws-lambda-python";
// import { InferOCRNestedStack } from './features/archieve/nest-ocr';
// import { SRNestedStack } from './features/nest-sr';
import { SuperResolutionFeatureNestedStack } from './features/super-resolution-feature';
import { GeneralOCRFeatureNestedStack } from './features/general-ocr-feature';
// import { SegNestedStack } from './features/nest-seg';
import { ECRDeployment, DockerImageName } from '../lib/cdk-ecr-deployment/lib';
import { ApiDocsNestedStack } from './nest-api-docs';
import { FeatureConditionConstruct } from './feature-condition-construct';
import { DataResourceType } from '@aws-cdk/aws-cloudtrail';
import { FeatureNestedStack } from './feature-nested-stack';

// all new, create CR, run CR in each nested stack, if Yes
// deployed, update stack, run CR in each nested stack(change Y/N param), let CR to add or delete resources by new Yes/No
// New feat, CF changed, new feat should be list in CF stack, it should not effect old ones, it operates the old API GW, r


export class AISolutionKitStack extends Stack {
    constructor(scope: Construct, id: string, props?: StackProps) {

        super(scope, id, props);
        this.templateOptions.description = `(SO8023) - AI Solution Kits - Template version v1.0.0`;

        const customStageName = new CfnParameter(this, "customStageName", {
            default: 'prod',
            type: 'String',
            description: `Custom Stage Name, default value is: prod`
        });

        const customAuthType = new CfnParameter(this, "APIGatewayAuthorization", {
            default: 'AWS_IAM',
            type: 'String',
            description: `Custom API Gateway Authorization Type, default value is: AWS_IAM`,
            allowedValues: ['AWS_IAM', 'NONE']
        });

        const singleDeployment = new CfnParameter(this, "singleDeployment", {
            default: 'no',
            type: 'String',
            description: `Custom Authorization Type, default value is: AWS_IAM`,
            allowedValues: ['yes', 'no']
        });

        //new features

        const generalOCRFeature = new CfnParameter(this, "InstallGeneralOCRFeature", {
            default: 'no',
            type: 'String',
            description: `Install General OCR Feature`,
            allowedValues: ['yes', 'no']
        });
        const generalOCRFeatureCondition = new CfnCondition(
            this,
            'generalOCRFeatureCondition',
            {
                expression: Fn.conditionEquals(generalOCRFeature, 'yes')
            }
        )

        const superResolutionFeature = new CfnParameter(this, "InstallSuperResolutionFeature", {
            default: 'yes',
            type: 'String',
            description: 'Install Super Resolution Feature',
            allowedValues: ['yes', 'no']
        });
        const superResolutionFeatureCondition = new CfnCondition(
            this,
            'superResolutionFeatureCondition',
            {
                expression: Fn.conditionEquals(superResolutionFeature, 'yes')
            }
        )

        // const segFeature = new CfnParameter(this, "InstallSEGFeature", {
        //     default: 'no',
        //     type: 'String',
        //     description: `Custom Authorization Type, default value is: AWS_IAM`,
        //     allowedValues: ['yes', 'no']
        // });
        // const segFeatureCondition = new CfnCondition(
        //     this,
        //     'segFeatureCondition',
        //     {
        //         expression: Fn.conditionEquals(segFeature, 'yes')
        //     }
        // )

        const apiDocsFeature = new CfnParameter(this, "InstallApiDocsFeature", {
            default: 'yes',
            type: 'String',
            description: `Custom Authorization Type, default value is: AWS_IAM`,
            allowedValues: ['yes', 'no']
        });

        const apiDocsFeatureCondition = new CfnCondition(
            this,
            'apiDocsFeatureCondition',
            {
                expression: Fn.conditionEquals(apiDocsFeature, 'yes')
            }
        )

        const api = new RestApi(this, 'AiSolutionKitApi', {
            restApiName: 'AI Solution Kit API',
            description: 'AI Solutions Kit REST API. You can find out more about AI Solution Kit at https://www.amazonaws.cn/solutions/ai-solution-kit.',
            deploy: false,
            defaultCorsPreflightOptions: {
                allowHeaders: [
                    'Content-Type',
                    'X-Amz-Date',
                    'Authorization',
                    'X-Api-Key',
                ],
                allowMethods: ['POST', 'OPTION'],
                allowCredentials: true,
                allowOrigins: Cors.ALL_ORIGINS,
            },
            endpointConfiguration: {
                types: [EndpointType.REGIONAL],
            },
            // deployOptions: {
            //     stageName: 'ai-solution-kit',
            //     tracingEnabled: true,
            //     loggingLevel: MethodLoggingLevel.INFO,
            // }
        });

        // const deployment = new Deployment(this, 'Deployment', {
        //     api: api,
        //     retainDeployments: true
        // });

        // api.deploymentStage = new Stage(this, 'stage_aikits', {
        //     stageName: customStageName.valueAsString,
        //     deployment,
        //     dataTraceEnabled: true,
        //     loggingLevel: MethodLoggingLevel.INFO,
        // });

        // api.root.addMethod('ANY');
        // api.root.addResource("sub");

        const inCnCondition = new CfnCondition(this,
            'IsChinaRegionCondition',
            { expression: Fn.conditionEquals(Aws.PARTITION, 'aws-cn') });
        const invokeUrl = Fn.conditionIf(
            inCnCondition.logicalId,
            `https://${api.restApiId}.execute-api.${Aws.REGION}.amazonaws.com.cn/${customStageName.valueAsString}`,
            `https://${api.restApiId}.execute-api.${Aws.REGION}.amazonaws.com/${customStageName.valueAsString}`
        );
        new CfnOutput(this, 'InvokeURL', { value: invokeUrl.toString() });

        // const apiLambda = new lambda.Function(this, `apihandler`, {
        //     // entry: path.join(__dirname, '../lib/api_resource'), // required
        //     // index: 'my_index.py', // optional, defaults to 'index.py'
        //     handler: 'api_resource.lambda_handler', // optional, defaults to 'handler'
        //     runtime: lambda.Runtime.PYTHON_3_9, // optional, defaults to lambda.Runtime.PYTHON_3_7
        //     code: lambda.Code.fromAsset(path.join(__dirname, '../lib/api_resource')),
        //     // handler: "api_resource.lambda_handler",
        //     memorySize: 2048,
        //     timeout: Duration.minutes(5),
        //     allowPublicSubnet: true,
        //     environment:{
        //         REST_API_ID: api.restApiId,
        //         CUSTOM_AUTH_TYPE: customAuthType.valueAsString
        //     }
        // });

        // const efsProvider = new cr.Provider(this, `apiprovider`, {
        //     onEventHandler: apiLambda,
        //     // vpc: vpc,
        // });

        // const customResource = new CustomResource(this, `apicustomresource`, {
        //     serviceToken: efsProvider.serviceToken,
        //     resourceType: "Custom::EfsModelLambda",
        //     properties: {
        //         MountPath: 'aaa',
        //         Objects: 'bbb',
        //         Features: [
        //             {
        //                 'install': ocrFeature.valueAsString,
        //                 'url': '295155050487.dkr.ecr.us-west-2.amazonaws.com/aikits:ocr-lite',
        //                 'resource': 'ocr'
        //             },
        //             {
        //                 'install': srFeature.valueAsString,
        //                 'url': '295155050487.dkr.ecr.us-west-2.amazonaws.com/aikits:ocr-lite',
        //                 'resource': 'sr'
        //             },
        //             {
        //                 'install': segFeature.valueAsString,
        //                 'url': '295155050487.dkr.ecr.us-west-2.amazonaws.com/aikits:ocr-lite',
        //                 'resource': 'seg'
        //             },
        //         ]
        //     },
        //     removalPolicy: RemovalPolicy.DESTROY,
        // });

        // apiLambda.addToRolePolicy(
        //     new iam.PolicyStatement({
        //         effect: iam.Effect.ALLOW,
        //         actions: [
        //             "apigateway:*"
        //         ],
        //         resources: ['*']
        //     })
        // )
        // apiLambda.addToRolePolicy(
        //     new iam.PolicyStatement({
        //         effect: iam.Effect.ALLOW,
        //         actions: [
        //             "iam:*",
        //         ],
        //         resources: ['*']
        //     })
        // )
        // apiLambda.addToRolePolicy(
        //     new iam.PolicyStatement({
        //         effect: iam.Effect.ALLOW,
        //         actions: [
        //             "lambda:*"
        //         ],
        //         resources: ['*']
        //     })
        // )
        // apiLambda.addToRolePolicy(
        //     new iam.PolicyStatement({
        //         effect: iam.Effect.ALLOW,
        //         actions: [
        //             "ecr:*"
        //         ],
        //         resources: ['*']
        //     })
        // )
        new CfnOutput(this, 'AISolutionKitStack CfnOutput', { value: 'AISolutionKitStack CfnOutput' });

        // const cfnTemplate = new CfnInclude(this, 'OCRTemplate', {
        //     templateFile: path.join(__dirname, 'conditional.template'),
        //     parameters: {
        //         'apiLambdaArn': apiLambda.functionArn,
        //         'CustomResourceServiceToken': efsProvider.serviceToken
        //     }
        // });

        // const sec = new SolutionEcrConstruct(this, "ocrEcr")
        // console.log(sec.ecrDeployment.serviceToken)

        const ecrDeployment = new ECRDeployment(this, 'ai-solution-kit-deployment', {
            src: new DockerImageName(''),
            dest: new DockerImageName(''),
        });

        // const nestedocrFeature = new InferOCRNestedStack(this, 'nested-ocr-stack', api, ecrDeployment) as NestedStack;;
        // nestedocrFeature.node.addDependency(ecrDeployment);
        // const nestedsrFeature = new SRNestedStack(this, 'nested-sr-stack', api, ecrDeployment, {
        //     reatApi: api
        // }) as NestedStack;

        // const map = new CfnMapping(this, 'authorizationTypeMapping', {
        //     mapping: {
        //         'AWS-IAM': { value: AuthorizationType.IAM },
        //         'NONE': { value: AuthorizationType.NONE },
        //     },
        // });

        const authType = `${customAuthType.valueAsString}` as AuthorizationType;
        // const authType = map.findInMap(`${customAuthType.valueAsString}`, 'value') as AuthorizationType;

        // let authTypeString: keyof typeof AuthorizationType = `${customAuthType.valueAsString}`;
        // authTypeString = authType;

        const nestedsrFeature = new SuperResolutionFeatureNestedStack(this, 'nested-sr-stack', {
            restApi: api,
            customAuthorizationType: authType,
            ecrDeployment: ecrDeployment
        }) as NestedStack;
        // const nestedocrFeature = new GeneralOCRFeatureNestedStack(this, 'nested-ocr-stack', {
        //     restApi: api,
        //     customAuthorizationType: customAuthType.valueAsString,
        //     ecrDeployment: ecrDeployment
        // }) as NestedStack;
        // nestedsrFeature.node.addDependency(nestedocrFeature);
        // const nestedsegFeature = new SegNestedStack(this, 'nested-seg-stack', efsProvider.serviceToken) as NestedStack;
        // nestedsegFeature.node.addDependency(nestedsrFeature);

        // console.log('================');
        // console.log(nestedocrFeature.node.children[0].node);
        // console.log('================');
        // (nestedocrFeature.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('InstallOCR');
        // (nestedsrFeature.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('InstallSR');
        // (nestedocrFeature.nestedStackResource as CfnStack).cfnOptions.condition = generalOCRFeatureCondition;
        (nestedsrFeature.nestedStackResource as CfnStack).cfnOptions.condition = superResolutionFeatureCondition;
        // (nestedocrFeature.nestedStackResource as CfnStack).cfnOptions.condition = ocrFeatureCondition.condition;
        // (nestedsegFeature.nestedStackResource as CfnStack).cfnOptions.condition = segFeatureCondition;

        // const apiDocs = new ApiDocsNestedStack(this, "api-docs", {
        //     restApi: api,
        //     invokeUrl: invokeUrl.toString()
        // });
        // (apiDocs.nestedStackResource as CfnStack).cfnOptions.condition = apiDocsFeatureCondition;
        // const apiDocFunction = new NodejsFunction(this, 'api-doc-function', {
        //     runtime: Runtime.NODEJS_14_X,
        //     memorySize: 1024,
        //     timeout: Duration.seconds(15),
        //     handler: 'handler',
        //     entry: path.join(__dirname, '/swagger-ui/app.js'),
        //     tracing: Tracing.ACTIVE,
        //     bundling: {
        //         nodeModules: [
        //             'yamljs',
        //             'serverless-http',
        //             'express',
        //             'serverless-http',
        //             'swagger-ui-express'
        //         ],
        //         minify: true,
        //         commandHooks: {
        //             beforeBundling(inputDir: string, outputDir: string): string[] {
        //                 return [
        //                     `cp -R ${inputDir}/source/api-deployment/swagger-ui/* ${outputDir}`
        //                 ]
        //             },
        //             beforeInstall() {
        //                 return []
        //             },
        //             afterBundling(_inputDir: string, _outputDir: string): string[] {
        //                 return []
        //             },
        //         },
        //     },
        //     environment: {
        //         SWAGGER_SPEC_URL: invokeUrl.toString()
        //     }
        // });

        // const resource = api.root.addResource('api-docs');
        // const proxy = resource.addProxy({
        //     anyMethod: true,
        //     defaultIntegration: new LambdaIntegration(apiDocFunction, { proxy: true })
        // });

        // const post = resource.addMethod('GET',
        //     new LambdaIntegration(apiDocFunction, { proxy: true }),
        //     {
        //         authorizationType: AuthorizationType.NONE,
        //     }
        // )
        const deployment = new Deployment(this, 'new_deployment', {
            api: api,
            // retainDeployments: true,
        });
        // const apiStage = api.deploymentStage;
        // const cfnStage = apiStage.node.defaultChild as CfnStage;
        // const cfnDeployment = api.latestDeployment?.node.defaultChild as CfnDeployment
        // const cfnApi = api.node.defaultChild as CfnRestApi;
        const deploymentStage = new Stage(this, 'stage_aikits', {
            stageName: customStageName.valueAsString,
            deployment: deployment,
            dataTraceEnabled: true,
            loggingLevel: MethodLoggingLevel.INFO,
        });
        deployment.node.addDependency(nestedsrFeature);
        this.addFeature(nestedsrFeature, 'Super Resolution', 'yes', deployment);
    }

    private addFeature(featureStack: FeatureNestedStack, featureName: string, defaultInstall: string, apiDeployment: Deployment) {
        const featureParameter = new CfnParameter(this, "InstallSuperResolutionFeature", {
            default: defaultInstall,
            type: 'String',
            description: `Install ${featureName} Feature?`,
            allowedValues: ['yes', 'no']
        });
        const featureCondition = new CfnCondition(
            this,
            'featureCondition',
            {
                expression: Fn.conditionEquals(featureParameter, 'yes')
            }
        );
        (featureStack.nestedStackResource as CfnStack).cfnOptions.condition = featureCondition;
        apiDeployment.node.addDependency(featureStack);
    }
}
