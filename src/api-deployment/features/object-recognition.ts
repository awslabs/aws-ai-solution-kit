import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { FeatureNestedStack, FeatureNestedStackProps } from '../feature-nested-stack';
import { LambdaFeatureConstruct } from '../lambda-feature-construct';

export class ObjectRecognitionFeatureNestedStack extends FeatureNestedStack {
  constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {

    super(scope, id, props);
    const featureName = 'object-recognition';
    this.templateOptions.description = '(SO8023-object-recognition) - AI Solution Kit - Object Recognition. Template version v1.2.0. See https://aws-samples.github.io/aws-ai-solution-kit/en/deploy-object-recognition.';

    new LambdaFeatureConstruct(this, featureName, {
      rootRestApi: props.restApi,
      authorizationType: props.customAuthorizationType,
      restApiResourcePath: `${featureName}`,
      lambdaEcrDeployment: props.ecrDeployment,
      lambdaDockerImageUrl: `${props.ecrRegistry}/${featureName}:latest`,
      featureName: `${featureName}`,
      featureCategory: 'media',
      updateCustomResourceProvider: props.updateCustomResourceProvider,
      lambdaMemorySize: 4096,
      lambdaTimeout: Duration.seconds(19),
    });
  }
}
