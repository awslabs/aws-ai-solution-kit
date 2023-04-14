import { PythonFunction, PythonFunctionProps } from '@aws-cdk/aws-lambda-python-alpha';
import {
  aws_dynamodb as dynamodb,
  aws_sns as sns,
  aws_iam as iam,
  aws_stepfunctions as sfn,
  aws_stepfunctions_tasks as sfn_tasks,
  Duration, aws_lambda, aws_dynamodb, aws_iam, aws_ecr, CustomResource, RemovalPolicy, aws_s3, aws_sagemaker,
} from 'aws-cdk-lib';
import { Effect, ServicePrincipal } from 'aws-cdk-lib/aws-iam';
import { Architecture, Runtime } from 'aws-cdk-lib/aws-lambda';
import { CfnEndpointConfigProps, CfnEndpointProps, CfnModelProps } from 'aws-cdk-lib/aws-sagemaker';
import { StateMachineProps } from 'aws-cdk-lib/aws-stepfunctions/lib/state-machine';
import { LambdaInvokeProps } from 'aws-cdk-lib/aws-stepfunctions-tasks/lib/lambda/invoke';
import { SnsPublishProps } from 'aws-cdk-lib/aws-stepfunctions-tasks/lib/sns/publish';
import { Construct } from 'constructs';
import { DockerImageName, ECRDeployment } from '../cdk-ecr-deployment/lib';


export interface CreateModelStateMachineProps {
  snsTopic: sns.Topic;
  modelTable: dynamodb.Table;
  srcRoot: string;
  s3Bucket: aws_s3.Bucket;
  layer: aws_lambda.LayerVersion;
}

export class CreateModelStateMachine {
  private readonly id: string;

  public readonly stateMachine: sfn.StateMachine;

  private readonly scope: Construct;
  private readonly srcRoot: string;
  private readonly layer: aws_lambda.LayerVersion;
  private readonly modelTable: aws_dynamodb.Table;
  private readonly sagemakerEndpointName: string;
  private readonly s3Bucket: aws_s3.Bucket;

  private readonly dockerRepo: aws_ecr.Repository;
  private readonly imageUrl: string ='public.ecr.aws/v1y2w4o9/aigc-webui-dreambooth-create-model:latest';
  private readonly createModelEndpoint: aws_sagemaker.CfnModel;


  constructor(scope: Construct, id: string, props: CreateModelStateMachineProps) {
    this.scope = scope;
    this.id = id;
    this.srcRoot = props.srcRoot;
    this.modelTable = props.modelTable;
    this.s3Bucket = props.s3Bucket;
    this.layer = props.layer;

    const dockerDeployment = new CreateModelInferenceImage(this.scope, this.imageUrl);
    this.dockerRepo = dockerDeployment.dockerRepo;

    // create sagemaker endpoint
    const sagemakerEndpoint = new CreateModelSageMakerEndpoint(this.scope, 'aigc-createmodel', {
      machineType: 'ml.g4dn.2xlarge',
      outputFolder: 'models',
      primaryContainer: `${this.dockerRepo.repositoryUri}:latest`,
      s3OutputBucket: this.s3Bucket,
    });
    this.createModelEndpoint = sagemakerEndpoint.model;
    this.sagemakerEndpointName = sagemakerEndpoint.modelEndpoint.attrEndpointName;
    this.createModelEndpoint.node.addDependency(dockerDeployment.customJob);

    this.stateMachine = this.sagemakerStepFunction(props.snsTopic);
    this.stateMachine.node.addDependency(sagemakerEndpoint.modelEndpoint);
  }

  private createInferenceJob(): aws_lambda.IFunction {
    return new PythonFunction(this.scope, `${this.id}-infer`, <PythonFunctionProps>{
      functionName: `${this.id}-infer`,
      entry: `${this.srcRoot}/create_model`,
      architecture: Architecture.X86_64,
      runtime: Runtime.PYTHON_3_9,
      index: 'create_model_sfn.py',
      handler: 'create_sagemaker_inference',
      timeout: Duration.minutes(15),
      memorySize: 1024,
      environment: {
        DYNAMODB_TABLE: this.modelTable.tableName,
        SAGEMAKER_ENDPOINT_NAME: this.sagemakerEndpointName,
        S3_BUCKET: this.s3Bucket.bucketName,
      },
      layers: [this.layer],
    });
  }

  private sagemakerStepFunction(snsTopic: sns.Topic): sfn.StateMachine {
    const createInferenceJob = new sfn_tasks.LambdaInvoke(
      this.scope,
      `${this.id}-create-inference`,
      <LambdaInvokeProps>{
        lambdaFunction: this.createInferenceJob(),
        outputPath: '$.Payload',
      },
    );

    // Step to send SNS notification
    const sendNotification = new sfn_tasks.SnsPublish(
      this.scope,
      `${this.id}-SendNotification`,
      <SnsPublishProps>{
        topic: snsTopic,
        message: sfn.TaskInput.fromText('Create Model job completed'),
      },
    );

    // const waitInference = new sfn.Wait(this.scope, `${this.id}-wait5min`, {
    //   time: WaitTime.duration(Duration.minutes(5)),
    // });


    // Create Step Function
    return new sfn.StateMachine(this.scope, 'CreateModelDeployStateMachine', <StateMachineProps>{
      definition: createInferenceJob
        .next(sendNotification),
      role: this.sagemakerRole(snsTopic.topicArn),
    });
  }

  private sagemakerRole(snsTopicArn: string): iam.Role {
    const sagemakerRole = new iam.Role(this.scope, 'SagemakerEndpointRole', {
      assumedBy: new iam.ServicePrincipal('states.amazonaws.com'),
    });
    // Add SageMaker permissions to the role
    sagemakerRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          'sagemaker:DescribeTrainingJob',
          'sagemaker:DescribeEndpoint',
          'sagemaker:DescribeEndpointConfig',
          'sagemaker:DescribeModel',
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

    sagemakerRole.addToPolicy(new aws_iam.PolicyStatement({
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

class CreateModelInferenceImage {

  private readonly id = 'aigc-createmodel-inf';
  public readonly ecrDeployment: ECRDeployment;
  public readonly dockerRepo: aws_ecr.Repository;
  public readonly customJob: CustomResource;

  constructor(scope: Construct, srcImage: string) {

    this.dockerRepo = new aws_ecr.Repository(scope, `${this.id}-repo`, {
      repositoryName: 'aigc-create-model',
      removalPolicy: RemovalPolicy.DESTROY,
      autoDeleteImages: true,
    });

    this.ecrDeployment = new ECRDeployment(scope, `${this.id}-ecr-deploy`, {
      src: new DockerImageName(srcImage),
      dest: new DockerImageName(`${this.dockerRepo.repositoryUri}:latest`),
    });

    // trigger the lambda
    this.customJob = new CustomResource(scope, `${this.id}-cr-image`, {
      serviceToken: this.ecrDeployment.serviceToken,
      resourceType: 'Custom::AIGCSolutionECRLambda',
      properties: {
        SrcImage: `docker://${srcImage}`,
        DestImage: `docker://${this.dockerRepo.repositoryUri}:latest`,
        RepositoryName: `${this.dockerRepo.repositoryName}`,
      },
    });
    this.customJob.node.addDependency(this.ecrDeployment);
  }
}


interface CreateModelSageMakerEndpointProps {
  primaryContainer: string;
  outputFolder: string;
  s3OutputBucket: aws_s3.Bucket;
  machineType: string;
  // successSnsTopic: string;
  // failureSnsTopic: string;
}

class CreateModelSageMakerEndpoint {

  private readonly id;

  private readonly s3Bucket: aws_s3.Bucket;
  public readonly model: aws_sagemaker.CfnModel;
  public readonly modelConfig: aws_sagemaker.CfnEndpointConfig;
  public readonly modelEndpoint: aws_sagemaker.CfnEndpoint;

  constructor(scope: Construct, id: string, props: CreateModelSageMakerEndpointProps) {
    this.s3Bucket = props.s3OutputBucket;
    this.id = id;

    this.model = new aws_sagemaker.CfnModel(scope, `${this.id}-model`, <CfnModelProps>{
      executionRoleArn: this.role(scope).roleArn,
      modelName: `${this.id}-cdk-sample-model`,
      primaryContainer: {
        // image: '991301791329.dkr.ecr.us-west-1.amazonaws.com/ecr-deployment-tryout-20-repo:latest',
        image: props.primaryContainer,
      },
    });


    this.modelConfig = new aws_sagemaker.CfnEndpointConfig(scope, `${this.id}-model-config`, <CfnEndpointConfigProps>{
      endpointConfigName: `${this.id}-config`,
      productionVariants: [
        {
          modelName: this.model.modelName,
          initialVariantWeight: 1.0,
          // instanceType: 'ml.g4dn.2xlarge',
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
          // notificationConfig: {
          //     successTopic:
          // }
        },
      },
    });

    this.modelConfig.node.addDependency(this.model);

    this.modelEndpoint = new aws_sagemaker.CfnEndpoint(scope, `${this.id}-endpoint`, <CfnEndpointProps>{
      endpointConfigName: this.modelConfig.endpointConfigName,
      endpointName: `${this.id}-endpoint`,
    });
    this.modelEndpoint.node.addDependency(this.modelConfig);
  }

  private role(scope: Construct): aws_iam.Role {
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
    return sagemakerRole;
  }
}