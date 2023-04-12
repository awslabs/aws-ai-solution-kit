import { PythonFunction, PythonFunctionProps } from '@aws-cdk/aws-lambda-python-alpha';
import { aws_apigateway as apigw, aws_dynamodb, aws_iam, aws_lambda, Duration } from 'aws-cdk-lib';
import { MethodOptions } from 'aws-cdk-lib/aws-apigateway/lib/method';
import { Resource } from 'aws-cdk-lib/aws-apigateway/lib/resource';
import { Effect } from 'aws-cdk-lib/aws-iam';
import { Architecture, Runtime } from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';

export interface UpdateModelStatusRestApiProps {
  httpMethod: string;
  router: Resource;
  trainingTable: aws_dynamodb.Table;
  srcRoot: string;
  commonLayer: aws_lambda.LayerVersion;
}

export class UpdateModelStatusRestApi {

  private readonly src;
  private readonly scope: Construct;
  private readonly trainingTable: aws_dynamodb.Table;
  private readonly layer: aws_lambda.LayerVersion;
  private readonly router: Resource;
  private readonly httpMethod: string;

  private readonly baseId = 'aigc-update-train-job';

  constructor(scope: Construct, props: UpdateModelStatusRestApiProps) {
    this.scope = scope;
    this.router = props.router;
    this.trainingTable = props.trainingTable;
    this.httpMethod = props.httpMethod;
    this.src = props.srcRoot;
    this.layer = props.commonLayer;

    this.updateModelJobApi();
  }

  private iamRole(): aws_iam.Role {
    const newRole = new aws_iam.Role(this.scope, `${this.baseId}-role`, {
      assumedBy: new aws_iam.ServicePrincipal('lambda.amazonaws.com'),
    });
    newRole.addToPolicy(new aws_iam.PolicyStatement({
      effect: Effect.ALLOW,
      actions: [
        'dynamodb:BatchGetItem',
        'dynamodb:GetItem',
        'dynamodb:Scan',
        'dynamodb:Query',
        'dynamodb:BatchWriteItem',
        'dynamodb:PutItem',
        'dynamodb:UpdateItem',
        'dynamodb:DeleteItem',
      ],
      resources: [this.trainingTable.tableArn],
    }));

    newRole.addToPolicy(new aws_iam.PolicyStatement({
      effect: Effect.ALLOW,
      actions: [
        'logs:CreateLogGroup',
        'logs:CreateLogStream',
        'logs:PutLogEvents',
      ],
      resources: ['*'],
    }));
    return newRole;
  }

  private updateModelJobApi() {

    const updateModelLambdaIntegration = new apigw.LambdaIntegration(
      new PythonFunction(this.scope, `${this.baseId}-handler`, <PythonFunctionProps>{
        functionName: `${this.baseId}-model`,
        entry: `${this.src}/create_model`,
        architecture: Architecture.X86_64,
        runtime: Runtime.PYTHON_3_9,
        index: 'update_job_api.py',
        handler: 'update_train_job_api',
        timeout: Duration.seconds(900),
        role: this.iamRole(),
        memorySize: 1024,
        environment: {
          DYNAMODB_TABLE: this.trainingTable.tableName,
        },
        layers: [this.layer],
      }),
      {
        proxy: false,
        integrationResponses: [{ statusCode: '200' }],
      },
    );
    this.router.addMethod(this.httpMethod, updateModelLambdaIntegration, <MethodOptions>{
      apiKeyRequired: true,
      methodResponses: [{
        statusCode: '200',
      }],
    });
  }
}