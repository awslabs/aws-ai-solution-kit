import {
  CfnOutput,
  CfnParameter,
  aws_apigateway as apigw,
  aws_iam as iam,

} from 'aws-cdk-lib';
import { AwsIntegrationProps } from 'aws-cdk-lib/aws-apigateway';
import { Construct } from 'constructs';

export class RestApiGateway {
  public readonly apiGateway: apigw.RestApi;
  public readonly apiKey: string;

  private readonly scope: Construct;

  constructor(scope: Construct) {
    this.scope = scope;
    [this.apiGateway, this.apiKey] = this.createApigw();
  }

  private createApigw(): [apigw.RestApi, string] {
    const apiKeyParam = new CfnParameter(this.scope, 'sd-extension-api-key', {
      type: 'String',
      description: 'API Key for Stable Diffusion extension',
      // API Key value should be at least 20 characters
      default: '09876543210987654321',
    });

    // Create an API Gateway, will merge with existing API Gateway
    const api = new apigw.RestApi(this.scope, 'train-deploy-api', {
      restApiName: 'Stable Diffusion Train and Deploy API',
      description:
                'This service is used to train and deploy Stable Diffusion models.',
    });

    // Output the API Gateway URL
    new CfnOutput(this.scope, 'train-deploy-api-url', {
      value: api.url,
    });

    return [api, apiKeyParam.valueAsString];
  }
}

export interface SagemakerTrainApiProps {
  api: apigw.RestApi;
  stateMachineArn: string;
  apiKey: string;
  apiResource: string;
}

export class SagemakerTrainApi {
  private readonly scope: Construct;

  constructor(scope: Construct, props: SagemakerTrainApiProps) {
    this.scope = scope;
    this.trainApi(props.api, props.stateMachineArn, props.apiKey, props.apiResource);
  }

  private credentialsRole(stateMachineArn: string): iam.Role {
    const credentialsRole = new iam.Role(this.scope, 'getRole', {
      assumedBy: new iam.ServicePrincipal('apigateway.amazonaws.com'),
    });

    credentialsRole.attachInlinePolicy(
      new iam.Policy(this.scope, 'getPolicy', {
        statements: [
          new iam.PolicyStatement({
            // Access to trigger the Step Function
            actions: ['states:StartExecution'],
            effect: iam.Effect.ALLOW,
            resources: [stateMachineArn],
          }),
        ],
      }),
    );
    return credentialsRole;
  }

  // Add a POST method with prefix train-deploy and integration with Step Function
  private trainApi(api: apigw.RestApi, stateMachineArn: string, apiKey: string, apiResource: string) {

    const trainDeploy = api.root.addResource(apiResource);

    const trainDeployIntegration = new apigw.AwsIntegration(<AwsIntegrationProps>{
      service: 'states',
      action: 'StartExecution',
      options: {
        credentialsRole: this.credentialsRole(stateMachineArn),
        passthroughBehavior: apigw.PassthroughBehavior.NEVER,
        requestTemplates: {
          'application/json': `{
            "input": "{\\"actionType\\": \\"create\\", \\"JobName\\": \\"$context.requestId\\", \\"S3Bucket_Train\\": \\"$input.params('S3Bucket_Train')\\", \\"S3Bucket_Output\\": \\"$input.params('S3Bucket_Output')\\", \\"InstanceType\\": \\"$input.params('InstanceType')\\"}",
            "stateMachineArn": "${stateMachineArn}"
          }`,
        },
        integrationResponses: [
          {
            statusCode: '200',
            responseTemplates: {
              'application/json': '{"done": true}',
            },
          },
        ],
      },
    });

    trainDeploy.addMethod('POST', trainDeployIntegration, {
      apiKeyRequired: true,
      methodResponses: [{ statusCode: '200' }],
    });

    // Add API Key to the API Gateway
    api.addApiKey('sd-extension-api-key', {
      apiKeyName: 'sd-extension-api-key',
      value: apiKey,
    });
  }
}