import { Aws, CfnCondition, CfnOutput, CustomResource, Fn, RemovalPolicy } from 'aws-cdk-lib';
import { AuthorizationType, AwsIntegration, Deployment, RestApi } from 'aws-cdk-lib/aws-apigateway';
import { Effect, ManagedPolicy, PolicyDocument, PolicyStatement, Role, ServicePrincipal } from 'aws-cdk-lib/aws-iam';
import { CfnEndpoint, CfnEndpointConfig, CfnModel } from 'aws-cdk-lib/aws-sagemaker';
import { Provider } from 'aws-cdk-lib/custom-resources';
import { Construct } from 'constructs';

export interface SageMakerFeatureProps {
  readonly featureName: string;
  readonly rootRestApi: RestApi;
  readonly restApiResourcePath: string;
  readonly featureCategory?: string;

  /**
     * @default AuthorizationType.IAM
     */
  readonly authorizationType?: AuthorizationType;
  readonly updateCustomResourceProvider: Provider;
  readonly sageMakerInstanceType: string;
  // readonly sageMakerDefaultInstanceType?: string;
  readonly sageMakerDockerImageUrl?: string;
  readonly sageMakerDockerImageUrlCN?: string;
  readonly sageMakerDockerImageTag?: string;
}

export class SageMakerFeatureConstruct extends Construct {

  constructor(scope: Construct, id: string, props: SageMakerFeatureProps) {

    super(scope, id);

    const sagemakerExecuteRole = new Role(
      this,
      'sagemakerExecuteRole',
      {
        assumedBy: new ServicePrincipal('sagemaker.amazonaws.com'),
        managedPolicies: [
          ManagedPolicy.fromAwsManagedPolicyName('AmazonS3FullAccess'),
          ManagedPolicy.fromAwsManagedPolicyName('AmazonEC2ContainerRegistryFullAccess'),
          ManagedPolicy.fromAwsManagedPolicyName('CloudWatchLogsFullAccess'),
        ],
      },
    );

    new CfnCondition(this,
      'IsChinaRegionCondition',
      { expression: Fn.conditionEquals(Aws.PARTITION, 'aws-cn') });

    // configure container image name
    const imageUrl = Fn.conditionIf(
      'IsChinaRegionCondition',
      props.sageMakerDockerImageUrlCN,
      props.sageMakerDockerImageUrl,
    );

    // create model
    const sagemakerEndpointModel = new CfnModel(
      this,
      'sagemakerEndpointModel',
      {
        executionRoleArn: sagemakerExecuteRole.roleArn,
        containers: [
          {
            image: imageUrl.toString(),
            mode: 'SingleModel',
            environment: {},
          },
        ],
      },
    );

    // create endpoint configuration
    const sagemakerEndpointConfig = new CfnEndpointConfig(
      this,
      'sagemakerEndpointConfig',
      {
        productionVariants: [{
          initialInstanceCount: 1,
          initialVariantWeight: 1,
          instanceType: props.sageMakerInstanceType,
          modelName: sagemakerEndpointModel.attrModelName,
          variantName: 'AllTraffic',
        }],
      },
    );

    // create endpoint
    const sagemakerEndpoint = new CfnEndpoint(
      this,
      'sagemakerEndpoint',
      {
        endpointName: props.featureName,
        endpointConfigName: sagemakerEndpointConfig.attrEndpointConfigName,
      },
    );

    const policyResource = Fn.conditionIf(
      'IsChinaRegionCondition',
      `arn:aws-cn:sagemaker:${Aws.REGION}:${Aws.ACCOUNT_ID}:endpoint/${sagemakerEndpoint.endpointName}`,
      `arn:aws:sagemaker:${Aws.REGION}:${Aws.ACCOUNT_ID}:endpoint/${sagemakerEndpoint.endpointName}`,
    );

    const apiGatewayAccessToSageMakerRole = new Role(
      this,
      'apiGatewayAccessToSageMakerRole',
      {
        assumedBy: new ServicePrincipal('apigateway.amazonaws.com'),
        managedPolicies: [ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonAPIGatewayPushToCloudWatchLogs')],
        inlinePolicies: {
          SageMakerEndpointInvokeAccess: new PolicyDocument({
            statements: [new PolicyStatement({
              actions: ['sagemaker:InvokeEndpoint'],
              resources: [policyResource.toString()],
              effect: Effect.ALLOW,
            })],
          }),
        },
      });

    const sageMakerIntegration = new AwsIntegration({
      service: 'runtime.sagemaker',
      region: `${Aws.REGION}`,
      path: `endpoints/${sagemakerEndpoint.endpointName}/invocations`,
      integrationHttpMethod: 'POST',
      options: {
        credentialsRole: apiGatewayAccessToSageMakerRole,
        integrationResponses: [
          {
            statusCode: '200',
          },
        ],
      },
    });

    const rootRestApi = RestApi.fromRestApiAttributes(this, 'client-api', {
      restApiId: props.rootRestApi.restApiId,
      rootResourceId: props.rootRestApi.root.resourceId,
    });
    const updateProvider = new CustomResource(this, 'updateProvider', {
      serviceToken: props.updateCustomResourceProvider.serviceToken,
      resourceType: 'Custom::AISolutionKitApiProvider',
      properties: {
        featureName: `${props.featureName}`,
        updateType: 'update',
      },
      removalPolicy: RemovalPolicy.RETAIN,
    });
    const deployment = new Deployment(this, 'new_deployment', {
      api: rootRestApi,
      retainDeployments: true,
    });
    const resource = rootRestApi.root.addResource(`${props.restApiResourcePath}-ml`);
    resource.node.addDependency(updateProvider);

    const post = resource.addMethod('POST',
      sageMakerIntegration,
      {
        authorizationType: props.authorizationType,
        methodResponses: [{ statusCode: '200' }],
      },
    );
    const apiProvider = new CustomResource(this, 'apiProvider', {
      serviceToken: props.updateCustomResourceProvider.serviceToken,
      resourceType: 'Custom::AISolutionKitApiProvider',
      properties: {
        featureName: `${props.featureName}`,
      },
      removalPolicy: RemovalPolicy.RETAIN,
    });
    apiProvider.node.addDependency(post);

    const invokeUrl = Fn.conditionIf(
      'IsChinaRegionCondition',
      `https://${post.api.restApiId}.execute-api.${Aws.REGION}.amazonaws.com.cn/-stage-/${props.restApiResourcePath}-ml`,
      `https://${post.api.restApiId}.execute-api.${Aws.REGION}.amazonaws.com/-stage-/${props.restApiResourcePath}-ml`,
    );
    new CfnOutput(this, `${props.featureName}-URL`, { value: invokeUrl.toString() });
  }
}
