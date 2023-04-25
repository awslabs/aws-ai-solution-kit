import { PythonFunction, PythonFunctionProps } from '@aws-cdk/aws-lambda-python-alpha';
import {
  aws_apigateway as apigw,
  aws_dynamodb,
  aws_ecr,
  aws_iam,
  aws_lambda,
  aws_s3,
  aws_sns,
  CustomResource,
  Duration,
  RemovalPolicy,
  Aws,
} from 'aws-cdk-lib';
import { MethodOptions } from 'aws-cdk-lib/aws-apigateway/lib/method';
import { Resource } from 'aws-cdk-lib/aws-apigateway/lib/resource';
import { Effect } from 'aws-cdk-lib/aws-iam';
import { Architecture, Runtime } from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';
import { CreateModelSageMakerEndpoint } from './create-model-endpoint';
import { DockerImageName, ECRDeployment } from '../cdk-ecr-deployment/lib';


export interface UpdateModelStatusRestApiProps {
  httpMethod: string;
  router: Resource;
  modelTable: aws_dynamodb.Table;
  srcRoot: string;
  commonLayer: aws_lambda.LayerVersion;
  s3Bucket: aws_s3.Bucket;
  snsTopic: aws_sns.Topic;
  checkpointTable: aws_dynamodb.Table;
}

export class UpdateModelStatusRestApi {

  private readonly imageUrl: string = 'public.ecr.aws/e2t2y5y0/aigc-webui-utils:latest';
  private readonly machineType: string = 'ml.g4dn.2xlarge';

  private readonly src;
  private readonly scope: Construct;
  private readonly modelTable: aws_dynamodb.Table;
  private readonly checkpointTable: aws_dynamodb.Table;
  private readonly layer: aws_lambda.LayerVersion;
  private readonly router: Resource;
  private readonly httpMethod: string;
  private readonly s3Bucket: aws_s3.Bucket;
  private readonly dockerRepo: aws_ecr.Repository;
  private readonly sagemakerEndpoint: CreateModelSageMakerEndpoint;

  private readonly baseId: string;

  constructor(scope: Construct, id: string, props: UpdateModelStatusRestApiProps) {
    this.scope = scope;
    this.router = props.router;
    this.baseId = id;
    this.modelTable = props.modelTable;
    this.httpMethod = props.httpMethod;
    this.src = props.srcRoot;
    this.layer = props.commonLayer;
    this.s3Bucket = props.s3Bucket;
    this.checkpointTable = props.checkpointTable;

    // create private image:
    const dockerDeployment = new CreateModelInferenceImage(this.scope, this.imageUrl);
    this.dockerRepo = dockerDeployment.dockerRepo;
    // create sagemaker endpoint
    this.sagemakerEndpoint = new CreateModelSageMakerEndpoint(this.scope, 'aigc-utils', {
      machineType: this.machineType,
      outputFolder: 'models',
      primaryContainer: `${this.dockerRepo.repositoryUri}:latest`,
      s3OutputBucket: this.s3Bucket,
      commonLayer: this.layer,
      modelTable: this.modelTable,
      rootSrc: this.src,
      userSnsTopic: props.snsTopic,
    });
    this.sagemakerEndpoint.model.node.addDependency(dockerDeployment.customJob);
    // create lambda to trigger
    this.updateModelJobApi();
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
      resources: [this.modelTable.tableArn, this.checkpointTable.tableArn],
    }));

    newRole.addToPolicy(new aws_iam.PolicyStatement({
      effect: Effect.ALLOW,
      actions: [
        'sagemaker:InvokeEndpointAsync',
      ],
      resources: [`arn:aws:sagemaker:${Aws.REGION}:${Aws.ACCOUNT_ID}:endpoint/${this.sagemakerEndpoint.modelEndpoint.attrEndpointName}`],
    }));

    newRole.addToPolicy(new aws_iam.PolicyStatement({
      effect: Effect.ALLOW,
      actions: [
        's3:GetObject',
        's3:PutObject',
        's3:DeleteObject',
        's3:ListBucket',
        's3:AbortMultipartUpload',
        's3:ListMultipartUploadParts',
        's3:ListBucketMultipartUploads',
      ],
      resources: [`${this.s3Bucket.bucketArn}/*`,
        'arn:aws:s3:::*SageMaker*',
        'arn:aws:s3:::*Sagemaker*',
        'arn:aws:s3:::*sagemaker*'],
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

  private updateModelJobApi() {
    const updateModelLambda = new PythonFunction(this.scope, `${this.baseId}-handler`, <PythonFunctionProps>{
      functionName: `${this.baseId}-update-model`,
      entry: `${this.src}/create_model`,
      architecture: Architecture.X86_64,
      runtime: Runtime.PYTHON_3_9,
      index: 'update_job_api.py',
      handler: 'update_model_job_api',
      timeout: Duration.seconds(900),
      role: this.iamRole(),
      memorySize: 1024,
      environment: {
        DYNAMODB_TABLE: this.modelTable.tableName,
        S3_BUCKET: this.s3Bucket.bucketName,
        SAGEMAKER_ENDPOINT_NAME: this.sagemakerEndpoint.modelEndpoint.attrEndpointName,
        CHECKPOINT_TABLE: this.checkpointTable.tableName,
      },
      layers: [this.layer],
    });
    updateModelLambda.node.addDependency(this.sagemakerEndpoint.modelEndpoint);

    const updateModelLambdaIntegration = new apigw.LambdaIntegration(
      updateModelLambda,
      {
        proxy: false,
        integrationResponses: [{ statusCode: '200' }],
      },
    );
    this.router.addMethod(this.httpMethod, updateModelLambdaIntegration, <MethodOptions>{
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
