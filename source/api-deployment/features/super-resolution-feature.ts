import { Construct } from "@aws-cdk/core";
import {Provider} from '@aws-cdk/custom-resources';
import { LambdaFeatureProps, LambdaFeatureConstruct } from '../lambda-feature-construct';
import { FeatureNestedStack, FeatureNestedStackProps } from '../feature-nested-stack';
import { pathToFileURL } from "url";

export class SuperResolutionFeatureNestedStack extends FeatureNestedStack {
    constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {

        super(scope, id, props);
        const featureName = 'super-resolution';
        this.templateOptions.description = '(SO8023-sr) - AI Solution Kits - Super Resolution. Template version v1.0.0';

        new LambdaFeatureConstruct(this, featureName, {
            rootRestApi: props.restApi,
            authorizationType: props.customAuthorizationType,
            restApiResourcePath: `${featureName}`,
            lambdaEcrDeployment: props.ecrDeployment,
            lambdaDockerImageUrl: 'public.ecr.aws/aws-gcr-solutions/ai-solution-kit-ocr-business-license:1.0.0',
            featureName: `${featureName}`,
            featureCategory: 'media',
            updateCustomResourceProvider: props.updateCustomResourceProvider
        });
    }
}
