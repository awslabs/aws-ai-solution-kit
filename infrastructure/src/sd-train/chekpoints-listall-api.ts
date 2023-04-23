import { PythonFunction, PythonFunctionProps } from '@aws-cdk/aws-lambda-python-alpha';
import {
  aws_apigateway,
  aws_apigateway as apigw,
  aws_dynamodb,
  aws_iam,
  aws_lambda, aws_s3,
  Duration,
} from 'aws-cdk-lib';
import { MethodOptions } from 'aws-cdk-lib/aws-apigateway/lib/method';
import { Effect } from 'aws-cdk-lib/aws-iam';
import { Architecture, Runtime } from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';


export interface ListAllCheckPointsApiProps {
  router: aws_apigateway.Resource;
  httpMethod: string;
  checkpointTable: aws_dynamodb.Table;
  srcRoot: string;
  commonLayer: aws_lambda.LayerVersion;
  s3Bucket: aws_s3.Bucket;
}

export class ListAllCheckPointsApi {
  private readonly src;
  private readonly router: aws_apigateway.Resource;
  private readonly httpMethod: string;
  private readonly scope: Construct;
  private readonly checkpointTable: aws_dynamodb.Table;
  private readonly layer: aws_lambda.LayerVersion;
  private readonly s3Bucket: aws_s3.Bucket;

  private readonly baseId: string;

  constructor(scope: Construct, id: string, props: ListAllCheckPointsApiProps) {
    this.scope = scope;
    this.baseId = id;
    this.router = props.router;
    this.httpMethod = props.httpMethod;
    this.checkpointTable = props.checkpointTable;
    this.src = props.srcRoot;
    this.layer = props.commonLayer;
    this.s3Bucket = props.s3Bucket;

    this.listAllCheckpointsApi();
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
      ],
      resources: [this.checkpointTable.tableArn],
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

  private listAllCheckpointsApi() {
    const lambdaFunction = new PythonFunction(this.scope, `${this.baseId}-listall`, <PythonFunctionProps>{
      functionName: `${this.baseId}-listall-checkpoints`,
      entry: `${this.src}/create_model`,
      architecture: Architecture.X86_64,
      runtime: Runtime.PYTHON_3_9,
      index: 'checkpoint_api.py',
      handler: 'list_all_checkpoints_api',
      timeout: Duration.seconds(900),
      role: this.iamRole(),
      memorySize: 1024,
      environment: {
        CHECKPOINT_TABLE: this.checkpointTable.tableName,
        S3_BUCKET: this.s3Bucket.bucketName,
      },
      layers: [this.layer],
    });

    const listCheckpointsIntegration = new apigw.LambdaIntegration(
      lambdaFunction,
      {
        proxy: false,
        requestParameters: {
          'integration.request.querystring.status': 'method.request.querystring.status',
          'integration.request.querystring.types': 'method.request.querystring.types',
        },
        requestTemplates: {
          'application/json': '{\n' +
              '    "queryStringParameters": {\n' +
              '        #foreach($queryParam in $input.params().querystring.keySet())\n' +
              '        "$queryParam": "$util.escapeJavaScript($input.params().querystring.get($queryParam))"\n' +
              '        #if($foreach.hasNext),#end\n' +
              '        #end\n' +
              '    }\n' +
              '}',
        },
        integrationResponses: [{ statusCode: '200' }],
      },
    );
    this.router.addMethod(this.httpMethod, listCheckpointsIntegration, <MethodOptions>{
      apiKeyRequired: true,
      requestParameters: {
        'method.request.querystring.status': true,
        'method.request.querystring.types': true,
      },
      methodResponses: [{
        statusCode: '200',
      }, { statusCode: '500' }],
    });
  }
}

