import { CustomResource, RemovalPolicy } from "aws-cdk-lib";
import { Repository } from "aws-cdk-lib/aws-ecr";
import { Construct } from "constructs";
import {
  FeatureNestedStack,
  FeatureNestedStackProps,
} from "../feature-nested-stack";
import { SageMakerFeatureConstruct } from "../sagemaker-feature-construct";

export class GreenScreenMattingSMFeatureNestedStack extends FeatureNestedStack {
  constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {
    super(scope, id, props);
    const featureName = "human-segmentation";
    this.templateOptions.description =
      "(SO8023-seg) - AI Solution Kit - Green Screen Matting. Template version v1.2.0. Template version v1.2.0. See https://awslabs.github.io/aws-ai-solution-kit/en/deploy-human-segmentation.";

    Repository.fromRepositoryName(
      this,
      `ai-solution-kit-${featureName}Repository`,
      `ai-solution-kit-${featureName}`
    );
    const stackRepo = new Repository(this, `ai-solution-kit-${featureName}`, {
      repositoryName: `ai-solution-kit-${featureName}`,
      removalPolicy: RemovalPolicy.RETAIN,
    });

    if (props.ecrDeployment != null) {
      // Lambda deployment
      const ecrCR = new CustomResource(this, `${featureName}Ecr`, {
        serviceToken: props.ecrDeployment.serviceToken,
        resourceType: "Custom::AISolutionKitECRLambda",
        properties: {
          SrcImage:
            "docker://public.ecr.aws/aws-gcr-solutions/aws-gcr-ai-solution-kit/human-image-segmentation:latest",
          DestImage: `docker://${stackRepo.repositoryUri}`,
          RepositoryName: `${stackRepo.repositoryName}`,
        },
      });

      // The default instance type is ml.g4dn.xlarge
      const sageMakerConstruct = new SageMakerFeatureConstruct(
        this,
        `${featureName}-class`,
        {
          rootRestApi: props.restApi,
          authorizationType: props.customAuthorizationType,
          restApiResourcePath: `${featureName}`,
          featureName: `${featureName}`,
          featureCategory: "media",
          updateCustomResourceProvider: props.updateCustomResourceProvider,

          sageMakerDockerImageUrl: `${
            Repository.fromRepositoryName(
              this,
              `${featureName}SM`,
              stackRepo.repositoryName
            ).repositoryUri
          }:latest`,
          sageMakerDockerImageUrlCN: `${
            Repository.fromRepositoryName(
              this,
              `${featureName}SM-CN`,
              stackRepo.repositoryName
            ).repositoryUri
          }:latest`,
          sageMakerInstanceType: "ml.inf1.xlarge",
        }
      );
      sageMakerConstruct.node.addDependency(ecrCR);
    }
  }
}
