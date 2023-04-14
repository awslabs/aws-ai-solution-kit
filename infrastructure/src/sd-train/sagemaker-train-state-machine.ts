import {
  aws_dynamodb as dynamodb,
  aws_sns as sns,
  aws_iam as iam,
  aws_stepfunctions as sfn,
  aws_stepfunctions_tasks as sfn_tasks,
  aws_lambda as lambda,
  aws_ec2 as ec2,
  Duration,
  Size,
} from 'aws-cdk-lib';
import { StateMachineProps } from 'aws-cdk-lib/aws-stepfunctions/lib/state-machine';
import { SnsPublishProps } from 'aws-cdk-lib/aws-stepfunctions-tasks/lib/sns/publish';
import { Construct } from 'constructs';

export interface SagemakerTrainProps {
  snsTopic: sns.Topic;
  trainingTable: dynamodb.Table;
  srcRoot: string;
}

export class SagemakerTrainStateMachine {
  public readonly stateMachineArn: string;
  private readonly scope: Construct;
  private readonly srcRoot: string;

  constructor(scope: Construct, props: SagemakerTrainProps) {
    this.scope = scope;
    this.srcRoot = props.srcRoot;
    this.stateMachineArn = this.sagemakerStepFunction(props.snsTopic, props.trainingTable).stateMachineArn;
  }

  private createSagemakerTrainingJob() {
    return new sfn_tasks.SageMakerCreateTrainingJob(
      this.scope,
      'TrainModel',
      {
        trainingJobName: sfn.JsonPath.stringAt('$.JobName'),
        algorithmSpecification: {
          algorithmName: 'stable-diffusion-byoc',
          trainingImage: sfn_tasks.DockerImage.fromRegistry(
            '763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-inference:1.8.0-cpu-py3',
          ),
          trainingInputMode: sfn_tasks.InputMode.FILE,
        },
        inputDataConfig: [
          {
            channelName: 'train',
            dataSource: {
              s3DataSource: {
                s3DataType: sfn_tasks.S3DataType.S3_PREFIX,
                s3Location: sfn_tasks.S3Location.fromJsonExpression('$.S3Bucket_Train'),
              },
            },
          },
        ],
        // This should be where the checkpoint is stored
        outputDataConfig: {
          s3OutputLocation: sfn_tasks.S3Location.fromJsonExpression('$.S3Bucket_Output'),
        },
        resourceConfig: {
          instanceCount: 1,
          instanceType: new ec2.InstanceType(
            sfn.JsonPath.stringAt('$.InstanceType'),
          ),
          volumeSize: Size.gibibytes(50),
        }, // optional: default is 1 instance of EC2 `M4.XLarge` with `10GB` volume
        stoppingCondition: {
          maxRuntime: Duration.hours(2),
        }, // optional: default is 1 hour
      },
    );
  }

  private sagemakerStepFunction(snsTopic: sns.Topic, trainingTable: dynamodb.Table): sfn.StateMachine {
    // Step Function Creation initial process
    // Initial step to receive request from API Gateway and start training job
    const trainingJob = this.createSagemakerTrainingJob();

    // Step to store training id into DynamoDB after training job complete
    const storeTrainingId = new sfn_tasks.LambdaInvoke(
      this.scope,
      'StoreTrainingId',
      {
        lambdaFunction: new lambda.DockerImageFunction(
          this.scope,
          'StoreTrainingIdFunction',
          {
            code: lambda.DockerImageCode.fromImageAsset(`${this.srcRoot}/train`),
            timeout: Duration.minutes(15),
            memorySize: 3008,
            environment: {
              TABLE_NAME: trainingTable.tableName,
              JOB_NAME: sfn.JsonPath.stringAt('$.JobName'),
            },
          },
        ),
        outputPath: '$.Payload',
      },
    );

    // Step to create endpoint configuration
    const createEndpointConfig = new sfn_tasks.SageMakerCreateEndpointConfig(
      this.scope,
      'CreateEndpointConfig',
      {
        endpointConfigName: sfn.JsonPath.stringAt('$.JobName'),
        productionVariants: [
          {
            initialInstanceCount: 1,
            instanceType: new ec2.InstanceType(
              sfn.JsonPath.stringAt('$.InstanceType'),
            ),
            modelName: sfn.JsonPath.stringAt('$.JobName'),
            variantName: 'AllTraffic',
          },
        ],
      },
    );

    // Step to create endpoint
    const createEndpoint = new sfn_tasks.SageMakerCreateEndpoint(
      this.scope,
      'CreateEndpoint',
      {
        endpointName: sfn.JsonPath.stringAt('$.JobName'),
        endpointConfigName: sfn.JsonPath.stringAt('$.JobName'),
      },
    );

    // Step to send SNS notification
    const sendNotification = new sfn_tasks.SnsPublish(
      this.scope,
      'SendNotification',
      <SnsPublishProps>{
        topic: snsTopic,
        message: sfn.TaskInput.fromText('Training job completed'),
      },
    );

    // Create Step Function
    return new sfn.StateMachine(this.scope, 'TrainDeployStateMachine', <StateMachineProps>{
      definition: trainingJob
        .next(storeTrainingId)
        .next(createEndpointConfig)
        .next(createEndpoint)
        .next(sendNotification),
      role: this.sagemakerRole(snsTopic.topicArn),
    });
  }


  private sagemakerRole(snsTopicArn: string): iam.Role {
    const sagemakerRole = new iam.Role(this.scope, 'SagemakerTrainRole', {
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
          'sagemaker:ListProcessingJobsForHyperParameterTuningJob',
        ],
        resources: ['*'],
      }),
    );

    // Add S3 permissions to the role
    sagemakerRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          's3:ListBucket',
          's3:GetObject',
          's3:PutObject',
          's3:DeleteObject',
        ],
        resources: ['*'],
      }),
    );
    // Add SNS permissions to the role
    sagemakerRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ['sns:Publish'],
        resources: [snsTopicArn],
      }),
    );

    return sagemakerRole;
  }
}