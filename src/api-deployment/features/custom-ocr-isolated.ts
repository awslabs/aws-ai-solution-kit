import { CustomResource, Duration, RemovalPolicy, Size } from 'aws-cdk-lib';
import { Deployment, LambdaIntegration, RestApi } from 'aws-cdk-lib/aws-apigateway';
import { Peer, Port, SecurityGroup, SubnetType, Vpc } from 'aws-cdk-lib/aws-ec2';
import { Repository } from 'aws-cdk-lib/aws-ecr';
import { FileSystem as efsFileSystem, LifecyclePolicy, PerformanceMode, ThroughputMode } from 'aws-cdk-lib/aws-efs';
import { DockerImageCode, DockerImageFunction, FileSystem } from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';
import { APIFeature } from '../../api-feature';
import { FeatureNestedStack, FeatureNestedStackProps } from '../feature-nested-stack';

/**
 * This stack for custom OCR will not create a PUBLIC subnets for VPC, it
 * will not allocate an elastic IP (EIP) when creating VPC, so the API
 * request only accept image Base64 format.
 */
export class CustomOCRIsolatedFeatureNestedStack extends FeatureNestedStack {
  constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {

    super(scope, id, props);
    const featureName = 'custom-ocr';
    this.templateOptions.description = '(SO8023-custom-ocr) - AI Solution Kit - Custom OCR. Template version v1.2.0. See https://awslabs.github.io/aws-ai-solution-kit/en/deploy-custom-ocr.';

    const featureVPC = new Vpc(this, featureName.toLowerCase(), {
      cidr: '10.0.0.0/16',
      natGateways: 0,
      maxAzs: 1,
      subnetConfiguration: [
        {
          name: 'private',
          subnetType: SubnetType.PRIVATE_ISOLATED,
          cidrMask: 28,
        },
      ],
    });

    const featureSecurityGroup = new SecurityGroup(this, 'SecurityGroup', { vpc: featureVPC });
    featureSecurityGroup.addIngressRule(Peer.anyIpv4(), Port.allTraffic());
    const lfs = new efsFileSystem(this, `${featureName}-efs`, {
      vpc: featureVPC,
      encrypted: true,
      lifecyclePolicy: LifecyclePolicy.AFTER_14_DAYS,
      performanceMode: PerformanceMode.GENERAL_PURPOSE,
      throughputMode: ThroughputMode.PROVISIONED,
      provisionedThroughputPerSecond: Size.mebibytes(10),
      removalPolicy: RemovalPolicy.DESTROY,
    });
    // create a new access point from the filesystem
    const accessPoint = lfs.addAccessPoint('AccessPoint', {
      path: '/efs',
      createAcl: {
        ownerUid: '1000',
        ownerGid: '1000',
        permissions: '777',
      },
      // enforce the POSIX identity so lambda function will access with this identity
      posixUser: {
        uid: '1000',
        gid: '1000',
      },
    });

    const featureEFS = FileSystem.fromEfsAccessPoint(accessPoint, '/mnt/custom-ocr');

    const featureRepository = new Repository(this, `ai-solution-kit-${featureName}`, {
      repositoryName: `ai-solution-kit-${featureName}`,
      removalPolicy: RemovalPolicy.RETAIN,
    });

    if (props.ecrDeployment != null) {
      const ecrCR = new CustomResource(this, 'deployECRImage', {
        serviceToken: props.ecrDeployment.serviceToken,
        resourceType: 'Custom::AISolutionKitECRLambda',
        properties: {
          SrcImage: `docker://${props.ecrRegistry}/custom-ocr:latest`,
          DestImage: `docker://${featureRepository.repositoryUri}`,
          RepositoryName: `${featureRepository.repositoryName}`,
        },
      });
      const appFunction = new DockerImageFunction(
        this,
        `${featureName}App`,
        {
          code: DockerImageCode.fromEcr(
            Repository.fromRepositoryName(this, `${featureName}Lambda`, featureRepository.repositoryName),
            {
              tag: 'latest',
            },
          ),
          timeout: Duration.seconds(29),
          memorySize: 8192,
          vpc: featureVPC,
          // allowPublicSubnet: true,
          vpcSubnets: {
            subnetType: SubnetType.PRIVATE_ISOLATED,
          },
          securityGroups: [featureSecurityGroup],
          filesystem: featureEFS,
        },
      );
      appFunction.node.addDependency(ecrCR);
      const rootRestApi = RestApi.fromRestApiAttributes(this, 'client-api', {
        restApiId: props.restApi.restApiId,
        rootResourceId: props.restApi.root.resourceId,
      });
      const deployment = new Deployment(this, 'feature_deployment', {
        api: rootRestApi,
        retainDeployments: true,
      });
      const resource = rootRestApi.root.addResource(`${featureName}`);
      const post = resource.addMethod('POST', new LambdaIntegration(appFunction, { proxy: true }), {
        authorizationType: props.customAuthorizationType,
      });

      const apiProvider = new CustomResource(this, 'apiProvider', {
        serviceToken: props.updateCustomResourceProvider.serviceToken,
        resourceType: 'Custom::AISolutionKitApiProvider',
        properties: {
          featureName: featureName,
        },
        removalPolicy: RemovalPolicy.DESTROY,
      });
      apiProvider.node.addDependency(post);
    }
  }
}
