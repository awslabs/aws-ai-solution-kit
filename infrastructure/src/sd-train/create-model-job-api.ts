import { PythonFunction, PythonFunctionProps } from '@aws-cdk/aws-lambda-python-alpha';
import {
  aws_apigateway,
  aws_apigateway as apigw,
  aws_dynamodb, aws_ecr,
  aws_iam,
  aws_lambda,
  aws_s3, aws_sagemaker, CustomResource,
  Duration, RemovalPolicy,
} from 'aws-cdk-lib';

import { MethodOptions } from 'aws-cdk-lib/aws-apigateway/lib/method';
import { Effect, ServicePrincipal } from 'aws-cdk-lib/aws-iam';
import { Architecture, Runtime } from 'aws-cdk-lib/aws-lambda';

import { CfnEndpointConfigProps, CfnEndpointProps, CfnModelProps } from 'aws-cdk-lib/aws-sagemaker';
import { Construct } from 'constructs';
import { DockerImageName, ECRDeployment } from '../cdk-ecr-deployment/lib';


export interface CreateModelJobApiProps {
  router: aws_apigateway.Resource;
  httpMethod: string;
  trainingTable: aws_dynamodb.Table;
  srcRoot: string;
  s3Bucket: aws_s3.Bucket;
  commonLayer: aws_lambda.LayerVersion;
}

export class CreateModelJobApi {
  private readonly src;
  private readonly router: aws_apigateway.Resource;
  private readonly httpMethod: string;
  private readonly scope: Construct;
  private readonly trainingTable: aws_dynamodb.Table;
  private readonly s3Bucket: aws_s3.Bucket;
  private readonly layer: aws_lambda.LayerVersion;

  private readonly ecrDeployment: ECRDeployment;
  private readonly createModelEndpoint: aws_sagemaker.CfnModel;
  private readonly dockerRepo: aws_ecr.Repository;

  private readonly baseId: string = 'aigc-create-train-job';
  private readonly imageUrl: string ='public.ecr.aws/v1y2w4o9/aigc-webui-dreambooth-create-model:latest';

  constructor(scope: Construct, props: CreateModelJobApiProps) {
    this.scope = scope;
    this.router = props.router;
    this.httpMethod = props.httpMethod;
    this.trainingTable = props.trainingTable;
    this.src = props.srcRoot;
    this.s3Bucket = props.s3Bucket;
    this.layer = props.commonLayer;

    const dockerDeployment = new CreateModelInferenceImage(this.scope, this.imageUrl);
    this.ecrDeployment = dockerDeployment.ecrDeployment;
    this.dockerRepo = dockerDeployment.dockerRepo;

    // create sagemaker endpoint
    const sagemakerEndpoint = new CreateModelSageMakerEndpoint(this.scope, 'aigc-createmodel', {
      machineType: 'ml.g4dn.2xlarge',
      outputFolder: 'models',
      primaryContainer: `${this.dockerRepo.repositoryUri}:latest`,
      s3OutputBucket: this.s3Bucket,
    });
    this.createModelEndpoint = sagemakerEndpoint.model;
    this.createModelEndpoint.node.addDependency(this.ecrDeployment);

    this.createModelJobApi();
  }

  private iamRole(): aws_iam.Role {
    const newRole = new aws_iam.Role(this.scope, `${this.baseId}-role`, {
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
      resources: [this.trainingTable.tableArn],
    }));

    newRole.addToPolicy(new aws_iam.PolicyStatement({
      effect: Effect.ALLOW,
      actions: [
        's3:GetObject',
        's3:PutObject',
      ],
      resources: [`${this.s3Bucket.bucketArn}/*`],
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

  private createModelJobApi() {
    const lambdaFunction = new PythonFunction(this.scope, `${this.baseId}-handler`, <PythonFunctionProps>{
      functionName: `${this.baseId}-model`,
      entry: `${this.src}/create_model`,
      architecture: Architecture.X86_64,
      runtime: Runtime.PYTHON_3_9,
      index: 'create_model_job_api.py',
      handler: 'create_model_api',
      timeout: Duration.seconds(900),
      role: this.iamRole(),
      memorySize: 1024,
      environment: {
        DYNAMODB_TABLE: this.trainingTable.tableName,
        S3_BUCKET: this.s3Bucket.bucketName,
      },
      layers: [this.layer],
    });
    lambdaFunction.node.addDependency(this.ecrDeployment, this.createModelEndpoint);
    const createModelIntegration = new apigw.LambdaIntegration(
      lambdaFunction,
      {
        proxy: false,
        integrationResponses: [{ statusCode: '200' }],
      },
    );
    this.router.addMethod(this.httpMethod, createModelIntegration, <MethodOptions>{
      apiKeyRequired: true,
      methodResponses: [{
        statusCode: '200',
      }],
    });
  }
}

class CreateModelInferenceImage {

  private readonly id = 'aigc-createmodel-inf';
  public readonly ecrDeployment: ECRDeployment;
  public readonly dockerRepo: aws_ecr.Repository;

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
    new CustomResource(scope, `${this.id}-cr-image`, {
      serviceToken: this.ecrDeployment.serviceToken,
      resourceType: 'Custom::AIGCSolutionECRLambda',
      properties: {
        SrcImage: `docker://${srcImage}`,
        DestImage: `docker://${this.dockerRepo.repositoryUri}:latest`,
        RepositoryName: `${this.dockerRepo.repositoryName}`,
      },
    });
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
    const sagemakerRole = new aws_iam.Role(scope, `${this.id}-sagemaker-role`, {
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