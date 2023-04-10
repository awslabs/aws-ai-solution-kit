import * as path from 'path';
import { aws_apigateway as apigw, aws_dynamodb, aws_lambda } from 'aws-cdk-lib';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';


export interface CreateModelJobApiProps {
  apiKey: string;
  apiGateway: apigw.RestApi;
  trainingTable: aws_dynamodb.Table;
  apiResource: string;
}

export class CreateModelJobApi {

  private readonly scope: Construct;
  private readonly apiGateway: apigw.RestApi;
  private readonly trainingTable: aws_dynamodb.Table;
  private readonly apiKey: string;
  private readonly apiResource: string;

  constructor(scope: Construct, props: CreateModelJobApiProps) {
    this.scope = scope;
    this.apiGateway = props.apiGateway;
    this.trainingTable = props.trainingTable;
    this.apiKey = props.apiKey;
    this.apiResource = props.apiResource;
  }

  private apiFunction(): aws_lambda.IFunction {
    return new aws_lambda.Function(this.scope, 'apigw-lambda-ddb-function', {
      functionName: 'apigw-lambda-ddb_function',
      runtime: aws_lambda.Runtime.NODEJS_16_X,
      handler: 'index.handler',
      description: 'playing function',
      code: aws_lambda.Code.fromAsset(path.join(__dirname, './lambda/playing_function')),
      logRetention: logs.RetentionDays.ONE_WEEK,
      environment: {
        DYNAMODB_TABLE: this.trainingTable.tableName,
      },
    });
  }

  private createModelJobApi() {
    const createModelApi = this.apiGateway.root.addResource(this.apiResource);
    const createModelIntegration = new apigw.LambdaIntegration(this.apiFunction(), {});
  }
}