import {
    AuthorizationType, Deployment, LambdaIntegration, RestApi
} from '@aws-cdk/aws-apigateway';
import { Repository } from "@aws-cdk/aws-ecr";
import { DockerImageCode, DockerImageFunction } from "@aws-cdk/aws-lambda";
import { Aws, CfnCondition, Construct, CustomResource, Duration, Fn, RemovalPolicy } from "@aws-cdk/core";
import { Provider } from '@aws-cdk/custom-resources';
import { ECRDeployment } from '../lib/cdk-ecr-deployment/lib';

export interface LambdaFeatureProps {
    readonly featureName: string;
    readonly rootRestApi: RestApi;
    readonly restApiResourcePath: string;
    readonly featureCategory?: string;

    /**
    //  * @default AuthorizationType.AWS_IAM
     */
    readonly authorizationType?: AuthorizationType;

    readonly updateCustomResourceProvider: Provider;

    readonly lambdaEcrDeployment?: ECRDeployment;

    /**
     * @default Duration.seconds(15)
     */
    readonly lambdaTimeout?: Duration;

    /**
     * @default 2048
     */
    readonly lambdaMemorySize?: number;
    readonly lambdaDockerImageUrl?: string;
    readonly lambdaDockerImageUrlCN?: string;

    /**
     * @default 'latest'
     */
    readonly lambdaDockerImageTag?: string;
}

export class LambdaFeatureConstruct extends Construct {

    constructor(scope: Construct, id: string, props: LambdaFeatureProps) {

        super(scope, id);

        const stackRepo = new Repository(this, `ai-solution-kit-${props.featureName}`, {
            repositoryName: `ai-solution-kit-${props.featureName}`,
            removalPolicy: RemovalPolicy.RETAIN,
        });

        if (props.lambdaEcrDeployment != null) {
            // Lambda deployment
            const ecrCR = new CustomResource(this, 'deployECRImage', {
                serviceToken: props.lambdaEcrDeployment.serviceToken,
                resourceType: 'Custom::AISolutionKitECRLambda',
                properties: {
                    SrcImage: `docker://${props.lambdaDockerImageUrl}`,
                    DestImage: `docker://${stackRepo.repositoryUri}`,
                    RepositoryName: `${stackRepo.repositoryName}`
                },
            });
            const appFunction = new DockerImageFunction(
                this,
                `${props.featureName}App`,
                {
                    code: DockerImageCode.fromEcr(
                        Repository.fromRepositoryName(this, `${props.featureName}Lambda`, stackRepo.repositoryName),
                        {
                            tag: props.lambdaDockerImageTag
                        }
                    ),
                    timeout: props.lambdaTimeout,
                    memorySize: props.lambdaMemorySize,
                }
            );
            appFunction.node.addDependency(ecrCR);
            // const lambdaInt = new LambdaIntegration(appFunction, { proxy: true });
            const rootRestApi = RestApi.fromRestApiAttributes(this, 'client-api', {
                restApiId: props.rootRestApi.restApiId,
                rootResourceId: props.rootRestApi.root.resourceId,
            });
            const deployment = new Deployment(this, 'new_deployment', {
                api: rootRestApi,
                retainDeployments: true
            });
            const resource = rootRestApi.root.addResource(props.restApiResourcePath);
            const post = resource.addMethod('POST', new LambdaIntegration(appFunction, { proxy: true }), {
                authorizationType: props.authorizationType
            });
            // const methodResource = post.node.findChild('Resource') as CfnMethod;
            // methodResource.addPropertyOverride('AuthorizationType', props.authorizationType);
            // rootRestApi.latestDeployment
            // const deployment = new Deployment(this, 'Deployment', {
            //     api: rootRestApi,
            // });
            const apiProvider = new CustomResource(this, `apiProvider`, {
                serviceToken: props.updateCustomResourceProvider.serviceToken,
                resourceType: "Custom::AISolutionKitApiProvider",
                properties: {
                    'featureName': `${props.featureName}`,
                },
                removalPolicy: RemovalPolicy.DESTROY,
            });
            apiProvider.node.addDependency(post);
        } else {
            // SageMaker deployment
        }
    }
}
