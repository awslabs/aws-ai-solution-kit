import { PythonFunction, PythonFunctionProps } from '@aws-cdk/aws-lambda-python-alpha';
import {
  aws_dynamodb,
  aws_iam,
  aws_lambda,
  aws_lambda_event_sources,
  aws_s3,
  aws_sagemaker,
  aws_sns,
  Duration,
} from 'aws-cdk-lib';
import { Effect, ServicePrincipal } from 'aws-cdk-lib/aws-iam';
import { Architecture, Runtime } from 'aws-cdk-lib/aws-lambda';
import { CfnEndpointConfigProps, CfnEndpointProps, CfnModelProps } from 'aws-cdk-lib/aws-sagemaker';
import { Construct } from 'constructs';

export interface CreateModelSageMakerEndpointProps {
  primaryContainer: string;
  outputFolder: string;
  s3OutputBucket: aws_s3.Bucket;
  machineType: string;
  rootSrc: string;
  modelTable: aws_dynamodb.Table;
  commonLayer: aws_lambda.LayerVersion;
  userSnsTopic: aws_sns.Topic;
}

export class CreateModelSageMakerEndpoint {

  private readonly id;

  private readonly rootSrc: string;
  private readonly modelTable: aws_dynamodb.Table;
  private readonly layer: aws_lambda.LayerVersion;
  private readonly userSnsTopic: aws_sns.Topic;

  private readonly s3Bucket: aws_s3.Bucket;
  public readonly model: aws_sagemaker.CfnModel;
  public readonly modelConfig: aws_sagemaker.CfnEndpointConfig;
  public readonly modelEndpoint: aws_sagemaker.CfnEndpoint;


  public readonly successTopic: aws_sns.Topic;
  public readonly failureTopic: aws_sns.Topic;

  constructor(scope: Construct, id: string, props: CreateModelSageMakerEndpointProps) {
    this.s3Bucket = props.s3OutputBucket;
    this.id = id;
    this.modelTable = props.modelTable;
    this.layer = props.commonLayer;
    this.rootSrc = props.rootSrc;
    this.userSnsTopic = props.userSnsTopic;


    this.successTopic = new aws_sns.Topic(scope, `${id}-success-topic`, {
      displayName: 'successCreateModel',
      topicName: 'successCreateModel',
    });
    this.failureTopic = new aws_sns.Topic(scope, `${id}-failure-topic`, {
      displayName: 'failureCreateModel',
      topicName: 'failureCreateModel',
    });

    this.model = new aws_sagemaker.CfnModel(scope, `${this.id}-model`, <CfnModelProps>{
      executionRoleArn: this.sagemakerRole(scope).roleArn,
      modelName: `${this.id}-cdk-sample-model`,
      primaryContainer: {
        image: props.primaryContainer,
      },
    });

    this.modelConfig = new aws_sagemaker.CfnEndpointConfig(scope, `${this.id}-model-config`, <CfnEndpointConfigProps>{
      endpointConfigName: `${this.id}-config`,
      productionVariants: [
        {
          modelName: this.model.modelName,
          initialVariantWeight: 1.0,
          instanceType: props.machineType,
          variantName: 'main',
          initialInstanceCount: 1,
        },
      ],
      asyncInferenceConfig: {
        // clientConfig: {},
        outputConfig: {
          // s3OutputPath: 's3://alvindaiyan-aigc-testing-playground/sagemaker-manu/',
          s3OutputPath: props.s3OutputBucket.s3UrlForObject(props.outputFolder),
          notificationConfig: {
            successTopic: this.successTopic.topicArn,
            errorTopic: this.failureTopic.topicArn,
          },
        },
      },
    });

    this.modelConfig.node.addDependency(this.model);

    this.modelEndpoint = new aws_sagemaker.CfnEndpoint(scope, `${this.id}-endpoint`, <CfnEndpointProps>{
      endpointConfigName: this.modelConfig.endpointConfigName,
      endpointName: `${this.id}-endpoint`,
    });
    this.modelEndpoint.node.addDependency(this.modelConfig);

    const processResult = this.createProcessResultLambda(scope, id);
    processResult.node.addDependency(this.successTopic, this.failureTopic, this.modelEndpoint);
    const successEventSource = new aws_lambda_event_sources.SnsEventSource(this.successTopic, {});
    const failureEventSource = new aws_lambda_event_sources.SnsEventSource(this.failureTopic, {});
    processResult.addEventSource(successEventSource);
    processResult.addEventSource(failureEventSource);
  }

  private sagemakerRole(scope: Construct): aws_iam.Role {
    const sagemakerRole = new aws_iam.Role(scope, `${this.id}-endpoint-role`, {
      assumedBy: new ServicePrincipal('sagemaker.amazonaws.com'),
    });
    sagemakerRole.addManagedPolicy(aws_iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSageMakerFullAccess'));

    sagemakerRole.addToPolicy(new aws_iam.PolicyStatement({
      effect: Effect.ALLOW,
      actions: [
        's3:GetObject',
        's3:PutObject',
        's3:DeleteObject',
        's3:ListBucket',
      ],
      // resources: ['arn:aws:s3:::*'],
      resources: [`${this.s3Bucket.bucketArn}/*`],
    }));

    sagemakerRole.addToPolicy(new aws_iam.PolicyStatement({
      effect: Effect.ALLOW,
      actions: [
        'sns:Publish',
        'sns:GetTopicAttributes',
        'sns:SetTopicAttributes',
        'sns:Subscribe',
        'sns:ListSubscriptionsByTopic',
        'sns:Publish',
        'sns:Receive',
      ],
      // resources: ['arn:aws:s3:::*'],
      resources: [this.successTopic.topicArn, this.failureTopic.topicArn],
    }));
    return sagemakerRole;
  }

  private createProcessResultLambda(scope: Construct, id: string): aws_lambda.Function {
    const updateModelLambda = new PythonFunction(scope, `${id}-process-sg-result`, <PythonFunctionProps>{
      functionName: `${id}-process-sg-result`,
      entry: `${this.rootSrc}/create_model`,
      architecture: Architecture.X86_64,
      runtime: Runtime.PYTHON_3_9,
      index: 'update_job_api.py',
      handler: 'process_result',
      timeout: Duration.seconds(900),
      role: this.lambdaRole(scope, id),
      memorySize: 1024,
      environment: {
        DYNAMODB_TABLE: this.modelTable.tableName,
        S3_BUCKET: this.s3Bucket.bucketName,
        SUCCESS_TOPIC_ARN: this.successTopic.topicArn,
        ERROR_TOPIC_ARN: this.failureTopic.topicArn,
        SAGEMAKER_ENDPOINT_NAME: this.modelEndpoint.attrEndpointName,
        USER_TOPIC_ARN: this.userSnsTopic.topicArn,
      },
      layers: [this.layer],
    });
    updateModelLambda.node.addDependency(this.modelEndpoint);

    return updateModelLambda;
  }

  private lambdaRole(scope: Construct, baseId: string): aws_iam.Role {
    const newRole = new aws_iam.Role(scope, `${baseId}-cm-result-role`, {
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
        's3:GetObject',
        's3:PutObject',
        's3:DeleteObject',
        's3:ListBucket',
      ],
      resources: [`${this.s3Bucket.bucketArn}/*`,
        'arn:aws:s3:::*SageMaker*',
        'arn:aws:s3:::*Sagemaker*',
        'arn:aws:s3:::*sagemaker*'],
    }));

    newRole.addToPolicy(new aws_iam.PolicyStatement({
      effect: Effect.ALLOW,
      actions: [
        'sns:Publish',
        'sns:GetTopicAttributes',
        'sns:SetTopicAttributes',
        'sns:ListSubscriptionsByTopic',
        'sns:Receive',
      ],
      resources: [this.userSnsTopic.topicArn],
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
}