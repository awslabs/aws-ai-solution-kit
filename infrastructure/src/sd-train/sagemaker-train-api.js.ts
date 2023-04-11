import { aws_apigateway as apigw, aws_iam as iam } from 'aws-cdk-lib';
import { AwsIntegrationProps } from 'aws-cdk-lib/aws-apigateway';
import { Construct } from 'constructs';

export interface SagemakerTrainApiProps {
  api: apigw.RestApi;
  stateMachineArn: string;
  apiResource: string;
}

export class SagemakerTrainApi {
  private readonly scope: Construct;

  constructor(scope: Construct, props: SagemakerTrainApiProps) {
    this.scope = scope;
    this.trainApi(props.api, props.stateMachineArn, props.apiResource);
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
  private trainApi(api: apigw.RestApi, stateMachineArn: string, apiResource: string) {

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
  }
}