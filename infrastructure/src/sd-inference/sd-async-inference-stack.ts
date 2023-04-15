import * as path from 'path';
import {
  Stack,
  StackProps,
  Duration,
  Aws,
  RemovalPolicy,
} from 'aws-cdk-lib';
import * as apigw from 'aws-cdk-lib/aws-apigateway';

import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as iam from 'aws-cdk-lib/aws-iam';
import { CompositePrincipal, ServicePrincipal } from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as eventSources from 'aws-cdk-lib/aws-lambda-event-sources';
import { RetentionDays } from 'aws-cdk-lib/aws-logs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sns from 'aws-cdk-lib/aws-sns';
import { Construct } from 'constructs';
import { SagemakerInferenceStateMachine } from './sd-sagemaker-inference-state-machine';
/*
AWS CDK code to create API Gateway, Lambda and SageMaker inference endpoint for txt2img/img2img inference
based on Stable Diffusion. S3 is used to store large payloads and passed as object reference in the API Gateway
request and Lambda function to avoid request payload limitation
Note: Sync Inference is put here for reference, we use Async Inference now
*/
export interface SDAsyncInferenceStackProps extends StackProps {
  api_gate_way: apigw.RestApi;
  s3_bucket: s3.Bucket;
  training_table: dynamodb.Table;
}

export class SDAsyncInferenceStack extends Stack {
  constructor(scope: Construct, id: string, props?: SDAsyncInferenceStackProps) {
    super(scope, id, props);

    const restful_api = apigw.RestApi.fromRestApiAttributes(this, 'ImportedRestApi', {
      restApiId: props?.api_gate_way.restApiId ?? '',
      rootResourceId: props?.api_gate_way.restApiRootResourceId ?? '',
    });


    // Create an S3 bucket to store input and output payloads with public access blocked
    const payloadBucket = new s3.Bucket(this, 'PayloadBucket', {
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    // create Dynamodb table to save the inference job data
    const sd_inference_job_table = new dynamodb.Table(
      this,
      'SD_Inference_job',
      {
        billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
        removalPolicy: RemovalPolicy.DESTROY,
        partitionKey: {
          name: 'InferenceJobId',
          type: dynamodb.AttributeType.STRING,
        },
        pointInTimeRecovery: true,
      },
    );

    // Create an SNS topic to get async inference result
    const inference_result_topic = new sns.Topic(
      this,
      'SNS-Receive-SageMaker-inference-success',
    );

    const inference_result_error_topic = new sns.Topic(
      this,
      'SNS-Receive-SageMaker-inference-error',
    );

    const stepFunctionStack = new SagemakerInferenceStateMachine(this, {
      snsTopic: inference_result_topic,
    });

    // Create a Lambda function for inference
    const inferenceLambda = new lambda.DockerImageFunction(
      this,
      'InferenceLambda',
      {
        code: lambda.DockerImageCode.fromImageAsset('../middleware_api/lambda/inference'),
        timeout: Duration.minutes(15),
        memorySize: 3008,
        environment: {
          DDB_INFERENCE_TABLE_NAME: sd_inference_job_table.tableName,
          DDB_TRAINING_TABLE_NAME: props?.training_table.tableName ?? '',
          S3_BUCKET: payloadBucket.bucketName,
          ACCOUNT_ID: Aws.ACCOUNT_ID,
          REGION_NAME: Aws.REGION,
          SNS_INFERENCE_SUCCESS: inference_result_topic.topicName,
          SNS_INFERENCE_ERROR: inference_result_error_topic.topicName,
          STEP_FUNCTION_ARN: stepFunctionStack.stateMachineArn,
        },
        logRetention: RetentionDays.ONE_WEEK,
      });

    // Grant Lambda permission to read/write from/to the S3 bucket
    payloadBucket.grantReadWrite(inferenceLambda);

    // Grant Lambda permission to invoke SageMaker endpoint
    inferenceLambda.addToRolePolicy(
      new iam.PolicyStatement({
        actions: [
          'sagemaker:*',
          's3:Get*',
          's3:List*',
          's3:PutObject',
          's3:GetObject',
          'sns:*',
          'states:*',
        ],
        resources: ['*'],
      }),
    );

    // Create a POST method for the API Gateway and connect it to the Lambda function
    const txt2imgIntegration = new apigw.LambdaIntegration(inferenceLambda);

    // Add a POST method with prefix inference
    // const inference = restful_api?.root.addResource('inference');
    const inference = restful_api?.root.addResource('inference');
    inference?.addMethod('POST', txt2imgIntegration, {
      apiKeyRequired: true,
    });

    const run_sagemaker_inference = inference.addResource('run-sagemaker-inference');
    run_sagemaker_inference.addMethod('POST', txt2imgIntegration, {
      apiKeyRequired: true,
    });


    // Create a Lambda function
    const lambdaRole = new iam.Role(this, 'LambdaRole', {
      assumedBy: new CompositePrincipal(
        new ServicePrincipal('lambda.amazonaws.com'),
      ),
    });


    const ddb_rw_policy = new iam.PolicyStatement({
      resources: [sd_inference_job_table.tableArn],
      actions: [
        'dynamodb:CreateTable',
        'dynamodb:DescribeTable',
        'dynamodb:DeleteItem',
        'dynamodb:GetItem',
        'dynamodb:PutItem',
        'dynamodb:Query',
        'dynamodb:Scan',
        'dynamodb:UpdateItem',
        'dynamodb:UpdateTable',
      ],
    });

    const s3_rw_policy = new iam.PolicyStatement({
      resources: ['*'],
      actions: [
        's3:Get*',
        's3:List*',
        's3-object-lambda:Get*',
        's3-object-lambda:List*',
        's3:PutObject',
        's3:GetObject',
      ],
    });

    const lambdaRunPolicy = new iam.PolicyStatement({
      resources: ['*'],
      actions: [
        'logs:CreateLogGroup',
        'logs:CreateLogStream',
        'logs:PutLogEvents',
      ],
    });

    lambdaRole.addToPolicy(ddb_rw_policy);
    lambdaRole.addToPolicy(s3_rw_policy);
    lambdaRole.addToPolicy(lambdaRunPolicy);

    const handler = new lambda.Function(this, 'InferenceResultNotification', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'app.lambda_handler',
      memorySize: 256,
      timeout: Duration.seconds(900),
      code: lambda.Code.fromAsset(
        path.join(__dirname, '../../../middleware_api/lambda/inference_result_notification'),
      ),
      role: lambdaRole,
      environment: {
        DDB_INFERENCE_TABLE_NAME: sd_inference_job_table.tableName,
        DDB_TRAINING_TABLE_NAME: props?.training_table.tableName ?? '',
        S3_BUCKET: payloadBucket.bucketName,
        ACCOUNT_ID: Aws.ACCOUNT_ID,
        REGION_NAME: Aws.REGION,

      },
      logRetention: RetentionDays.ONE_WEEK,
    });


    // Add the SNS topic as an event source for the Lambda function
    handler.addEventSource(
      new eventSources.SnsEventSource(inference_result_topic),
    );
    handler.addEventSource(
      new eventSources.SnsEventSource(inference_result_error_topic),
    );

  }
}