import { CustomResource, RemovalPolicy } from 'aws-cdk-lib';
import { Repository } from 'aws-cdk-lib/aws-ecr';
import { Construct } from 'constructs';
import { FeatureNestedStack, FeatureNestedStackProps } from '../../feature-nested-stack';
import { SageMakerFeatureConstruct } from '../../sagemaker-feature-construct';

export class TextSimilaritySageMakerFeatureNestedStack extends FeatureNestedStack {
  constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {

    super(scope, id, props);
    const featureName = 'text-similarity';
    this.templateOptions.description = '(SO8023-tsg) - AI Solution Kit - Text Similarity. Template version v1.4.0. See https://awslabs.github.io/aws-ai-solution-kit/en/deploy-text-similarity.';

    // The default instance type is ml.g4dn.xlarge
    const sageMakerConstruct = new SageMakerFeatureConstruct(this, `${featureName}-construct`, {
      rootRestApi: props.restApi,
      authorizationType: props.customAuthorizationType,
      restApiResourcePath: `${featureName}`,
      featureName: `${featureName}`,
      featureCategory: 'media',
      updateCustomResourceProvider: props.updateCustomResourceProvider,
      sageMakerInstanceType: 'ml.g4dn.xlarge',
      sageMakerEcrDeployment: props.ecrDeployment,
    });
  }
}
