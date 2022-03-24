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
import * as ecrDeploy from 'cdk-ecr-deployment';


export class OCRBusinessLicenseSolutionECRStack extends Stack {
    constructor(scope: Construct, id: string, props?: StackProps) {

        super(scope, id, props);
        this.templateOptions.description = `(SO8023-ocr) - AI Solution Kits - OCR for China Business License. Template version v1.0.0`;

        const customStageName = new CfnParameter(this, "customStageName", {
            default: 'prod',
            type: 'String',
            description: `Custom Stage Name, default value is: prod`
        });

        const customResourceName = new CfnParameter(this, "customResourceName", {
            default: 'business_license',
            type: 'String',
            description: 'Custom Stage Name, default value is: business_license'
        });

        const customAuthType = new CfnParameter(this, "customAuthType", {
            default: 'AWS_IAM',
            type: 'String',
            description: `Custom Authorization Type, default value is: AWS_IAM`,
            allowedValues: ['NONE', 'AWS_IAM']
        });

        const sec = new SolutionEcrConstruct(this, "OCRBusinessLicenseSolutionConstruct")
        /**
          * Lambda Provision
          */
        const ocrLicenseImage = new DockerImageFunction(
            this,
            'ocrLicenseImage',
            {
                code: DockerImageCode.fromEcr(
                    Repository.fromRepositoryName(this, 'ocrBusinessLicenseImage', 'ai-solution-kit-ocr-business-license'),
                    {
                        tag: '1.0.0'
                    }
                ),
                timeout: Duration.seconds(15),
                memorySize: 10240,
            }
        );
        ocrLicenseImage.node.addDependency(sec)
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

        const post = ocrBusinessLicenseApi.root.addResource(customStageName.valueAsString).addMethod('POST', new LambdaIntegration(ocrLicenseImage), {
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
            `https://${post.api.restApiId}.execute-api.${Aws.REGION}.amazonaws.com.cn/${customStageName.valueAsString}/${customResourceName.valueAsString}`,
            `https://${post.api.restApiId}.execute-api.${Aws.REGION}.amazonaws.com/${customStageName.valueAsString}/${customResourceName.valueAsString}`
        );
        new CfnOutput(this, 'InvokeURL', { value: invokeUrl.toString() });

        new CfnOutput(this, 'API Name', { value: ocrBusinessLicenseApi.restApiName });
    }
}

export class SolutionEcrConstruct extends Construct {

    public stackRepo: Repository

    constructor(scope: Construct, id: string) {
        super(scope, id);

        this.stackRepo = new Repository(this, 'ai-solution-kit-ocr-business-license', {
            repositoryName: 'ai-solution-kit-ocr-business-license',
            removalPolicy: RemovalPolicy.DESTROY,
        });

        const ecrImage = new ecrDeploy.ECRDeployment(this, 'ocrBusinessLicenseECR', {
            src: new ecrDeploy.DockerImageName('public.aws/aws-gcr-solutions/ai-solution-kit-ocr-business-license:1.0.0'),
            dest: new ecrDeploy.DockerImageName(`${this.stackRepo.repositoryUri}:latest`),
        });

    }
}
