import { CustomResource, Duration, RemovalPolicy } from 'aws-cdk-lib';
import {
  AuthorizationType, Deployment, LambdaIntegration, RestApi,
} from 'aws-cdk-lib/aws-apigateway';
import { Repository } from 'aws-cdk-lib/aws-ecr';
import {
  ManagedPolicy,
  Role,
  ServicePrincipal,
} from 'aws-cdk-lib/aws-iam';
import { DockerImageCode, DockerImageFunction } from 'aws-cdk-lib/aws-lambda';
import { Provider } from 'aws-cdk-lib/custom-resources';
import { Construct } from 'constructs';
import { ECRDeployment } from '../lib/cdk-ecr-deployment/lib';

export interface LambdaFeatureProps {
  readonly featureName: string;
  readonly rootRestApi: RestApi;
  readonly restApiResourcePath: string;
  readonly featureCategory?: string;

  /**
    //  * @default AuthorizationType.NONE
     */
  readonly authorizationType?: AuthorizationType;

  readonly updateCustomResourceProvider: Provider;

  readonly lambdaEcrDeployment?: ECRDeployment;

  /**
     * @default Duration.seconds(19)
     */
  readonly lambdaTimeout?: Duration;

  /**
     * @default 8192
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
    Repository.fromRepositoryName(this, `ai-solution-kit-${props.featureName}Repository`, `ai-solution-kit-${props.featureName}`);
    const stackRepo = new Repository(this, `ai-solution-kit-${props.featureName}`, {
      repositoryName: `ai-solution-kit-${props.featureName}`,
      removalPolicy: RemovalPolicy.RETAIN,
    });

    if (props.lambdaEcrDeployment != null) {
      // Lambda deployment
      const ecrCR = new CustomResource(this, `${props.featureName}Ecr`, {
        serviceToken: props.lambdaEcrDeployment.serviceToken,
        resourceType: 'Custom::AISolutionKitECRLambda',
        properties: {
          SrcImage: `docker://${props.lambdaDockerImageUrl}`,
          DestImage: `docker://${stackRepo.repositoryUri}`,
          RepositoryName: `${stackRepo.repositoryName}`,
        },
      });
      const myRole = new Role(this, `${props.featureName}Role`, {
        assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
      });
      const appFunction = new DockerImageFunction(
        this,
        `${props.featureName}App`,
        {
          code: DockerImageCode.fromEcr(
            Repository.fromRepositoryName(this, `${props.featureName}Lambda`, stackRepo.repositoryName),
            {
              tag: props.lambdaDockerImageTag,
            },
          ),
          timeout: props.lambdaTimeout,
          memorySize: props.lambdaMemorySize,
          role: myRole,
        },
      );
      myRole.addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'));
      myRole.addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName('AmazonS3ReadOnlyAccess'));
      appFunction.node.addDependency(ecrCR);
      // const lambdaInt = new LambdaIntegration(appFunction, { proxy: true });
      const rootRestApi = RestApi.fromRestApiAttributes(this, 'client-api', {
        restApiId: props.rootRestApi.restApiId,
        rootResourceId: props.rootRestApi.root.resourceId,
      });
      const deployment = new Deployment(this, `${props.featureName}Deployment`, {
        api: rootRestApi,
        retainDeployments: true,
      });
      const resource = rootRestApi.root.addResource(props.restApiResourcePath);
      const post = resource.addMethod('POST', new LambdaIntegration(appFunction, { proxy: true }), {
        authorizationType: props.authorizationType,
      });
      // const methodResource = post.node.findChild('Resource') as CfnMethod;
      // methodResource.addPropertyOverride('AuthorizationType', props.authorizationType);
      // rootRestApi.latestDeployment
      // const deployment = new Deployment(this, 'Deployment', {
      //     api: rootRestApi,
      // });
      const apiProvider = new CustomResource(this, `${props.featureName}Api`, {
        serviceToken: props.updateCustomResourceProvider.serviceToken,
        resourceType: 'Custom::AISolutionKitApiProvider',
        properties: {
          featureName: props.featureName,
          authorizationType: props.authorizationType,
        },
        removalPolicy: RemovalPolicy.DESTROY,
      });
      apiProvider.node.addDependency(post);
      // deployment.node.addDependency(apiProvider);
    }
  }
}
