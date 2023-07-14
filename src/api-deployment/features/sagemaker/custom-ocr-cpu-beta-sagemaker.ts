import { CustomResource, RemovalPolicy } from 'aws-cdk-lib';
import { Repository } from 'aws-cdk-lib/aws-ecr';
import { Construct } from 'constructs';
import { FeatureNestedStack, FeatureNestedStackProps } from '../../feature-nested-stack';
import { SageMakerFeatureConstruct } from '../../sagemaker-feature-construct';

export class CustomOCRCpuBetaSageMakerFeatureNestedStack extends FeatureNestedStack {
  constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {

    super(scope, id, props);
    const featureName = 'custom-ocr';
    this.templateOptions.description = '(SO8023-cog) - AI Solution Kit - Custom OCR. Template version v1.4.0. See https://awslabs.github.io/aws-ai-solution-kit/en/deploy-custom-ocr.';

    // The default instance type is ml.c5.2xlarge
    const sageMakerConstruct = new SageMakerFeatureConstruct(this, `${featureName}-construct`, {
      rootRestApi: props.restApi,
      authorizationType: props.customAuthorizationType,
      restApiResourcePath: `${featureName}`,
      featureName: `${featureName}`,
      featureCategory: 'media',
      updateCustomResourceProvider: props.updateCustomResourceProvider,
      sageMakerInstanceType: 'ml.c5.2xlarge',
      sageMakerEcrDeployment: props.ecrDeployment,
    });
  }
}
