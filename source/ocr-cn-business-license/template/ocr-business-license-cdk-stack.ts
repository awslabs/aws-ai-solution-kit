import {
    AuthorizationType, CfnMethod, Cors, Deployment, EndpointType,
    LambdaIntegration, Method, MethodLoggingLevel, RestApi, Stage
} from '@aws-cdk/aws-apigateway';
import { Repository } from "@aws-cdk/aws-ecr";
import { DockerImageCode, DockerImageFunction } from "@aws-cdk/aws-lambda";
import {
    Aws, CfnCondition, CfnOutput, CfnParameter, Construct, Duration, Fn, RemovalPolicy, Stack,
    StackProps
} from "@aws-cdk/core";


export class OCRBusinessLicenseSolutionCDKStack extends Stack {
    constructor(scope: Construct, id: string, props?: StackProps) {

        super(scope, id, props);
        this.templateOptions.description = `(SO8023-ocr) - AI Solution Kits - OCR for China Business License. Template version v1.0.0`;

        const customStageName = new CfnParameter(this, "customStageName", {
            default: 'prod',
            type: 'String',
            description: `Custom Stage Name, default value is: prod`
        });

        const customAuthType = new CfnParameter(this, "customAuthType", {
            default: 'AWS_IAM',
            type: 'String',
            description: `Custom Authorization Type, default value is: AWS_IAM`,
            allowedValues: ['NONE', 'AWS_IAM']
        });

        /**
          * Lambda Provision
          */
        const ocrLicenseImage = new DockerImageFunction(
            this,
            'OCRBusinessLicense',
            {
                code: DockerImageCode.fromImageAsset('source/ocr-cn-business-license/model'),
                timeout: Duration.seconds(15),
                memorySize: 10240,
                environment: {
                    LICENSE_ID: 'true',
                    COMPANY_NAME: 'true',
                    DURATION: 'true',
                    MODEL_NAME: 'standard_cn_business_license',
                    MODEL_PATH: '/opt/program/model/',
                    REFERECNE_SCORE: '0.90',
                    AUTO_ROTATION: 'true',
                    ENHANCE_MODE: 'true',
                    DENOISING_MODE: 'true'
                }
            }
        );

        /**
         * API Gateway Provision
         */
        const ocrBusinessLicenseApi = new RestApi(
            this,
            'ocrBusinessLicenseRouter',
            {
                restApiName: 'ocrBusinessLicenseApi',
                deploy: false,
                endpointConfiguration: {
                    types: [EndpointType.REGIONAL]
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
                    allowOrigins: Cors.ALL_ORIGINS,
                }
            }
        );

        const deployment = new Deployment(this, 'ocrBusinessLicenseDeployment', {
            api: ocrBusinessLicenseApi,
        });

        ocrBusinessLicenseApi.deploymentStage = new Stage(this, 'ocrBusinessLicenseStage', {
            stageName: customStageName.valueAsString,
            deployment,
            dataTraceEnabled: true,
            loggingLevel: MethodLoggingLevel.INFO,
        });

        const post = ocrBusinessLicenseApi.root.addResource('business-license').addMethod('POST', new LambdaIntegration(ocrLicenseImage), {
            authorizationType: AuthorizationType.IAM,
        }) as Method;

        const methodResource = post.node.findChild('Resource') as CfnMethod
        methodResource.addPropertyOverride('AuthorizationType', customAuthType.valueAsString)

        ocrBusinessLicenseApi.node.addDependency(ocrLicenseImage)

        new CfnOutput(this, 'InvokeURLArn', { value: post.methodArn });

        const inCnCondition = new CfnCondition(this,
            'IsChinaRegionCondition',
            { expression: Fn.conditionEquals(Aws.PARTITION, 'aws-cn') });
        const invokeUrl = Fn.conditionIf(
            inCnCondition.logicalId,
            `https://${post.api.restApiId}.execute-api.${Aws.REGION}.amazonaws.com.cn/${customStageName.valueAsString}/business-license`,
            `https://${post.api.restApiId}.execute-api.${Aws.REGION}.amazonaws.com/${customStageName.valueAsString}/business-license`
        );
        new CfnOutput(this, 'InvokeURL', { value: invokeUrl.toString() });

        new CfnOutput(this, 'API Name', { value: ocrBusinessLicenseApi.restApiName });
    }
}
