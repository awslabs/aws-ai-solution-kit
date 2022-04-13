import { Aws, Construct } from "@aws-cdk/core";
import { FeatureNestedStack, FeatureNestedStackProps } from '../feature-nested-stack';
import { SageMakerFeatureConstruct } from '../sagemaker-feature-construct';

export class SuperResolutionGpuFeatureNestedStack extends FeatureNestedStack {
    constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {

        super(scope, id, props);
        const featureName = 'super-resolution-gpu';
        this.templateOptions.description = '(SO8023-sr) - AI Solution Kits - Super Resolution. Template version v1.0.0';
        // The default GPU instance type is ml.g4dn.xlarge
        var instanceType: string = props.instanceType == null ? 'ml.g4dn.xlarge' : props.instanceType;

        new SageMakerFeatureConstruct(this, `${featureName}-class`, {
            rootRestApi: props.restApi,
            authorizationType: props.customAuthorizationType,
            restApiResourcePath: `${featureName}`,
            featureName: `${featureName}`,
            featureCategory: 'media',
            updateCustomResourceProvider: props.updateCustomResourceProvider,
            sageMakerDockerImageUrl: `366590864501.dkr.ecr.${Aws.REGION}.amazonaws.com/ai-kits-super-resolution-gpu:latest`,
            sageMakerDockerImageUrlCN: `753680513547.dkr.ecr.${Aws.REGION}.amazonaws.com.cn/ai-kits-super-resolution-gpu:latest`,
            sageMakerInstanceType: instanceType
        });
    }
}
