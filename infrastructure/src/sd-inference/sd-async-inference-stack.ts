import {
  Stack,
  StackProps,
  Duration,
  Aws,
  RemovalPolicy,
  aws_ecr,
  CustomResource,
} from 'aws-cdk-lib';
import * as apigw from 'aws-cdk-lib/aws-apigateway';

import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as eventSources from 'aws-cdk-lib/aws-lambda-event-sources';
import { RetentionDays } from 'aws-cdk-lib/aws-logs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sns from 'aws-cdk-lib/aws-sns';
import { Construct } from 'constructs';
import { DockerImageName, ECRDeployment } from '../cdk-ecr-deployment/lib';
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
  snsTopic: sns.Topic
}

export class SDAsyncInferenceStack extends Stack {



  constructor(scope: Construct, id: string, props?: SDAsyncInferenceStackProps) {
    super(scope, id, props);
    const srcImg = 'public.ecr.aws/t6q0v9n4/aigc-webui-inference:latest';

    const restful_api = apigw.RestApi.fromRestApiAttributes(this, 'ImportedRestApi', {
      restApiId: props?.api_gate_way.restApiId ?? '',
      rootResourceId: props?.api_gate_way.restApiRootResourceId ?? '',
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

    // create Dynamodb table to save the inference job data
    const sd_endpoint_deployment_job_table = new dynamodb.Table(
      this,
      'SD_endpoint_deployment_job',
      {
        billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
        removalPolicy: RemovalPolicy.DESTROY,
        partitionKey: {
          name: 'EndpointDeploymentJobId',
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

    const inferenceECR_url = this.createInferenceECR(srcImg);

    const stepFunctionStack = new SagemakerInferenceStateMachine(this, {
      snsTopic: inference_result_topic,
      snsErrorTopic: inference_result_error_topic,
      inferenceJobName: sd_inference_job_table.tableName,
      s3_bucket_name: props?.s3_bucket.bucketName ?? '',
      endpointDeploymentJobName: sd_endpoint_deployment_job_table.tableName,
      userNotifySNS: props?.snsTopic ?? new sns.Topic(this, 'MyTopic', {
        displayName: 'My SNS Topic',
      }),
      inference_ecr_url: inferenceECR_url
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
          DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME: sd_endpoint_deployment_job_table.tableName,
          S3_BUCKET: props?.s3_bucket.bucketName ?? '',
          ACCOUNT_ID: Aws.ACCOUNT_ID,
          REGION_NAME: Aws.REGION,
          SNS_INFERENCE_SUCCESS: inference_result_topic.topicName,
          SNS_INFERENCE_ERROR: inference_result_error_topic.topicName,
          STEP_FUNCTION_ARN: stepFunctionStack.stateMachineArn,
          NOTICE_SNS_TOPIC: props?.snsTopic.topicArn ?? "",
          INFERENCE_ECR_IMAGE_URL: inferenceECR_url
        },
        logRetention: RetentionDays.ONE_WEEK,
      });

    // Grant Lambda permission to read/write from/to the S3 bucket
    props?.s3_bucket.grantReadWrite(inferenceLambda);

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
          'dynamodb:*'
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

    inference?.addMethod('GET', txt2imgIntegration, {
      apiKeyRequired: true,
    });

    const run_sagemaker_inference = inference.addResource('run-sagemaker-inference');
    run_sagemaker_inference.addMethod('POST', txt2imgIntegration, {
      apiKeyRequired: true,
    });

    const deploy_sagemaker_endpoint = inference.addResource('deploy-sagemaker-endpoint');
    deploy_sagemaker_endpoint.addMethod('POST', txt2imgIntegration, {
      apiKeyRequired: true,
    });

    const list_endpoint_deployment_jobs = inference.addResource('list-endpoint-deployment-jobs');
    list_endpoint_deployment_jobs.addMethod('GET', txt2imgIntegration, {
      apiKeyRequired: true,
    })

    const list_inference_jobs = inference.addResource('list-inference-jobs');
    list_inference_jobs.addMethod('GET', txt2imgIntegration, {
      apiKeyRequired: true,
    })

    const get_endpoint_deployment_job = inference.addResource('get-endpoint-deployment-job');
    get_endpoint_deployment_job.addMethod('GET', txt2imgIntegration, {
      apiKeyRequired: true,
    })

    const get_inference_job = inference.addResource('get-inference-job');
    get_inference_job.addMethod('GET', txt2imgIntegration, {
      apiKeyRequired: true,
    })

    const get_texual_inversion_list = inference.addResource('get-texual-inversion-list');
    get_texual_inversion_list.addMethod('GET', txt2imgIntegration, {
      apiKeyRequired: true,
    })

    const get_lora_list = inference.addResource('get-lora-list');
    get_lora_list.addMethod('GET', txt2imgIntegration, {
      apiKeyRequired: true,
    })

    const get_hypernetwork_list = inference.addResource('get-hypernetwork-list');
    get_hypernetwork_list.addMethod('GET', txt2imgIntegration, {
      apiKeyRequired: true,
    })

    const get_controlnet_model_list = inference.addResource('get-controlnet-model-list');
    get_controlnet_model_list.addMethod('GET', txt2imgIntegration, {
      apiKeyRequired: true,
    })
    
    const get_inference_job_image_output = inference.addResource('get-inference-job-image-output');
    get_inference_job_image_output.addMethod('GET', txt2imgIntegration, {
      apiKeyRequired: true,
    })

    const get_inference_job_param_output = inference.addResource('get-inference-job-param-output');
    get_inference_job_param_output.addMethod('GET', txt2imgIntegration, {
      apiKeyRequired: true,
    })

    // const test_output = inference.addResource('generate-s3-presigned-url-for-uploading',
    //   {
    //     defaultCorsPreflightOptions: {
    //       allowOrigins: ['*'], // Allow all origins
    //       allowMethods: ['GET', 'POST', 'OPTION', 'PUT'], // Specify the allowed methods
    //       allowHeaders: ['*'], // Specify the allowed headers
    //     },
    //   }
    // );
    const test_output = inference.addResource('generate-s3-presigned-url-for-uploading') 
    // test_output.addCorsPreflight({
    //   allowOrigins: apigw.Cors.ALL_ORIGINS,
    //   allowMethods: apigw.Cors.ALL_METHODS,
    //   allowHeaders: ['Content-Type', 'X-Amz-Date', 'Authorization', 'X-Api-Key', 'X-Amz-Security-Token', 'X-Amz-User-Agent'],
    // });

    test_output.addMethod("GET", txt2imgIntegration, {
        apiKeyRequired: true,
    });
    const testResource = inference.addResource("test-connection");
    const mockIntegration = new apigw.MockIntegration({
        integrationResponses: [
            {
                statusCode: "200",
                responseTemplates: {
                    "application/json": JSON.stringify({ message: "Success" }),
                },
            },
        ],
        passthroughBehavior: apigw.PassthroughBehavior.NEVER,
        requestTemplates: {
            "application/json": '{"statusCode": 200}',
        },
    });

    testResource.addMethod("GET", mockIntegration, {
        methodResponses: [
            {
                statusCode: "200",
                responseModels: {
                    "application/json": apigw.Model.EMPTY_MODEL,
                },
            },
        ],
    });

    const current_time = new Date().toISOString;
    const deployment = new apigw.Deployment(this, 'rest-api-deployment'+current_time, { api: restful_api });
    deployment.addToLogicalId(new Date().toISOString());
    (deployment as any).resource.stageName = 'prod';
   
    // Create a Lambda function for inference
    const handler = new lambda.DockerImageFunction(
      this,
      'InferenceResultNotification',
      {
        code: lambda.DockerImageCode.fromImageAsset('../middleware_api/lambda/inference_result_notification'),
        timeout: Duration.minutes(15),
        memorySize: 1024,
        environment: {
          DDB_INFERENCE_TABLE_NAME: sd_inference_job_table.tableName,
          DDB_TRAINING_TABLE_NAME: props?.training_table.tableName ?? '',
          DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME: sd_endpoint_deployment_job_table.tableName,
          S3_BUCKET: props?.s3_bucket.bucketName ?? '',
          ACCOUNT_ID: Aws.ACCOUNT_ID,
          REGION_NAME: Aws.REGION,
          SNS_INFERENCE_SUCCESS: inference_result_topic.topicName,
          SNS_INFERENCE_ERROR: inference_result_error_topic.topicName,
          STEP_FUNCTION_ARN: stepFunctionStack.stateMachineArn,
          NOTICE_SNS_TOPIC: props?.snsTopic.topicArn ?? "",
          INFERENCE_ECR_IMAGE_URL: inferenceECR_url
        },
        logRetention: RetentionDays.ONE_WEEK,
      });

        // Grant Lambda permission to invoke SageMaker endpoint
        handler.addToRolePolicy(
          new iam.PolicyStatement({
            actions: [
              'sagemaker:*',
              's3:Get*',
              's3:List*',
              's3:PutObject',
              's3:GetObject',
              'sns:*',
              'states:*',
              'dynamodb:*'
            ],
            resources: ['*'],
          }),
        );  


    // Add the SNS topic as an event source for the Lambda function
    handler.addEventSource(
      new eventSources.SnsEventSource(inference_result_topic),
    );
    handler.addEventSource(
      new eventSources.SnsEventSource(inference_result_error_topic),
    );

    

  }

  private createInferenceECR(srcImg: string) {
    const dockerRepo = new aws_ecr.Repository(this, 'aigc-webui-inference-repo', {
      repositoryName: 'aigc-webui-inference',
      removalPolicy: RemovalPolicy.DESTROY,
      autoDeleteImages: true,
    });

    const ecrDeployment = new ECRDeployment(this, `aigc-webui-inference-ecr-deploy`, {
      src: new DockerImageName(srcImg),
      dest: new DockerImageName(`${dockerRepo.repositoryUri}:latest`),
    });

    // trigger the custom resource lambda
    const customJob = new CustomResource(this, `aigc-webui-inference-ecr-cr-image`, {
      serviceToken: ecrDeployment.serviceToken,
      resourceType: 'Custom::AIGCSolutionECRLambda',
      properties: {
        SrcImage: `docker://${srcImg}`,
        DestImage: `docker://${dockerRepo.repositoryUri}:latest`,
        RepositoryName: `${dockerRepo.repositoryName}`,
      },
    });

    customJob.node.addDependency(ecrDeployment);

    return dockerRepo.repositoryUri
  }
}