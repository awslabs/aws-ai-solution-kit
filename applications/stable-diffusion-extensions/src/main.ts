import { App, Stack, StackProps, Duration, CfnParameter, CfnOutput, Size } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as apigw from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';

import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as sfn from 'aws-cdk-lib/aws-stepfunctions';
import * as sfn_tasks from 'aws-cdk-lib/aws-stepfunctions-tasks';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as sns_subscriptions from 'aws-cdk-lib/aws-sns-subscriptions';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';

export class Middleware extends Stack {
  constructor(scope: Construct, id: string, props: StackProps = {}) {
    super(scope, id, props);

    // define resources here...
  }
}

/*
AWS CDK TypeScript code to create API Gateway, Step Function and SageMaker for Stable Diffusion BYOC model creation and deployment. The API Gateway will trigger Step Function after it receive request, then training job on Step Function will use official Python SageMaker SDK to execute training job on SageMaker, then waiting job will wait such training job complete and trigger deployment job to deploy model onto SageMaker inference, finally it will send SNS notification to subscribe user.
*/
export class SdTrainDeployStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // CDK parameters for SNS email address
    const emailParam = new CfnParameter(this, 'email', {
      type: 'String',
      description: 'Email address to receive notifications',
      default: 'example@example.com',
    });
    const apiKeyParam = new CfnParameter(this, 'sd-extension-api-key', {
      type: 'String',
      description: 'API Key for Stable Diffusion extension',
      // API Key value should be at least 20 characters
      default: '09876543210987654321',
    });

    // Create SNS topic for notifications
    const snsTopic = new sns.Topic(this, 'StableDiffusionSnsTopic');

    // Subscribe user to SNS notifications
    snsTopic.addSubscription(new sns_subscriptions.EmailSubscription(emailParam.valueAsString));

    // Step Function Creation initial process
    // Create IAM role for Step Function
    const sagemakerRole = new iam.Role(this, 'SagemakerRole', {
      assumedBy: new iam.ServicePrincipal('states.amazonaws.com'),
    });
    // Add SageMaker permissions to the role
    sagemakerRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          'sagemaker:CreateTrainingJob',
          'sagemaker:CreateEndpoint',
          'sagemaker:CreateEndpointConfig',
          'sagemaker:CreateModel',
          'sagemaker:DescribeTrainingJob',
          'sagemaker:DescribeEndpoint',
          'sagemaker:DescribeEndpointConfig',
          'sagemaker:DescribeModel',
          'sagemaker:StopTrainingJob',
          'sagemaker:StopEndpoint',
          'sagemaker:DeleteEndpoint',
          'sagemaker:DeleteEndpointConfig',
          'sagemaker:DeleteModel',
          'sagemaker:UpdateEndpoint',
          'sagemaker:UpdateEndpointWeightsAndCapacities',
          'sagemaker:ListTrainingJobs',
          'sagemaker:ListTrainingJobsForHyperParameterTuningJob',
          'sagemaker:ListEndpointConfigs',
          'sagemaker:ListEndpoints',
          'sagemaker:ListModels',
          'sagemaker:ListProcessingJobs',
          'sagemaker:ListProcessingJobsForHyperParameterTuningJob'
        ],
        resources: ['*'],
      })
    );
    // Add S3 permissions to the role
    sagemakerRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ['s3:ListBucket', 's3:GetObject', 's3:PutObject', 's3:DeleteObject'],
        resources: ['*'],
      })
    );
    // Add SNS permissions to the role
    sagemakerRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ['sns:Publish'],
        resources: [snsTopic.topicArn],
      })
    );

    // Create DynamoDB table to store training job id
    const trainingTable = new dynamodb.Table(this, 'TrainingTable', {
      tableName : 'TrainingTable',
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
    });

    // Initial step to receive request from API Gateway and start training job
    const trainingJob = new sfn_tasks.SageMakerCreateTrainingJob(this, 'TrainModel', {
      trainingJobName: sfn.JsonPath.stringAt('$.JobName'),
      algorithmSpecification: {
        algorithmName: 'stable-diffusion-byoc',
        trainingImage: sfn_tasks.DockerImage.fromRegistry('763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-inference:1.8.0-cpu-py3'),
        trainingInputMode: sfn_tasks.InputMode.FILE,
      },
      inputDataConfig: [{
        channelName: 'train',
        dataSource: {
          s3DataSource: {
            s3DataType: sfn_tasks.S3DataType.S3_PREFIX,
            s3Location: sfn_tasks.S3Location.fromJsonExpression('$.S3Bucket'),
          },
        },
      }],
      outputDataConfig: {
        s3OutputLocation: sfn_tasks.S3Location.fromJsonExpression('$.S3Bucket'),
      },
      resourceConfig: {
        instanceCount: 1,
        instanceType: new ec2.InstanceType(sfn.JsonPath.stringAt('$.InstanceType')),
        volumeSize: Size.gibibytes(50),
      }, // optional: default is 1 instance of EC2 `M4.XLarge` with `10GB` volume
      stoppingCondition: {
        maxRuntime: Duration.hours(2),
      }, // optional: default is 1 hour
    });

    // Step to store training id into DynamoDB after training job complete
    const storeTrainingId = new sfn_tasks.LambdaInvoke(this, 'StoreTrainingId', {
      lambdaFunction: new lambda.DockerImageFunction(this, 'StoreTrainingIdFunction', {
        code: lambda.DockerImageCode.fromImageAsset('lambda/train'),
        timeout: Duration.minutes(15),
        memorySize: 3008,
        environment: {
          TABLE_NAME: trainingTable.tableName,
          JOB_NAME: sfn.JsonPath.stringAt('$.JobName'),
        },
      }),
      outputPath: '$.Payload',
    });
 
    // Step to create endpoint configuration
    const createEndpointConfig = new sfn_tasks.SageMakerCreateEndpointConfig(this, 'CreateEndpointConfig', {
      endpointConfigName: sfn.JsonPath.stringAt('$.JobName'),
      productionVariants: [{
        initialInstanceCount: 1,
        instanceType: new ec2.InstanceType(sfn.JsonPath.stringAt('$.InstanceType')),
        modelName: sfn.JsonPath.stringAt('$.JobName'),
        variantName: 'AllTraffic',
      }],
    });

    // Step to create endpoint
    const createEndpoint = new sfn_tasks.SageMakerCreateEndpoint(this, 'CreateEndpoint', {
      endpointName: sfn.JsonPath.stringAt('$.JobName'),
      endpointConfigName: sfn.JsonPath.stringAt('$.JobName'),
    });

    // Step to send SNS notification
    const sendNotification = new sfn_tasks.SnsPublish(this, 'SendNotification', {
      topic: snsTopic,
      message: sfn.TaskInput.fromText('Training job completed'),
    });

    // Create Step Function
    const stateMachine = new sfn.StateMachine(this, 'TrainDeployStateMachine', {
      definition: trainingJob
        .next(storeTrainingId)
        .next(createEndpointConfig)
        .next(createEndpoint)
        .next(sendNotification),
      role: sagemakerRole,
    });

    // Create an API Gateway, will merge with existing API Gateway
    const api = new apigw.RestApi(this, 'train-deploy-api', {
      restApiName: 'Stable Diffusion Train and Deploy API',
      description: 'This service is used to train and deploy Stable Diffusion models.',
    });

    const credentialsRole = new iam.Role(this, "getRole", {
      assumedBy: new iam.ServicePrincipal("apigateway.amazonaws.com"),
    });
    
    credentialsRole.attachInlinePolicy(
      new iam.Policy(this, "getPolicy", {
        statements: [
          new iam.PolicyStatement({
            // Access to trigger the Step Function
            actions: ["states:StartExecution"],
            effect: iam.Effect.ALLOW,
            resources: [stateMachine.stateMachineArn],
          }),
        ],
      })
    );

    // Add a POST method with prefix train-deploy and integration with Step Function
    const trainDeploy = api.root.addResource('train-deploy');
    const trainDeployIntegration = new apigw.AwsIntegration ({
      service: 'states',
      action: 'StartExecution',
      options: {
        credentialsRole: credentialsRole,
        passthroughBehavior: apigw.PassthroughBehavior.NEVER,
        requestTemplates: {
          "application/json": `{
            "input": "{\\"actionType\\": \\"create\\", \\"JobName\\": \\"$context.requestId\\", \\"S3Bucket\\": \\"$input.params('S3Bucket')\\", \\"InstanceType\\": \\"$input.params('InstanceType')\\"}",
            "stateMachineArn": "${stateMachine.stateMachineArn}"
          }`,
        },
        integrationResponses: [
          {
            statusCode: "200",
            responseTemplates: {
              "application/json": `{"done": true}`,
            },
          },
        ],
      },
    });

    trainDeploy.addMethod('POST', trainDeployIntegration, {
      apiKeyRequired: true, 
      methodResponses: [{ statusCode: "200" }],
    });

    // Add API Key to the API Gateway
    api.addApiKey('sd-extension-api-key', {
      apiKeyName: 'sd-extension-api-key',
      value: apiKeyParam.valueAsString,
    });

    // Output the API Gateway URL
    new CfnOutput(this, 'train-deploy-api-url', {
      value: api.url,
    });

  }
}

/*
AWS CDK code to create API Gateway, Lambda and SageMaker inference endpoint for txt2img/img2img inference 
based on Stable Diffusion. S3 is used to store large payloads and passed as object reference in the API Gateway 
request and Lambda function to avoid request payload limitation
*/
export class TxtImgInferenceStack extends Stack {
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
      description: 'SageMaker endpoint name for txt2img/img2img Inference Service',
    });

    // Create an S3 bucket to store input and output payloads
    const payloadBucket = new s3.Bucket(this, 'PayloadBucket');

    // Create a Lambda function for inference
    const inferenceLambda = new lambda.DockerImageFunction(this, 'InferenceLambda', {
      code: lambda.DockerImageCode.fromImageAsset('lambda/inference'),
      timeout: Duration.minutes(15),
      memorySize: 3008,
      environment: {
        BUCKET_NAME: payloadBucket.bucketName,
        BUCKET_INPUT_PREFIX: 'prefix/input.jpg',
        BUCKET_OUTPUT_PREFIX: 'prefix/output.jpg',
        ENDPOINT_NAME: endpointNameParam.valueAsString,
      },
    });

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
      description: 'Inference service for txt2img/img2img based on Stable Diffusion',
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
  region: 'us-west-2',
};

const app = new App();

// new Middleware(app, 'stable-diffusion-extensions-dev', { env: devEnv });

// new TxtImgInferenceCdkStack(app, 'TxtImgInferenceCdkStack-dev', { env: devEnv });

new SdTrainDeployStack(app, 'SdTrainDeployStack-dev', { env: devEnv });

app.synth();