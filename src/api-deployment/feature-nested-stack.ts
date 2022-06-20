import { Aws, CfnCondition, Fn, NestedStack, NestedStackProps } from 'aws-cdk-lib';
import { AuthorizationType, RestApi } from 'aws-cdk-lib/aws-apigateway';
import { Provider } from 'aws-cdk-lib/custom-resources';
import { Construct } from 'constructs';
import { ECRDeployment } from '../lib/cdk-ecr-deployment/lib';

export interface FeatureNestedStackProps extends NestedStackProps {
  readonly restApi: RestApi;
  readonly customAuthorizationType?: AuthorizationType;
  readonly ecrDeployment?: ECRDeployment;
  readonly updateCustomResourceProvider: Provider;
  readonly instanceType?: string;
  /**
     * @default 8192
     */
  readonly lambdaMemorySize?: number;

  /**
   * ECR Registry
   * @default 'public.ecr.aws/aws-gcr-solutions/aws-gcr-ai-solution-kit'
   */
  readonly ecrRegistry?: string;
}

export class FeatureNestedStack extends NestedStack {
  constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {
    super(scope, id, props);
    new CfnCondition(this,
      'IsChinaRegionCondition',
      { expression: Fn.conditionEquals(Aws.PARTITION, 'aws-cn') });
  }
}
