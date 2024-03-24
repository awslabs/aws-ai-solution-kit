import { Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { FeatureNestedStack, FeatureNestedStackProps } from '../../feature-nested-stack';
import { LambdaFeatureConstruct } from '../../lambda-feature-construct';

export class LayoutAnalysisFeatureNestedStack extends FeatureNestedStack {
  constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {

    super(scope, id, props);
    const featureName = 'layout-analysis';
    this.templateOptions.description = '(SO8023-la) - AI Solution Kit - Layout Analysis. Template version v1.4.0. See https://awslabs.github.io/aws-ai-solution-kit/en/deploy-layout-analysis.';

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
