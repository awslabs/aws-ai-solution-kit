import { PythonLayerVersion } from '@aws-cdk/aws-lambda-python-alpha';
import {
  aws_apigateway,
  aws_dynamodb,
  aws_dynamodb as dynamodb,
  aws_s3,
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
import { RestApiGateway } from './rest-api-gateway';
import { UpdateModelStatusRestApi } from './update_model_status_api';


export class SdTrainDeployStack extends Stack {

  public readonly s3Bucket: aws_s3.Bucket;
  public readonly trainingTable: aws_dynamodb.Table;
  public readonly apiGateway: aws_apigateway.RestApi;

  private readonly srcRoot='../middleware_api/lambda';

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // const snsTopic = this.createSns();

    this.s3Bucket = this.createS3Bucket();
    // Create DynamoDB table to store training job id
    this.trainingTable = new dynamodb.Table(this, 'TrainingTable', {
      tableName: 'TrainingTable',
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    // const stateMachine = new SagemakerTrainStateMachine(this, {
    //   snsTopic: snsTopic,
    //   trainingTable: trainingTable,
    // });
    const restApi = new RestApiGateway(this, ['model']);
    this.apiGateway = restApi.apiGateway;
    const routers = restApi.routers;
    // POST /train
    // new SagemakerTrainApi(this, {
    //   api: apiGateway.apiGateway,
    //   apiKey: apiGateway.apiKey,
    //   stateMachineArn: stateMachine.stateMachineArn,
    //   apiResource: 'train-deploy',
    // });
    const commonLayer = this.commonLayer();
    new CreateModelJobApi(this, {
      router: routers.model,
      s3Bucket: this.s3Bucket,
      srcRoot: this.srcRoot,
      trainingTable: this.trainingTable,
      commonLayer: commonLayer,
      httpMethod: 'POST',
    });

    new UpdateModelStatusRestApi(this, {
      router: routers.model,
      httpMethod: 'PUT',
      commonLayer: commonLayer,
      srcRoot: this.srcRoot,
      trainingTable: this.trainingTable,
    });
  }

  // private createSns(): sns.Topic {
  //   // CDK parameters for SNS email address
  //   const emailParam = new CfnParameter(this, 'email', {
  //     type: 'String',
  //     description: 'Email address to receive notifications',
  //     default: 'example@example.com',
  //   });
  //
  //   // Create SNS topic for notifications
  //   const snsTopic = new sns.Topic(this, 'StableDiffusionSnsTopic');
  //
  //   // Subscribe user to SNS notifications
  //   snsTopic.addSubscription(
  //     new sns_subscriptions.EmailSubscription(emailParam.valueAsString),
  //   );
  //
  //   return snsTopic;
  // }

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
