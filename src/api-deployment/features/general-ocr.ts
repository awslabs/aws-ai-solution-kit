import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { FeatureNestedStack, FeatureNestedStackProps } from '../feature-nested-stack';
import { LambdaFeatureConstruct } from '../lambda-feature-construct';

export class GeneralOCRFeatureNestedStack extends FeatureNestedStack {
  constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {

    super(scope, id, props);
    const featureName = 'general-ocr';
    this.templateOptions.description = '(SO8023-ocr) - AI Solution Kit - General OCR Simplified Chinese. Template version v1.2.0. See https://awslabs.github.io/aws-ai-solution-kit/en/deploy-general-ocr.';

    new LambdaFeatureConstruct(this, `${featureName}-advanced`, {
      rootRestApi: props.restApi,
      authorizationType: props.customAuthorizationType,
      restApiResourcePath: `${featureName}-advanced`,
      lambdaEcrDeployment: props.ecrDeployment,
      lambdaDockerImageUrl: `${props.ecrRegistry}/${featureName}-advanced:latest`,
      featureName: `${featureName}-advanced`,
      featureCategory: 'media',
      updateCustomResourceProvider: props.updateCustomResourceProvider,
      lambdaMemorySize: 4096,
      lambdaTimeout: Duration.seconds(30),
    });

    new LambdaFeatureConstruct(this, `${featureName}-standard`, {
      rootRestApi: props.restApi,
      authorizationType: props.customAuthorizationType,
      restApiResourcePath: `${featureName}-standard`,
      lambdaEcrDeployment: props.ecrDeployment,
      lambdaDockerImageUrl: `${props.ecrRegistry}/${featureName}-standard:latest`,
      featureName: `${featureName}-standard`,
      featureCategory: 'media',
      updateCustomResourceProvider: props.updateCustomResourceProvider,
      lambdaMemorySize: 4096,
      lambdaTimeout: Duration.seconds(19),
    });
  }
}
