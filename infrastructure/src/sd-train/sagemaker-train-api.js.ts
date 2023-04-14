import { aws_apigateway as apigw, aws_iam as iam } from 'aws-cdk-lib';
import { AwsIntegrationProps } from 'aws-cdk-lib/aws-apigateway';
import { Resource } from 'aws-cdk-lib/aws-apigateway/lib/resource';
import { Construct } from 'constructs';

export interface SagemakerTrainApiProps {
  stateMachineArn: string;
  router: Resource;
  httpMethod: string;
}

export class SagemakerTrainApi {
  private readonly scope: Construct;
  private readonly stateMachineArn: string;
  private readonly router: Resource;
  private readonly httpMethod: string;

  constructor(scope: Construct, props: SagemakerTrainApiProps) {
    this.scope = scope;
    this.stateMachineArn = props.stateMachineArn;
    this.router = props.router;
    this.httpMethod = props.httpMethod;

    this.trainApi();
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
  private trainApi() {
    const trainDeployIntegration = new apigw.AwsIntegration(<AwsIntegrationProps>{
      service: 'states',
      action: 'StartExecution',
      options: {
        credentialsRole: this.credentialsRole(this.stateMachineArn),
        passthroughBehavior: apigw.PassthroughBehavior.NEVER,
        requestTemplates: {
          'application/json': `{
            "input": "{\\"actionType\\": \\"create\\", \\"JobName\\": \\"$context.requestId\\", \\"S3Bucket_Train\\": \\"$input.params('S3Bucket_Train')\\", \\"S3Bucket_Output\\": \\"$input.params('S3Bucket_Output')\\", \\"InstanceType\\": \\"$input.params('InstanceType')\\"}",
            "stateMachineArn": "${this.stateMachineArn}"
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

    this.router.addMethod(this.httpMethod, trainDeployIntegration, {
      apiKeyRequired: true,
      methodResponses: [{ statusCode: '200' }],
    });
  }
}