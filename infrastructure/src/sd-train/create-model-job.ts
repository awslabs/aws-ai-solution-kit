import { PythonFunction, PythonFunctionProps } from '@aws-cdk/aws-lambda-python-alpha';
import { aws_apigateway as apigw, aws_dynamodb, aws_iam, aws_lambda, aws_s3, Duration } from 'aws-cdk-lib';
import { MethodOptions } from 'aws-cdk-lib/aws-apigateway/lib/method';
import { Effect } from 'aws-cdk-lib/aws-iam';
import { Architecture, Runtime } from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';


export interface CreateModelJobApiProps {
  apiGateway: apigw.RestApi;
  trainingTable: aws_dynamodb.Table;
  apiResource: string;
  srcRoot: string;
  s3Bucket: aws_s3.Bucket;
  commonLayer: aws_lambda.LayerVersion;
}

export class CreateModelJobApi {
  private readonly src;
  private readonly scope: Construct;
  private readonly apiGateway: apigw.RestApi;
  private readonly trainingTable: aws_dynamodb.Table;
  private readonly apiResource: string;
  private readonly s3Bucket: aws_s3.Bucket;
  private readonly layer: aws_lambda.LayerVersion;

  constructor(scope: Construct, props: CreateModelJobApiProps) {
    this.scope = scope;
    this.apiGateway = props.apiGateway;
    this.trainingTable = props.trainingTable;
    this.apiResource = props.apiResource;
    this.src = props.srcRoot;
    this.s3Bucket = props.s3Bucket;
    this.layer = props.commonLayer;

    this.createModelJobApi();
  }

  private iamRole(): aws_iam.Role {
    const newRole = new aws_iam.Role(this.scope, 'aigc-create-model-role', {
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
        's3:GetObject',
        's3:PutObject',
      ],
      resources: [`${this.s3Bucket.bucketArn}/*`],
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

  private createModelJobApi() {
    const createModelApi = this.apiGateway.root.addResource(this.apiResource);

    const createModelIntegration = new apigw.LambdaIntegration(
      new PythonFunction(this.scope, 'aigc-create-model-handler', <PythonFunctionProps>{
        functionName: 'aigc-midware-create-model',
        entry: `${this.src}/create_model`,
        architecture: Architecture.X86_64,
        runtime: Runtime.PYTHON_3_9,
        index: 'handler.py',
        handler: 'handler',
        timeout: Duration.seconds(900),
        role: this.iamRole(),
        memorySize: 1024,
        environment: {
          DYNAMODB_TABLE: this.trainingTable.tableName,
          S3_BUCKET: this.s3Bucket.bucketName,
        },
        layers: [this.layer],
      }),
      {
        proxy: false,
        integrationResponses: [{ statusCode: '200' }],
      },
    );
    createModelApi.addMethod('POST', createModelIntegration, <MethodOptions>{
      apiKeyRequired: true,
      methodResponses: [{
        statusCode: '200',
      }],
    });
  }
}