import { PythonFunction, PythonFunctionProps } from '@aws-cdk/aws-lambda-python-alpha';
import {
  Aws,
  aws_apigateway as apigw,
  aws_apigateway,
  aws_dynamodb,
  aws_ecr,
  aws_iam as iam,
  aws_iam,
  aws_lambda,
  aws_s3,
  aws_sns,
  aws_stepfunctions as sfn,
  aws_stepfunctions_tasks as sfn_tasks,
  CustomResource,
  Duration,
  RemovalPolicy,
} from 'aws-cdk-lib';
import { MethodOptions } from 'aws-cdk-lib/aws-apigateway/lib/method';
import { Effect } from 'aws-cdk-lib/aws-iam';
import { Architecture, Runtime } from 'aws-cdk-lib/aws-lambda';
import * as stepfunctions from 'aws-cdk-lib/aws-stepfunctions';
import { StateMachineProps } from 'aws-cdk-lib/aws-stepfunctions/lib/state-machine';
import { LambdaInvokeProps } from 'aws-cdk-lib/aws-stepfunctions-tasks/lib/lambda/invoke';
import { Construct } from 'constructs';
import { DockerImageName, ECRDeployment } from '../cdk-ecr-deployment/lib';

export interface UpdateTrainJobApiProps{
  router: aws_apigateway.Resource;
  httpMethod: string;
  modelTable: aws_dynamodb.Table;
  trainTable: aws_dynamodb.Table;
  srcRoot: string;
  s3Bucket: aws_s3.Bucket;
  commonLayer: aws_lambda.LayerVersion;
  checkpointTable: aws_dynamodb.Table;
  userTopic: aws_sns.Topic;
}

export class UpdateTrainJobApi {

  private readonly id: string;
  private readonly scope: Construct;
  private readonly srcRoot: string;
  private readonly modelTable: aws_dynamodb.Table;
  private readonly layer: aws_lambda.LayerVersion;
  private readonly s3Bucket: aws_s3.Bucket;
  private readonly httpMethod: string;
  private readonly router: aws_apigateway.Resource;
  private readonly trainTable: aws_dynamodb.Table;
  private readonly checkpointTable: aws_dynamodb.Table;
  private readonly sagemakerTrainRole: aws_iam.Role;
  private readonly dockerRepo: aws_ecr.Repository;
  private readonly customJob: CustomResource;
  private readonly trainingStateMachine: sfn.StateMachine;
  private readonly userSnsTopic: aws_sns.Topic;
  private readonly sfnLambdaRole: aws_iam.Role;

  private readonly srcImg: string = 'public.ecr.aws/v1y2w4o9/aigc-webui-dreambooth-training:latest';
  private readonly instanceType: string = 'ml.g4dn.2xlarge';

  constructor(scope: Construct, id: string, props: UpdateTrainJobApiProps) {
    this.id = id;
    this.scope = scope;
    this.srcRoot = props.srcRoot;
    this.userSnsTopic = props.userTopic;
    this.modelTable = props.modelTable;
    this.checkpointTable = props.checkpointTable;
    this.layer = props.commonLayer;
    this.s3Bucket = props.s3Bucket;
    this.httpMethod = props.httpMethod;
    this.router = props.router;
    this.trainTable = props.trainTable;
    this.sagemakerTrainRole = this.sageMakerTrainRole();
    this.sfnLambdaRole = this.getStepFunctionLambdaRole();
    [this.dockerRepo, this.customJob] = this.trainImageInPrivateRepo(this.srcImg);

    this.trainingStateMachine = this.sagemakerStepFunction(this.userSnsTopic);
    this.trainingStateMachine.node.addDependency(this.customJob);

    this.updateTrainJobLambda();
  }

  private sageMakerTrainRole(): aws_iam.Role {
    const sagemakerRole = new aws_iam.Role(this.scope, `${this.id}-train-role`, {
      assumedBy: new aws_iam.ServicePrincipal('sagemaker.amazonaws.com'),
    });
    sagemakerRole.addManagedPolicy(aws_iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSageMakerFullAccess'));

    sagemakerRole.addToPolicy(new aws_iam.PolicyStatement({
      effect: Effect.ALLOW,
      actions: [
        's3:GetObject',
        's3:PutObject',
      ],
      resources: [
        `${this.s3Bucket.bucketArn}/*`,
        'arn:aws:s3:::*SageMaker*',
        'arn:aws:s3:::*Sagemaker*',
        'arn:aws:s3:::*sagemaker*',
      ],
    }));

    return sagemakerRole;
  }

  private getLambdaRole(): aws_iam.Role {
    const newRole = new aws_iam.Role(this.scope, `${this.id}-role`, {
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
      resources: [this.modelTable.tableArn, this.trainTable.tableArn, this.checkpointTable.tableArn],
    }));
    newRole.attachInlinePolicy(
      new iam.Policy(this.scope, 'getPolicy', {
        statements: [
          new iam.PolicyStatement({
            // Access to trigger the Step Function
            actions: ['states:StartExecution'],
            effect: iam.Effect.ALLOW,
            resources: [this.trainingStateMachine.stateMachineArn],
          }),
        ],
      }),
    );
    newRole.addToPolicy(new aws_iam.PolicyStatement({
      effect: Effect.ALLOW,
      actions: [
        'sagemaker:CreateTrainingJob',
      ],
      // resources: [`arn:aws:sagemaker:${Aws.REGION}:${Aws.ACCOUNT_ID}:endpoint/${this.sagemakerEndpoint.modelEndpoint.attrEndpointName}`],
      resources: [`arn:aws:sagemaker:${Aws.REGION}:${Aws.ACCOUNT_ID}:training-job/*`],
    }));

    newRole.addToPolicy(new aws_iam.PolicyStatement({
      effect: Effect.ALLOW,
      actions: [
        'iam:PassRole',
      ],
      resources: [this.sagemakerTrainRole.roleArn],
    }));

    newRole.addToPolicy(new aws_iam.PolicyStatement({
      effect: Effect.ALLOW,
      actions: [
        's3:GetObject',
        's3:PutObject',
        's3:DeleteObject',
        's3:ListBucket',
      ],
      resources: [
        `${this.s3Bucket.bucketArn}/*`,
        'arn:aws:s3:::*SageMaker*',
        'arn:aws:s3:::*Sagemaker*',
        'arn:aws:s3:::*sagemaker*',
      ],
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

  private getStepFunctionLambdaRole(): aws_iam.Role {
    const newRole = new aws_iam.Role(this.scope, `${this.id}-sfn-lambda-role`, {
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
      resources: [this.modelTable.tableArn, this.trainTable.tableArn, this.checkpointTable.tableArn],
    }));

    newRole.addToPolicy(new aws_iam.PolicyStatement({
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
      resources: [this.userSnsTopic.topicArn],
    }));

    newRole.addToPolicy(new aws_iam.PolicyStatement({
      effect: Effect.ALLOW,
      actions: [
        'sagemaker:DescribeTrainingJob',
      ],
      // resources: [`arn:aws:sagemaker:${Aws.REGION}:${Aws.ACCOUNT_ID}:endpoint/${this.sagemakerEndpoint.modelEndpoint.attrEndpointName}`],
      resources: [`arn:aws:sagemaker:${Aws.REGION}:${Aws.ACCOUNT_ID}:training-job/*`],
    }));

    newRole.addToPolicy(new aws_iam.PolicyStatement({
      effect: Effect.ALLOW,
      actions: [
        's3:GetObject',
        's3:PutObject',
        's3:DeleteObject',
        's3:ListBucket',
      ],
      resources: [
        `${this.s3Bucket.bucketArn}/*`,
        `${this.s3Bucket.bucketArn}`,
        'arn:aws:s3:::*SageMaker*',
        'arn:aws:s3:::*Sagemaker*',
        'arn:aws:s3:::*sagemaker*',
      ],
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

  private updateTrainJobLambda(): aws_lambda.IFunction {
    const lambdaFunction = new PythonFunction(this.scope, `${this.id}-updateTrainJob`, <PythonFunctionProps>{
      functionName: `${this.id}-update-train-job`,
      entry: `${this.srcRoot}/create_model`,
      architecture: Architecture.X86_64,
      runtime: Runtime.PYTHON_3_9,
      index: 'train_api.py',
      handler: 'update_train_job_api',
      timeout: Duration.seconds(900),
      role: this.getLambdaRole(),
      memorySize: 1024,
      environment: {
        S3_BUCKET: this.s3Bucket.bucketName,
        TRAIN_TABLE: this.trainTable.tableName,
        MODEL_TABLE: this.modelTable.tableName,
        CHECKPOINT_TABLE: this.checkpointTable.tableName,
        INSTANCE_TYPE: this.instanceType,
        TRAIN_JOB_ROLE: this.sagemakerTrainRole.roleArn,
        TRAIN_ECR_URL: `${this.dockerRepo.repositoryUri}:latest`,
        TRAINING_SAGEMAKER_ARN: this.trainingStateMachine.stateMachineArn,
        USER_EMAIL_TOPIC_ARN: this.userSnsTopic.topicArn,
      },
      layers: [this.layer],
    });
    lambdaFunction.node.addDependency(this.customJob);

    const createTrainJobIntegration = new apigw.LambdaIntegration(
      lambdaFunction,
      {
        proxy: false,
        integrationResponses: [{ statusCode: '200' }],
      },
    );
    this.router.addMethod(this.httpMethod, createTrainJobIntegration, <MethodOptions>{
      apiKeyRequired: true,
      methodResponses: [{
        statusCode: '200',
      }],
    });
    return lambdaFunction;
  }

  private checkTrainingJobStatusLambda(): aws_lambda.IFunction {
    return new PythonFunction(this.scope, `${this.id}-checkTrainingJobStatus`, <PythonFunctionProps>{
      functionName: `${this.id}-train-state-check`,
      entry: `${this.srcRoot}/create_model`,
      architecture: Architecture.X86_64,
      runtime: Runtime.PYTHON_3_9,
      index: 'train_api.py',
      role: this.sfnLambdaRole,
      handler: 'check_train_job_status',
      timeout: Duration.seconds(900),
      memorySize: 1024,
      environment: {
        S3_BUCKET: this.s3Bucket.bucketName,
        TRAIN_TABLE: this.trainTable.tableName,
        MODEL_TABLE: this.modelTable.tableName,
        CHECKPOINT_TABLE: this.checkpointTable.tableName,
        INSTANCE_TYPE: this.instanceType,
        TRAIN_JOB_ROLE: this.sagemakerTrainRole.roleArn,
        TRAIN_ECR_URL: `${this.dockerRepo.repositoryUri}:latest`,
        USER_EMAIL_TOPIC_ARN: this.userSnsTopic.topicArn,
      },
      layers: [this.layer],
    });
  }

  private processTrainingJobResultLambda(): aws_lambda.IFunction {
    return new PythonFunction(this.scope, `${this.id}-processTrainingJobResult`, <PythonFunctionProps>{
      functionName: `${this.id}-train-result-process`,
      entry: `${this.srcRoot}/create_model`,
      architecture: Architecture.X86_64,
      runtime: Runtime.PYTHON_3_9,
      role: this.sfnLambdaRole,
      index: 'train_api.py',
      handler: 'process_train_job_result',
      timeout: Duration.seconds(900),
      memorySize: 1024,
      environment: {
        S3_BUCKET: this.s3Bucket.bucketName,
        TRAIN_TABLE: this.trainTable.tableName,
        MODEL_TABLE: this.modelTable.tableName,
        CHECKPOINT_TABLE: this.checkpointTable.tableName,
        INSTANCE_TYPE: this.instanceType,
        TRAIN_JOB_ROLE: this.sagemakerTrainRole.roleArn,
        TRAIN_ECR_URL: `${this.dockerRepo.repositoryUri}:latest`,
        USER_EMAIL_TOPIC_ARN: this.userSnsTopic.topicArn,
      },
      layers: [this.layer],
    });
  }

  private trainImageInPrivateRepo(srcImage: string): [aws_ecr.Repository, CustomResource] {
    const dockerRepo = new aws_ecr.Repository(this.scope, `${this.id}-repo`, {
      repositoryName: 'aigc-train-utils',
      removalPolicy: RemovalPolicy.DESTROY,
      autoDeleteImages: true,
    });

    const ecrDeployment = new ECRDeployment(this.scope, `${this.id}-ecr-deploy`, {
      src: new DockerImageName(srcImage),
      dest: new DockerImageName(`${dockerRepo.repositoryUri}:latest`),
    });

    // trigger the custom resource lambda
    const customJob = new CustomResource(this.scope, `${this.id}-cr-image`, {
      serviceToken: ecrDeployment.serviceToken,
      resourceType: 'Custom::AIGCSolutionECRLambda',
      properties: {
        SrcImage: `docker://${srcImage}`,
        DestImage: `docker://${dockerRepo.repositoryUri}:latest`,
        RepositoryName: `${dockerRepo.repositoryName}`,
      },
    });
    customJob.node.addDependency(ecrDeployment);
    return [dockerRepo, customJob];
  }

  private sagemakerStepFunction(snsTopic: aws_sns.Topic): sfn.StateMachine {
    // Step to store training id into DynamoDB after training job complete
    const trainingJobCheckState = new sfn_tasks.LambdaInvoke(
      this.scope,
      `${this.id}-trainingJobCheckState`,
      <LambdaInvokeProps>{
        lambdaFunction: this.checkTrainingJobStatusLambda(),
        outputPath: '$.Payload',
      },
    );

    const processJobResult = new sfn_tasks.LambdaInvoke(
      this.scope,
      `${this.id}-processJobResult`,
        <LambdaInvokeProps>{
          lambdaFunction: this.processTrainingJobResultLambda(),
          outputPath: '$.Payload',
        },
    );

    const checkTrainingBranch = new stepfunctions.Choice(
      this.scope,
      'CheckTrainingBranch',
    );

    const waitStatusDeploymentTask = new stepfunctions.Wait(
      this.scope,
      'WaitTrainingJobStatus',
      {
        time: stepfunctions.WaitTime.duration(Duration.minutes(2)),
      },
    );

    // Create Step Function
    return new sfn.StateMachine(this.scope, `${this.id}-TrainDeployStateMachine`, <StateMachineProps>{
      definition: trainingJobCheckState
        .next(
          checkTrainingBranch
            .when(
              sfn.Condition.or(sfn.Condition.stringEquals(
                '$.status',
                'InProgress',
              ), sfn.Condition.stringEquals(
                '$.status',
                'Stopping',
              )),
              waitStatusDeploymentTask.next(trainingJobCheckState),
            ).otherwise(
              processJobResult,
            )
            .afterwards(),
        ),
      role: this.sagemakerRoleForStepFunction(snsTopic.topicArn),
    });
  }

  private sagemakerRoleForStepFunction(snsTopicArn: string): iam.Role {
    const sagemakerRole = new iam.Role(this.scope, `${this.id}-SagemakerTrainRole`, {
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