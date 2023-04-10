import {
  CfnParameter,
  Stack,
  StackProps,
  aws_sns as sns,
  aws_sns_subscriptions as sns_subscriptions,
  aws_dynamodb as dynamodb,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { RestApiGateway, SagemakerTrainApi } from './rest-api-gateway';
import { SagemakerTrainStateMachine } from './sagemaker-train-state-machine';


export class SdTrainDeployStack extends Stack {

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const snsTopic = this.createSns();
    // Create DynamoDB table to store training job id
    const trainingTable = new dynamodb.Table(this, 'TrainingTable', {
      tableName: 'TrainingTable',
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
    });
    const stateMachine = new SagemakerTrainStateMachine(this, {
      snsTopic: snsTopic,
      trainingTable: trainingTable,
    });

    const apiGateway = new RestApiGateway(this);
    // POST /train
    new SagemakerTrainApi(this, {
      api: apiGateway.apiGateway,
      apiKey: stateMachine.stateMachineArn,
      stateMachineArn: apiGateway.apiKey,
      apiResource: 'train-deploy',
    });
  }

  private createSns(): sns.Topic {
    // CDK parameters for SNS email address
    const emailParam = new CfnParameter(this, 'email', {
      type: 'String',
      description: 'Email address to receive notifications',
      default: 'example@example.com',
    });

    // Create SNS topic for notifications
    const snsTopic = new sns.Topic(this, 'StableDiffusionSnsTopic');

    // Subscribe user to SNS notifications
    snsTopic.addSubscription(
      new sns_subscriptions.EmailSubscription(emailParam.valueAsString),
    );

    return snsTopic;
  }
}
