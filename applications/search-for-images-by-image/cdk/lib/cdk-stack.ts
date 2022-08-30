import { Aws,Stack, StackProps,RemovalPolicy,Duration,CfnOutput,CfnParameter } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { aws_s3 as s3 } from 'aws-cdk-lib';
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as iam from 'aws-cdk-lib/aws-iam';
import * as os from 'aws-cdk-lib/aws-opensearchservice';
import * as ec2 from 'aws-cdk-lib/aws-ec2';

export interface AISolutionKitWorkshopStackProps extends StackProps {
  readonly lambdaMemorySize?: number;
}

export class CdkStack extends Stack {
  constructor(scope: Construct, id: string, props?: AISolutionKitWorkshopStackProps) {
    super(scope, id, props);
    const paramStagebaseURL = new CfnParameter(this, "StagebaseURL", {
      type: "String",
      description: "StagebaseURL value of AI Solution Kit output."});
    const paramOpenSearchInstanceType = new CfnParameter(this, "InstanceType", {
      type: "String",
      default: "c5.large.search",
      allowedValues:["c5.large.search","r5.xlarge.search","r5.12xlarge.search"],
      description: "OpenSearch instance type."});

    const bucket = new s3.Bucket(this, 'bucket', {
      removalPolicy: RemovalPolicy.DESTROY,
      autoDeleteObjects: true
    });

    const domainName = "ask-workshop";
    // const domain = new os.Domain(this, 'Domain', {
    //   domainName: domainName,
    //   version: os.EngineVersion.OPENSEARCH_1_2,
    //   capacity: {
    //     dataNodes: 1,
    //     dataNodeInstanceType: "t3.small.search",
    //   },
    //   ebs: {
    //     volumeSize: 10,
    //     volumeType: ec2.EbsDeviceVolumeType.GENERAL_PURPOSE_SSD,
    //   },
    //   nodeToNodeEncryption: true,
    //   encryptionAtRest: {
    //     enabled: true,
    //   },
    //   accessPolicies: [new iam.PolicyStatement({
    //     actions: ["es:*"],
    //     principals:[new iam.AccountRootPrincipal()],
    //     resources: [`arn:${Aws.PARTITION}:es:${Aws.REGION}:${Aws.ACCOUNT_ID}:domain/${domainName}/*`,],
    //     })],
    //   removalPolicy: RemovalPolicy.DESTROY,
    // });
    const myPolicy={
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "AWS": `${Aws.ACCOUNT_ID}`
          },
          "Action": "es:*",
          "Resource": `arn:${Aws.PARTITION}:es:${Aws.REGION}:${Aws.ACCOUNT_ID}:domain/${domainName}/*`
        }
      ]
    }
    const domain = new os.CfnDomain(this, 'Domain', {
      domainName: domainName,
      engineVersion: os.EngineVersion.OPENSEARCH_1_2.version,
      clusterConfig: {
        instanceCount: 1,
        instanceType: paramOpenSearchInstanceType.value.toString(),
      },
      ebsOptions: {
        ebsEnabled: true,
        volumeSize: 10,
        volumeType: ec2.EbsDeviceVolumeType.GENERAL_PURPOSE_SSD,
      },
      domainEndpointOptions: {
        enforceHttps: true,
      },
      accessPolicies: myPolicy,
    });
    domain.applyRemovalPolicy(RemovalPolicy.DESTROY)

    const layerBase = new lambda.LayerVersion(this, 'ASKLayerBase', {
      // code: lambda.Code.fromBucket(s3.Bucket.fromBucketName(this,"ArtifactBucketBase","ask-workshop-data"),"layer/base_python3.8.zip"),
      code: lambda.Code.fromBucket(s3.Bucket.fromBucketName(this,"ArtifactBucketBase",`aws-gcr-solutions-workshop-${Aws.REGION}`),"ai-solution-kit/v1.0.0/layer.zip"),
      description: 'AI Solution Kit workshop base layer.',
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_8],
      removalPolicy: RemovalPolicy.DESTROY
    });

    const myRole = new iam.Role(this, 'Role', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
    });
    var lambdaMemorySize = 10240;
    if (props?.lambdaMemorySize){
      lambdaMemorySize = props?.lambdaMemorySize
    }
    const handler = new lambda.Function(this, "lambda", {
      runtime: lambda.Runtime.PYTHON_3_8,
      code: lambda.Code.fromAsset("resources"),
      handler: "main.handler",
      memorySize: lambdaMemorySize,
      timeout: Duration.minutes(15),
      environment: {
        bucket_name: bucket.bucketName,
        StagebaseURL: paramStagebaseURL.value.toString(),
        // es_host: domain.domainEndpoint,
        es_host: domain.attrDomainEndpoint,
        region: Aws.REGION,
      },
      layers: [layerBase],
      role: myRole,
    });

    myRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'));
    myRole.attachInlinePolicy(new iam.Policy(this, 'policy', {
      policyName: "workshop",
      statements: [new iam.PolicyStatement({
        actions: ["s3:GetObject",
          "s3:ListBucket",
          "es:ESHttpPost",
          "es:ESHttpPut",
          "es:ESHttpDelete",],
        resources: [bucket.bucketArn,
          `${bucket.bucketArn}/*`,
          `${domain.attrArn}/*`],
        })],
      }));

    const api = new apigateway.RestApi(this, "API", {
      restApiName: "AI Solution Kit workshop",
      description: "AI Solution Kit workshop example.",
      deploy: false,
      endpointConfiguration: {
        types: [apigateway.EndpointType.REGIONAL],
      },
      defaultCorsPreflightOptions: {
        allowHeaders: [
          'Content-Type',
          'X-Amz-Date',
          'Authorization',
          'X-Api-Key',
        ],
        allowMethods: ['GET', 'POST', 'OPTION'],
        allowCredentials: true,
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
      },
    });

    const resource = api.root;
    resource.addProxy({
      anyMethod: true,
      defaultIntegration: new apigateway.LambdaIntegration(handler, { proxy: true }),
    });

    resource.addMethod('GET',
      new apigateway.LambdaIntegration(handler, { proxy: true }),
    );

    const deployment = new apigateway.Deployment(this, 'new_deployment', {
      api: api,
    });

    const deploymentStage = new apigateway.Stage(this, 'Stage-demo', {
      stageName: "demo",
      deployment: deployment,
      dataTraceEnabled: false,
      loggingLevel: apigateway.MethodLoggingLevel.INFO,
    });

    //output
    new CfnOutput(this, 'InvokeBaseUrl', { value: deploymentStage.urlForPath()});
    new CfnOutput(this, 's3Bucket', { value: bucket.bucketName });
  }
}
