import * as path from 'path';
import { Aws, CfnCondition, Duration, Fn, NestedStack, NestedStackProps } from 'aws-cdk-lib';
import { LambdaIntegration, RestApi } from 'aws-cdk-lib/aws-apigateway';
import {
  Effect,
  PolicyStatement,
} from 'aws-cdk-lib/aws-iam';
import { Runtime, Tracing } from 'aws-cdk-lib/aws-lambda';
import { NodejsFunction } from 'aws-cdk-lib/aws-lambda-nodejs';
import { Construct } from 'constructs';

export interface ApiExplorerProps extends NestedStackProps {
  readonly restApi: RestApi;
  readonly invokeUrl: string;
  readonly authorizationType: string;
}

export class ApiExplorerNestedStack extends NestedStack {

  constructor(scope: Construct, id: string, props: ApiExplorerProps) {

    super(scope, id, props);
    this.templateOptions.description = '(SO8023) - AI Solution Kit - API Explorer. Template version v1.2.0. See https://aws-samples.github.io/aws-ai-solution-kit/en/api-explorer.';
    new CfnCondition(this,
      'IsChinaRegionCondition',
      { expression: Fn.conditionEquals(Aws.PARTITION, 'aws-cn') });

    const apiDocFunction = new NodejsFunction(this, 'api-explorer-function', {
      runtime: Runtime.NODEJS_14_X,
      memorySize: 2048,
      timeout: Duration.seconds(19),
      handler: 'handler',
      entry: path.join(__dirname, './api-explorer/app.js'),
      tracing: Tracing.ACTIVE,
      bundling: {
        nodeModules: [
          'aws-sdk',
          'yamljs',
          'serverless-http',
          'express',
          'serverless-http',
          'swagger-ui-express',
          'deasync',
        ],
        minify: true,
        commandHooks: {
          beforeBundling(inputDir: string, outputDir: string): string[] {
            return [
              `cp -R ${inputDir}/src/api-deployment/features/api-explorer/* ${outputDir}`,
            ];
          },
          beforeInstall() {
            return [];
          },
          afterBundling(_inputDir: string, _outputDir: string): string[] {
            return [];
          },
        },
      },
      environment: {
        REST_API_ID: props.restApi.restApiId,
        SWAGGER_SPEC_URL: props.invokeUrl.toString(),
        AUTH_TYPE: props.authorizationType.toString(),
      },
    });

    apiDocFunction.addToRolePolicy(
      new PolicyStatement({
        effect: Effect.ALLOW,
        actions: [
          'apigateway:*',
        ],
        resources: [
          '*',
        ],
      }),
    );

    const resource = props?.restApi.root.addResource('api-explorer');
    const proxy = resource.addProxy({
      anyMethod: true,
      defaultIntegration: new LambdaIntegration(apiDocFunction, { proxy: true }),
    });

    const post = resource.addMethod('GET',
      new LambdaIntegration(apiDocFunction, { proxy: true }),
    );
  }
}
