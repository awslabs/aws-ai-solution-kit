import { PythonFunction, PythonFunctionProps } from '@aws-cdk/aws-lambda-python-alpha';
import {
  aws_apigateway as apigw,
  aws_dynamodb,
  aws_iam,
  aws_lambda, aws_s3,
  aws_stepfunctions as sfn,
  Duration,
} from 'aws-cdk-lib';
import { MethodOptions } from 'aws-cdk-lib/aws-apigateway/lib/method';
import { Resource } from 'aws-cdk-lib/aws-apigateway/lib/resource';
import { Effect } from 'aws-cdk-lib/aws-iam';
import { Architecture, Runtime } from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';

export interface UpdateModelStatusRestApiProps {
  httpMethod: string;
  router: Resource;
  modelTable: aws_dynamodb.Table;
  srcRoot: string;
  commonLayer: aws_lambda.LayerVersion;
  stateMachine: sfn.StateMachine;
  s3Bucket: aws_s3.Bucket;
}

export class UpdateModelStatusRestApi {

  private readonly src;
  private readonly scope: Construct;
  private readonly modelTable: aws_dynamodb.Table;
  private readonly layer: aws_lambda.LayerVersion;
  private readonly router: Resource;
  private readonly httpMethod: string;
  private readonly stateMachine: sfn.StateMachine;
  private readonly s3Bucket: aws_s3.Bucket;

  private readonly baseId = 'aigc-update-train-job';

  constructor(scope: Construct, props: UpdateModelStatusRestApiProps) {
    this.scope = scope;
    this.router = props.router;
    this.modelTable = props.modelTable;
    this.httpMethod = props.httpMethod;
    this.src = props.srcRoot;
    this.layer = props.commonLayer;
    this.stateMachine = props.stateMachine;
    this.s3Bucket = props.s3Bucket;

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
      resources: [this.modelTable.tableArn],
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
    const updateModelLambda = new PythonFunction(this.scope, `${this.baseId}-handler`, <PythonFunctionProps>{
      functionName: `${this.baseId}-update-model`,
      entry: `${this.src}/create_model`,
      architecture: Architecture.X86_64,
      runtime: Runtime.PYTHON_3_9,
      index: 'update_job_api.py',
      handler: 'update_train_job_api',
      timeout: Duration.seconds(900),
      role: this.iamRole(),
      memorySize: 1024,
      environment: {
        DYNAMODB_TABLE: this.modelTable.tableName,
        SFN_ARN: this.stateMachine.stateMachineArn,
        S3_BUCKET: this.s3Bucket.bucketName,
      },
      layers: [this.layer],
    });
    updateModelLambda.node.addDependency(this.stateMachine);
    const updateModelLambdaIntegration = new apigw.LambdaIntegration(
      updateModelLambda,
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