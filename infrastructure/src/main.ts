import {
  App,
  Stack,
  StackProps,
  Duration,
  CfnParameter,
  CfnOutput,
} from 'aws-cdk-lib';
import * as apigw from 'aws-cdk-lib/aws-apigateway';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3';

import { Construct } from 'constructs';
import { SdTrainDeployStack } from './sd-train/sd-train-deploy-stack';
// import { SDAsyncInferenceStack } from './SDAsyncInferenceStack';

export class Middleware extends Stack {
  constructor(scope: Construct, id: string, props: StackProps = {}) {
    super(scope, id, props);

  }
}

/*
AWS CDK code to create API Gateway, Lambda and SageMaker inference endpoint for txt2img/img2img inference
based on Stable Diffusion. S3 is used to store large payloads and passed as object reference in the API Gateway
request and Lambda function to avoid request payload limitation
Note: Sync Inference is put here for reference, we use Async Inference now
*/
export class SdSyncInferenceStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // CDK parameters for API Gateway API Key and SageMaker endpoint name
    const apiKeyParam = new CfnParameter(this, 'txt2img-api-key', {
      type: 'String',
      description: 'API Key for txt2img/img2img Inference Service',
      // API Key value should be at least 20 characters
      default: '12345678901234567890',
    });

    const endpointNameParam = new CfnParameter(this, 'txt2img-endpoint-name', {
      type: 'String',
      description:
          'SageMaker endpoint name for txt2img/img2img Inference Service',
    });

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
          ENDPOINT_NAME: endpointNameParam.valueAsString,
        },
      },
    );

    // Grant Lambda permission to read/write from/to the S3 bucket
    payloadBucket.grantReadWrite(inferenceLambda);

    // Grant Lambda permission to invoke SageMaker endpoint
    inferenceLambda.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['sagemaker:InvokeEndpoint'],
        resources: ['*'],
      }),
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

    // Output the API Gateway URL
    new CfnOutput(this, 'txt2img-api-url', {
      value: api.url,
    });
  }
}

// for development, use account/region from cdk cli
const devEnv = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

const app = new App();

// new Middleware(app, 'stable-diffusion-extensions-dev', { env: devEnv });

// new TxtImgInferenceCdkStack(app, 'TxtImgInferenceCdkStack-dev', { env: devEnv });

// new SdTrainDeployStack(app, 'SdTrainDeployStack-dev', { env: devEnv });

// new SDAsyncInferenceStack(app, 'SdAsyncInferenceStack-dev', { env: devEnv });

new SdTrainDeployStack(app, 'SdDreamBoothTrainStack', { env: devEnv });

app.synth();
