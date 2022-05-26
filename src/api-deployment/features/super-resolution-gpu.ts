import { Aws, CfnMapping } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { FeatureNestedStack, FeatureNestedStackProps } from '../feature-nested-stack';
import { SageMakerFeatureConstruct } from '../sagemaker-feature-construct';

export class SuperResolutionGpuFeatureNestedStack extends FeatureNestedStack {
  constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {

    super(scope, id, props);
    const featureName = 'super-resolution';
    this.templateOptions.description = '(SO8023-sr) - AI Solution Kit - Super Resolution. Template version v1.2.0. See https://awslabs.github.io/aws-ai-solution-kit/en/deploy-super-resolution.';
    // The default GPU instance type is ml.g4dn.xlarge
    var instanceType: string = props.instanceType == null ? 'ml.g4dn.xlarge' : props.instanceType;
    const map = new CfnMapping(this, 'instanceTypeMapping', {
      mapping: {
        'yes-ml.g4dn.xlarge': { value: 'ml.g4dn.xlarge' },
        'yes-ml.g4dn.2xlarge': { value: 'ml.g4dn.2xlarge' },
        'yes-ml.g4dn.8xlarge': { value: 'ml.g4dn.8xlarge' },
      },
    });
    new SageMakerFeatureConstruct(this, `${featureName}-class`, {
      rootRestApi: props.restApi,
      authorizationType: props.customAuthorizationType,
      restApiResourcePath: `${featureName}`,
      featureName: `${featureName}`,
      featureCategory: 'media',
      updateCustomResourceProvider: props.updateCustomResourceProvider,
      sageMakerDockerImageUrl: `366590864501.dkr.ecr.${Aws.REGION}.amazonaws.com/ai-kits-super-resolution-gpu:latest`,
      sageMakerDockerImageUrlCN: `753680513547.dkr.ecr.${Aws.REGION}.amazonaws.com.cn/ai-kits-super-resolution-gpu:latest`,
      sageMakerInstanceType: instanceType,
    });
  }
}
