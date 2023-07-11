import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { FeatureNestedStack, FeatureNestedStackProps } from '../../feature-nested-stack';
import { LambdaFeatureConstruct } from '../../lambda-feature-construct';

export class GeneralNLUFeatureNestedStack extends FeatureNestedStack {
  constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {

    super(scope, id, props);
    const featureName = 'general-nlu';
    this.templateOptions.description = '(SO8023-nul) - AI Solution Kit - General NLU. Template version v1.3.0. See https://awslabs.github.io/aws-ai-solution-kit/en/deploy-text-similarity.';

    new LambdaFeatureConstruct(this, featureName, {
      rootRestApi: props.restApi,
      authorizationType: props.customAuthorizationType,
      restApiResourcePath: `${featureName}`,
      lambdaEcrDeployment: props.ecrDeployment,
      lambdaDockerImageUrl: `${props.ecrRegistry}/${featureName}:latest`,
      featureName: `${featureName}`,
      featureCategory: 'media',
      updateCustomResourceProvider: props.updateCustomResourceProvider,
      lambdaMemorySize: props.lambdaMemorySize,
      lambdaTimeout: Duration.seconds(19),
    });
  }
}
