import { Aws, Construct } from 'aws-cdk-lib';
import { FeatureNestedStack, FeatureNestedStackProps } from '../feature-nested-stack';
import { SageMakerFeatureConstruct } from '../sagemaker-feature-construct';

export class SuperResolutionInf1FeatureNestedStack extends FeatureNestedStack {
  constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {

    super(scope, id, props);
    const featureName = 'super-resolution-inf1';
    this.templateOptions.description = '(SO8023-sr) - AI Solution Kit - Super Resolution with Amazon SageMaker Inferentia Instance. Template version v1.2.0. See https://aws-samples.github.io/aws-ai-solution-kit/en/deploy-super-resolution-inf1.';
    // The default Inf1 instance type is ml.inf1.xlarge
    var instanceType: string = props.instanceType == null ? 'ml.inf1.xlarge' : props.instanceType;

    new SageMakerFeatureConstruct(this, `${featureName}`, {
      rootRestApi: props.restApi,
      authorizationType: props.customAuthorizationType,
      restApiResourcePath: `${featureName}`,
      featureName: `${featureName}`,
      featureCategory: 'media',
      updateCustomResourceProvider: props.updateCustomResourceProvider,
      sageMakerDockerImageUrl: `366590864501.dkr.ecr.${Aws.REGION}.amazonaws.com/ai-kits-super-resolution:latest`,
      sageMakerDockerImageUrlCN: `753680513547.dkr.ecr.${Aws.REGION}.amazonaws.com.cn/ai-kits-super-resolution:latest`,
      sageMakerInstanceType: instanceType,
    });
  }
}
