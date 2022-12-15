import { CustomResource, RemovalPolicy } from 'aws-cdk-lib';
import { Repository } from 'aws-cdk-lib/aws-ecr';
import { Construct } from 'constructs';
import { FeatureNestedStack, FeatureNestedStackProps } from '../../feature-nested-stack';
import { SageMakerFeatureConstruct } from '../../sagemaker-feature-construct';

export class CustomOCRSageMakerFeatureNestedStack extends FeatureNestedStack {
  constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {

    super(scope, id, props);
    const featureName = 'custom-ocr';
    this.templateOptions.description = '(SO8023-custom-ocr-sagemaker) - AI Solution Kit - Custom OCR. Template version v1.2.0. See https://awslabs.github.io/aws-ai-solution-kit/en/deploy-custom-ocr.';

    Repository.fromRepositoryName(this, `ai-solution-kit-${featureName}-repo`, `ai-solution-kit-${featureName}`);
    const stackRepo = new Repository(this, `ai-solution-kit-${featureName}`, {
      repositoryName: `ai-solution-kit-${featureName}`,
      removalPolicy: RemovalPolicy.RETAIN,
    });

    if (props.ecrDeployment != null) {
      const ecrCR = new CustomResource(this, `${featureName}-ecr`, {
        serviceToken: props.ecrDeployment.serviceToken,
        resourceType: 'Custom::AISolutionKitECRSageMaker',
        properties: {
          SrcImage: 'docker://public.ecr.aws/aws-gcr-solutions/aws-gcr-ai-solution-kit/custom-ocr-sagemaker:latest',
          DestImage: `docker://${stackRepo.repositoryUri}`,
          RepositoryName: `${stackRepo.repositoryName}`,
        },
      });


      // The default instance type is ml.g4dn.xlarge
      const sageMakerConstruct = new SageMakerFeatureConstruct(this, `${featureName}-construct`, {
        rootRestApi: props.restApi,
        authorizationType: props.customAuthorizationType,
        restApiResourcePath: `${featureName}`,
        featureName: `${featureName}`,
        featureCategory: 'media',
        updateCustomResourceProvider: props.updateCustomResourceProvider,

        sageMakerDockerImageUrl: `${Repository.fromRepositoryName(this, `${featureName}-sagemaker`, stackRepo.repositoryName).repositoryUri}:latest`,
        sageMakerDockerImageUrlCN: `${Repository.fromRepositoryName(this, `${featureName}-sagemaker-cn`, stackRepo.repositoryName).repositoryUri}:latest`,
        sageMakerInstanceType: 'ml.g4dn.xlarge',
      });
      sageMakerConstruct.node.addDependency(ecrCR);
    }
  }
}
