import {
  aws_sns as sns,
  aws_iam as iam,
  aws_stepfunctions as sfn,
  aws_stepfunctions_tasks as sfn_tasks,
  aws_ec2 as ec2,
} from 'aws-cdk-lib';
import { StateMachineProps } from 'aws-cdk-lib/aws-stepfunctions/lib/state-machine';
import { SnsPublishProps } from 'aws-cdk-lib/aws-stepfunctions-tasks/lib/sns/publish';
import { Construct } from 'constructs';

export interface SagemakerInferenceProps {
  snsTopic: sns.Topic;
}

export class SagemakerInferenceStateMachineBackup {
  public readonly stateMachineArn: string;
  private readonly scope: Construct;

  constructor(scope: Construct, props: SagemakerInferenceProps) {
    this.scope = scope;
    this.stateMachineArn = this.sagemakerStepFunction(props.snsTopic).stateMachineArn;
  }

  private sagemakerStepFunction(snsTopic: sns.Topic): sfn.StateMachine {
    // Step Function Creation initial process
    // Initial step to receive request from API Gateway and start training job

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
    return new sfn.StateMachine(this.scope, 'CreateEndPointStateMachine', <StateMachineProps>{
      definition: 
        createEndpointConfig
        .next(createEndpoint)
        .next(sendNotification),
      role: this.sagemakerRole(snsTopic.topicArn),
    });
  }


  private sagemakerRole(snsTopicArn: string): iam.Role {
    const sagemakerRole = new iam.Role(this.scope, 'SagemakerRole', {
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