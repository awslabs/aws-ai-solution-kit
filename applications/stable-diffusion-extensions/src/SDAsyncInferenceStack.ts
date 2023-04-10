import {
  Stack,
  StackProps,
  Duration,
  CfnParameter,
  CfnOutput,
  Aws,
  RemovalPolicy,
} from 'aws-cdk-lib';
import * as path from 'path';
import { Construct } from 'constructs';
import * as apigw from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';

import * as sns from 'aws-cdk-lib/aws-sns';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as eventSources from 'aws-cdk-lib/aws-lambda-event-sources';
import { CompositePrincipal, ServicePrincipal } from 'aws-cdk-lib/aws-iam';
import { RetentionDays } from 'aws-cdk-lib/aws-logs';
/*
AWS CDK code to create API Gateway, Lambda and SageMaker inference endpoint for txt2img/img2img inference 
based on Stable Diffusion. S3 is used to store large payloads and passed as object reference in the API Gateway 
request and Lambda function to avoid request payload limitation
Note: Sync Inference is put here for reference, we use Async Inference now
*/
export class SDAsyncInferenceStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // CDK parameters for API Gateway API Key and SageMaker endpoint name
    const apiKeyParam = new CfnParameter(this, 'txt2img-api-key', {
      type: 'String',
      description: 'API Key for txt2img/img2img Inference Service',
      // API Key value should be at least 20 characters
      default: '12345678901234567890',
    });

    // const endpointNameParam = new CfnParameter(this, "txt2img-endpoint-name", {
    //   type: "String",
    //   description:
    //     "SageMaker endpoint name for txt2img/img2img Inference Service",
    // });

    // Create an S3 bucket to store input and output payloads with public access blocked
    const payloadBucket = new s3.Bucket(this, 'PayloadBucket', {
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    // Create a Lambda function for inference
    const inferenceLambda = new lambda.DockerImageFunction(
      this,
      'InferenceLambda',
      {
        code: lambda.DockerImageCode.fromImageAsset('lambda/inference'),
        timeout: Duration.minutes(15),
        memorySize: 3008,
        environment: {
          BUCKET_NAME: payloadBucket.bucketName,
          BUCKET_INPUT_PREFIX: 'prefix/input.jpg',
          BUCKET_OUTPUT_PREFIX: 'prefix/output.jpg',
          // ENDPOINT_NAME: endpointNameParam.valueAsString,
        },
      }
    );

    // Grant Lambda permission to read/write from/to the S3 bucket
    payloadBucket.grantReadWrite(inferenceLambda);

    // Grant Lambda permission to invoke SageMaker endpoint
    inferenceLambda.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['sagemaker:InvokeEndpoint'],
        resources: ['*'],
      })
    );

    // Create an API Gateway
    const api = new apigw.RestApi(this, 'txt2img-api', {
      restApiName: 'txt2img/img2img Inference Service',
      description:
        'Inference service for txt2img/img2img based on Stable Diffusion',
    });

    // Create a POST method for the API Gateway and connect it to the Lambda function
    const txt2imgIntegration = new apigw.LambdaIntegration(inferenceLambda);

    // Add a POST method with prefix inference
    const inference = api.root.addResource('inference');
    inference.addMethod('POST', txt2imgIntegration, {
      apiKeyRequired: true,
    });

    // Add API Key to the API Gateway
    api.addApiKey('txt2img-api-key', {
      apiKeyName: 'txt2img-api-key',
      value: apiKeyParam.valueAsString,
    });

    // Create an SNS topic to get async inference result
    const inference_result_topic = new sns.Topic(
      this,
      'SNS-Receive-SageMaker-inference-result'
    );

    // Create a Lambda function
    const lambdaRole = new iam.Role(this, 'LambdaRole', {
      assumedBy: new CompositePrincipal(
        new ServicePrincipal('lambda.amazonaws.com')
      ),
    });

    // create Dynamodb table to save the cloudfront config version data
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
      }
    );
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
        path.join(__dirname, '../lambda/inference_result_notification')
      ),
      role: lambdaRole,
      environment: {
        DDB_VERSION_TABLE_NAME: sd_inference_job_table.tableName,
        S3_BUCKET: payloadBucket.bucketName,
        ACCOUNT_ID: Aws.ACCOUNT_ID,
        REGION_NAME: Aws.REGION,
      },
      logRetention: RetentionDays.ONE_WEEK,
    });

    // // Subscribe the Lambda function to the SNS topic
    // inference_result_topic.addSubscription(
    //   new subs.LambdaSubscription(handler),
    // );

    // Add the SNS topic as an event source for the Lambda function
    handler.addEventSource(
      new eventSources.SnsEventSource(inference_result_topic)
    );

    // create a lambda function
    

    // Output the API Gateway URL
    new CfnOutput(this, 'txt2img-api-url', {
      value: api.url,
    });
  }
}