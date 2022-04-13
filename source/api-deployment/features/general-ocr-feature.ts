import { Construct, Duration } from "@aws-cdk/core";
import { LambdaFeatureProps, LambdaFeatureConstruct } from '../lambda-feature-construct';
import { FeatureNestedStack, FeatureNestedStackProps } from '../feature-nested-stack';

export class GeneralOCRFeatureNestedStack extends FeatureNestedStack {
    constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {

        super(scope, id, props);
        const featureName = 'general-ocr';
        this.templateOptions.description = '(SO8023-ocr) - AI Solution Kits - General OCR. Template version v1.0.0';

        new LambdaFeatureConstruct(this, featureName, {
            rootRestApi: props.restApi,
            authorizationType: props.customAuthorizationType,
            restApiResourcePath: `${featureName}`,
            lambdaEcrDeployment: props.ecrDeployment,
            lambdaDockerImageUrl: 'public.ecr.aws/aws-gcr-solutions/ai-solution-kit-ocr-business-license:1.0.0',
            featureName: `${featureName}`,
            featureCategory: 'media',
            updateCustomResourceProvider: props.updateCustomResourceProvider,
            lambdaMemorySize: 4096,
            lambdaTimeout: Duration.seconds(15),
        });
    }
}
