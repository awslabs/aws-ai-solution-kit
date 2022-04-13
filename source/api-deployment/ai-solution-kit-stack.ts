import {
    AuthorizationType, Cors, Deployment, EndpointType, MethodLoggingLevel, RestApi, Stage
} from '@aws-cdk/aws-apigateway';
import * as iam from '@aws-cdk/aws-iam';
import { Code, Function, Runtime } from '@aws-cdk/aws-lambda';
import {
    Aws, CfnCondition, CfnOutput, CfnParameter, CfnStack, Construct, Duration, Fn, Stack,
    StackProps
} from "@aws-cdk/core";
import { Provider } from '@aws-cdk/custom-resources';
import * as path from 'path';
// import { SegNestedStack } from './features/nest-seg';
import { DockerImageName, ECRDeployment } from '../lib/cdk-ecr-deployment/lib';
import { FeatureNestedStack } from './feature-nested-stack';
import { GeneralOCRFeatureNestedStack } from './features/general-ocr-feature';
// import { InferOCRNestedStack } from './features/archieve/nest-ocr';
// import { SRNestedStack } from './features/nest-sr';
import { SuperResolutionFeatureNestedStack } from './features/super-resolution-feature';
import { SuperResolutionGpuFeatureNestedStack } from './features/super-resolution-gpu-feature';
import { SuperResolutionInf1FeatureNestedStack } from './features/super-resolution-inf1-feature';
import { ApiDocsNestedStack } from './nest-api-docs';

// all new, create CR, run CR in each nested stack, if Yes
// deployed, update stack, run CR in each nested stack(change Y/N param), let CR to add or delete resources by new Yes/No
// New feat, CF changed, new feat should be list in CF stack, it should not effect old ones, it operates the old API GW, r

export interface FeatureProps {
    readonly featureStack: FeatureNestedStack;
    readonly title: string;
    readonly description: string;
    readonly defaultInstall: string;
    readonly sageMakerInstanceTypes?: string[];
}

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

        const apiLambda = new Function(this, `apihandler`, {
            handler: 'api_resource.lambda_handler',
            runtime: Runtime.PYTHON_3_9,
            code: Code.fromAsset(path.join(__dirname, '../lib/api_resource'), {
                bundling: {
                    image: Runtime.PYTHON_3_9.bundlingImage,
                    command: [
                        'bash', '-c', [
                            `cp -r /asset-input/* /asset-output/`,
                            `pip install -r requirements.txt --no-cache-dir --target /asset-output`
                        ].join(' && ')
                    ],
                }
            }),
            memorySize: 2048,
            timeout: Duration.minutes(1),
            environment: {
                REST_API_ID: api.restApiId,
                STAGE_NAME: customStageName.valueAsString,
                CUSTOM_AUTH_TYPE: customAuthType.valueAsString
            }
        });

        const updateCustomResourceProvider = new Provider(this, `apiprovider`, {
            onEventHandler: apiLambda,
        });

        apiLambda.addToRolePolicy(
            new iam.PolicyStatement({
                effect: iam.Effect.ALLOW,
                actions: [
                    "apigateway:*"
                ],
                resources: ['*']
            })
        );

        new CfnOutput(this, 'AISolutionKitStack CfnOutput', { value: 'AISolutionKitStack CfnOutput' });

        // const cfnTemplate = new CfnInclude(this, 'OCRTemplate', {
        //     templateFile: path.join(__dirname, 'conditional.template'),
        //     parameters: {
        //         'apiLambdaArn': apiLambda.functionArn,
        //         'CustomResourceServiceToken': updateProvider.serviceToken
        //     }
        // });

        // const sec = new SolutionEcrConstruct(this, "ocrEcr")
        // console.log(sec.ecrDeployment.serviceToken)

        const ecrDeployment = new ECRDeployment(this, 'ai-solution-kit-deployment', {
            src: new DockerImageName(''),
            dest: new DockerImageName(''),
        });

        const authType = `${customAuthType.valueAsString}` as AuthorizationType;

        const deployment = new Deployment(this, 'new_deployment', {
            api: api,
            // retainDeployments: true,
        });

        const deploymentStage = new Stage(this, 'ai-solution-kit-prod', {
            stageName: customStageName.valueAsString,
            deployment: deployment,
            dataTraceEnabled: true,
            loggingLevel: MethodLoggingLevel.INFO,
        });

        new CfnCondition(this,
            'IsChinaRegionCondition',
            { expression: Fn.conditionEquals(Aws.PARTITION, 'aws-cn') });

        const invokeUrl = Fn.conditionIf(
            'IsChinaRegionCondition',
            `https://${api.restApiId}.execute-api.${Aws.REGION}.amazonaws.com.cn/${customStageName.valueAsString}`,
            `https://${api.restApiId}.execute-api.${Aws.REGION}.amazonaws.com/${customStageName.valueAsString}`
        );

        // Feature: API Docs
        const apiDocs = new ApiDocsNestedStack(this, "api-docs", {
            restApi: api,
            invokeUrl: invokeUrl.toString(),
            authorizationType: customAuthType.valueAsString
        });
        this.addLambdaFeature({
            featureStack: apiDocs,
            title: 'API Docs',
            defaultInstall: 'yes',
            description: 'Do you want to install API Docs.',
        });

        // Feature: Super Resolution
        const superResolution = new SuperResolutionFeatureNestedStack(this, 'srFeat', {
            restApi: api,
            customAuthorizationType: authType,
            ecrDeployment: ecrDeployment,
            updateCustomResourceProvider: updateCustomResourceProvider,
        });

        this.addLambdaFeature({
            featureStack: superResolution,
            title: 'Super-Resolution',
            defaultInstall: 'no',
            description: 'Do you want to install photo super resolution feature. You can find out more about photo super resolution at https://www.amazonaws.cn/solutions/ai-solution-kit/super-resolution',
        });

        // Feature: General OCR Standard
        const generalOCR = new GeneralOCRFeatureNestedStack(this, 'ocrFeat', {
            restApi: api,
            customAuthorizationType: authType,
            ecrDeployment: ecrDeployment,
            updateCustomResourceProvider: updateCustomResourceProvider,
        });

        this.addLambdaFeature({
            featureStack: generalOCR,
            title: 'General-OCR',
            defaultInstall: 'no',
            description: 'Do you want to install general OCR feature. You can find out more about general OCR at https://www.amazonaws.cn/solutions/ai-solution-kit/general-ocr.',
        });

        // Feature: Super Resolution GPU
        const srGpuType = new CfnParameter(this, 'Super-Resolution-GPU-Instance', {
            description: 'Do you want to install photo super resolution GPU feature. You can find out more about photo super resolution GPU at https://www.amazonaws.cn/solutions/ai-solution-kit/general-ocr.',
            type: 'String',
            default: 'no',
            allowedValues: [
                'no',
                'ml.g4dn.xlarge',
                'ml.g4dn.2xlarge',
                'ml.g4dn.8xlarge'
            ]
        });

        const srGpuCondition = new CfnCondition(
            this,
            `srGpuCondition`,
            {
                expression: Fn.conditionNot(Fn.conditionEquals(srGpuType, 'no'))
            }
        );

        const superResolutionGpu = new SuperResolutionGpuFeatureNestedStack(this, 'srGpu', {
            restApi: api,
            customAuthorizationType: authType,
            updateCustomResourceProvider: updateCustomResourceProvider,
            instanceType: srGpuType.valueAsString
        });

        (superResolutionGpu.nestedStackResource as CfnStack).cfnOptions.condition = srGpuCondition;


        // Feature: Super Resolution Inf1
        const srInf1Type = new CfnParameter(this, 'Super-Resolution-Inf1-Instance', {
            description: 'Do you want to install photo super resolution Inf1 feature. You can find out more about photo super resolution GPU at https://www.amazonaws.cn/solutions/ai-solution-kit/general-ocr.',
            type: 'String',
            default: 'no',
            allowedValues: [
                'no',
                'ml.inf1.xlarge',
                'ml.inf1.2xlarge',
                'ml.inf1.6xlarge'
            ]
        });

        const srInf1Condition = new CfnCondition(
            this,
            `srInf1Condition`,
            {
                expression: Fn.conditionNot(Fn.conditionEquals(srInf1Type, 'no'))
            }
        );

        const superResolutionInf1 = new SuperResolutionInf1FeatureNestedStack(this, 'srInf1', {
            restApi: api,
            customAuthorizationType: authType,
            updateCustomResourceProvider: updateCustomResourceProvider,
            instanceType: srInf1Type.valueAsString
        });
        (superResolutionInf1.nestedStackResource as CfnStack).cfnOptions.condition = srInf1Condition;
        // this.addSageMakerFeature({
        //     featureStack: superResolutionInf1,
        //     title: 'Super-Resolution-Inf1',
        //     defaultInstall: 'no',
        //     sageMakerInstanceTypes: [
        //         'ml.inf1.xlarge',
        //         'ml.inf1.2xlarge',
        //         'ml.inf1.6xlarge'
        //     ],
        //     description: 'Do you want to install photo super resolution Inf1 feature. You can find out more about photo super resolution GPU at https://www.amazonaws.cn/solutions/ai-solution-kit/general-ocr.',
        // });
    }

    private addLambdaFeature(props: FeatureProps) {
        const featureParameter = new CfnParameter(this, `Install-${props.title}`, {
            default: props.defaultInstall,
            type: 'String',
            description: props.description,
            allowedValues: ['yes', 'no']
        });
        const featureCondition = new CfnCondition(
            this,
            `${props.title}condition`,
            {
                expression: Fn.conditionEquals(featureParameter, 'yes')
            }
        );
        (props.featureStack.nestedStackResource as CfnStack).cfnOptions.condition = featureCondition;
    }

    // private addSageMakerFeature(props: FeatureProps) {
    //     props.sageMakerInstanceTypes?.push('no');
    //     const featureParameter = new CfnParameter(this, `Install-${props.title}`, {
    //         default: props.defaultInstall,
    //         type: 'String',
    //         description: props.description,
    //         allowedValues: props.sageMakerInstanceTypes
    //     });
    //     const featureCondition = new CfnCondition(
    //         this,
    //         `${props.title}condition`,
    //         {
    //             expression: Fn.conditionNot(Fn.conditionEquals(featureParameter, 'no'))
    //         }
    //     );
    //     (props.featureStack.nestedStackResource as CfnStack).cfnOptions.condition = featureCondition;
    // }
}
