import { CustomResource, RemovalPolicy } from 'aws-cdk-lib';
import { Repository } from 'aws-cdk-lib/aws-ecr';
import { Construct } from 'constructs';
import { FeatureNestedStack, FeatureNestedStackProps } from '../../feature-nested-stack';
import { SageMakerFeatureConstruct } from '../../sagemaker-feature-construct';

export class ObjectRecognitionSageMakerFeatureNestedStack extends FeatureNestedStack {
  constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {

    super(scope, id, props);
    const featureName = 'object-recognition';
    this.templateOptions.description = '(SO8023-object-recognition-sagemaker) - AI Solution Kit - Image Similarity. Template version v1.3.0. See https://awslabs.github.io/aws-ai-solution-kit/en/deploy-object-recognition.';


    const stackRepo = new Repository(this, `ai-solution-kit-${featureName}`, {
      repositoryName: `ai-solution-kit-${featureName}-sagemaker`,
      removalPolicy: RemovalPolicy.RETAIN,
    });

    if (props.ecrDeployment != null) {
      const ecrCR = new CustomResource(this, `${featureName}-ecr`, {
        serviceToken: props.ecrDeployment.serviceToken,
        resourceType: 'Custom::AISolutionKitECRSageMaker',
        properties: {
          SrcImage: `docker://public.ecr.aws/aws-gcr-solutions/aws-gcr-ai-solution-kit/${featureName}-sagemaker:latest`,
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
