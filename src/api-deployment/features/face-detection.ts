import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { FeatureNestedStack, FeatureNestedStackProps } from '../feature-nested-stack';
import { LambdaFeatureConstruct } from '../lambda-feature-construct';

export class FaceDetectionFeatureNestedStack extends FeatureNestedStack {
  constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {

    super(scope, id, props);
    const featureName = 'face-detection';
    this.templateOptions.description = '(SO8023-face-detection) - AI Solution Kit - Face Detection. Template version v1.2.0. See https://awslabs.github.io/aws-ai-solution-kit/en/deploy-face-detection.';

    new LambdaFeatureConstruct(this, featureName, {
      rootRestApi: props.restApi,
      authorizationType: props.customAuthorizationType,
      restApiResourcePath: `${featureName}`,
      lambdaEcrDeployment: props.ecrDeployment,
      lambdaDockerImageUrl: `${props.ecrRegistry}/${featureName}:latest`,
      featureName: `${featureName}`,
      featureCategory: 'media',
      updateCustomResourceProvider: props.updateCustomResourceProvider,
      lambdaMemorySize: 8192,
      lambdaTimeout: Duration.seconds(19),
    });
  }
}
