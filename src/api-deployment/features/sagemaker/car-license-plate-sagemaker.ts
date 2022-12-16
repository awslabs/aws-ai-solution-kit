import { CustomResource, RemovalPolicy } from 'aws-cdk-lib';
import { Repository } from 'aws-cdk-lib/aws-ecr';
import { Construct } from 'constructs';
import { FeatureNestedStack, FeatureNestedStackProps } from '../../feature-nested-stack';
import { SageMakerFeatureConstruct } from '../../sagemaker-feature-construct';

export class CarLicensePlateSageMakerFeatureNestedStack extends FeatureNestedStack {
  constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {

    super(scope, id, props);
    const featureName = 'car-license-plate';
    this.templateOptions.description = '(SO8023-car-license-plate-sagemaker) - AI Solution Kit - Car License Plate. Template version v1.2.0. See https://awslabs.github.io/aws-ai-solution-kit/en/deploy-car-license-plate.';


    const stackRepo = new Repository(this, `ai-solution-kit-${featureName}`, {
      repositoryName: `ai-solution-kit-${featureName}-sagemaker`,
      removalPolicy: RemovalPolicy.RETAIN,
    });

    if (props.ecrDeployment != null) {
      const ecrCR = new CustomResource(this, `${featureName}-ecr`, {
        serviceToken: props.ecrDeployment.serviceToken,
        resourceType: 'Custom::AISolutionKitECRSageMaker',
        properties: {
          SrcImage: 'docker://public.ecr.aws/aws-gcr-solutions/aws-gcr-ai-solution-kit/car-license-plate-sm:latest',
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
