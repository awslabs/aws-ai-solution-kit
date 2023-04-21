import { PythonLayerVersion } from '@aws-cdk/aws-lambda-python-alpha';
import {
  aws_apigateway,
  aws_dynamodb,
  aws_dynamodb as dynamodb,
  aws_s3,
  aws_sns,
  aws_sns_subscriptions as sns_subscriptions,
  CfnParameter,
  RemovalPolicy,
  Stack,
  StackProps,
} from 'aws-cdk-lib';
import { Runtime } from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { BlockPublicAccess } from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';
import { CreateModelJobApi } from './create-model-job-api';
import { CreateTrainJobApi } from './create-train-job-api';
import { ListAllCheckPointsApi } from './listall-chekpoints-api';
import { ListAllModelJobApi } from './listall-model-job-api';
import { RestApiGateway } from './rest-api-gateway';

import { UpdateModelStatusRestApi } from './update-model-status-api';
import { UpdateTrainJobApi } from './update-train-job-api';

// ckpt -> create_model -> model -> training -> ckpt -> inference
export class SdTrainDeployStack extends Stack {

  public readonly s3Bucket: aws_s3.Bucket;
  public readonly trainingTable: aws_dynamodb.Table;
  public readonly modelTable: aws_dynamodb.Table;
  public readonly checkPointTable: aws_dynamodb.Table;
  public apiGateway: aws_apigateway.RestApi;
  public readonly snsTopic: aws_sns.Topic;

  private readonly srcRoot='../middleware_api/lambda';

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);
    this.snsTopic = this.createSns();
    this.s3Bucket = this.createS3Bucket();
    const commonLayer = this.commonLayer();

    // Create DynamoDB table to store model job id
    this.modelTable = new dynamodb.Table(this, 'ModelTable', {
      tableName: 'ModelTable',
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    // Create DynamoDB table to store training job id
    this.trainingTable = new dynamodb.Table(this, 'TrainingTable', {
      tableName: 'TrainingTable',
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    this.checkPointTable = new dynamodb.Table(this, 'CheckpointTable', {
      tableName: 'CheckpointTable',
      partitionKey: {
        name: 'id',
        type: dynamodb.AttributeType.STRING,
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    // api gateway setup
    const restApi = new RestApiGateway(this, ['model', 'models', 'checkpoints', 'train']);
    this.apiGateway = restApi.apiGateway;
    const routers = restApi.routers;

    // POST /train
    new CreateTrainJobApi(this, 'aigc-create-train-api', {
      checkpointTable: this.checkPointTable,
      commonLayer: commonLayer,
      httpMethod: 'POST',
      modelTable: this.modelTable,
      router: routers.train,
      s3Bucket: this.s3Bucket,
      srcRoot: this.srcRoot,
      trainTable: this.trainingTable,
    });

    // PUT /train
    new UpdateTrainJobApi(this, 'aigc-put-train-api', {
      checkpointTable: this.checkPointTable,
      commonLayer: commonLayer,
      httpMethod: 'PUT',
      modelTable: this.modelTable,
      router: routers.train,
      s3Bucket: this.s3Bucket,
      srcRoot: this.srcRoot,
      trainTable: this.trainingTable,
      userTopic: this.snsTopic,
    });

    // POST /model
    new CreateModelJobApi(this, 'aigc-create-model-api', {
      router: routers.model,
      s3Bucket: this.s3Bucket,
      srcRoot: this.srcRoot,
      modelTable: this.modelTable,
      commonLayer: commonLayer,
      httpMethod: 'POST',
      checkpointTable: this.checkPointTable,
    });

    // GET /models
    new ListAllModelJobApi(this, 'aigc-listall-model-api', {
      router: routers.models,
      srcRoot: this.srcRoot,
      modelTable: this.modelTable,
      commonLayer: commonLayer,
      httpMethod: 'GET',
    });

    // PUT /model
    new UpdateModelStatusRestApi(this, 'aigc-update-model-api', {
      s3Bucket: this.s3Bucket,
      router: routers.model,
      httpMethod: 'PUT',
      commonLayer: commonLayer,
      srcRoot: this.srcRoot,
      modelTable: this.modelTable,
      snsTopic: this.snsTopic,
      checkpointTable: this.checkPointTable,
    });

    new ListAllCheckPointsApi(this, 'list-all-ckpts-api', {
      checkpointTable: this.checkPointTable,
      commonLayer: commonLayer,
      httpMethod: 'GET',
      router: routers.checkpoints,
      srcRoot: this.srcRoot,
    });
  }

  private createSns(): aws_sns.Topic {
    // CDK parameters for SNS email address
    const emailParam = new CfnParameter(this, 'email', {
      type: 'String',
      description: 'Email address to receive notifications',
      allowedPattern: '\\w[-\\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\\.)+[A-Za-z]{2,14}',
      default: 'example@example.com',
    });

    // Create SNS topic for notifications
    const snsTopic = new aws_sns.Topic(this, 'StableDiffusionSnsTopic');

    // Subscribe user to SNS notifications
    snsTopic.addSubscription(
      new sns_subscriptions.EmailSubscription(emailParam.valueAsString),
    );

    return snsTopic;
  }

  private createS3Bucket(): s3.Bucket {
    // CDK parameters for API Gateway API Key and SageMaker endpoint name
    const bucketName = new CfnParameter(this, 'aigc-bucket-name', {
      type: 'String',
      description: 'Base bucket for aigc solution to use. Mainly for uploading data files and storing results',
    });

    //The code that defines your stack goes here
    return new s3.Bucket(this, 'aigc-bucket', {
      bucketName: bucketName.valueAsString,
      blockPublicAccess: BlockPublicAccess.BLOCK_ACLS,
      removalPolicy: RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });
  }

  private commonLayer() {
    return new PythonLayerVersion(this, 'aigc-common-layer', {
      entry: `${this.srcRoot}`,
      bundling: {
        outputPathSuffix: '/python',
      },
      compatibleRuntimes: [Runtime.PYTHON_3_9],
    });
  }
}
