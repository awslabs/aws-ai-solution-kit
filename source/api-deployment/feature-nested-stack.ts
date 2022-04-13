import { AuthorizationType, RestApi } from '@aws-cdk/aws-apigateway';
import { Aws, CfnCondition, Construct, Fn, NestedStack, NestedStackProps } from "@aws-cdk/core";
import { Provider } from '@aws-cdk/custom-resources';
import { ECRDeployment } from '../lib/cdk-ecr-deployment/lib';

export interface FeatureNestedStackProps extends NestedStackProps {
    readonly restApi: RestApi;
    readonly customAuthorizationType?: AuthorizationType;
    readonly ecrDeployment?: ECRDeployment;
    readonly updateCustomResourceProvider: Provider;
    readonly instanceType?: string;
}

export class FeatureNestedStack extends NestedStack {
    constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {
        super(scope, id, props);
        new CfnCondition(this,
            'IsChinaRegionCondition',
            { expression: Fn.conditionEquals(Aws.PARTITION, 'aws-cn') });
    }
}
