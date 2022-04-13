import {
    AuthorizationType, LambdaIntegration, RestApi
} from '@aws-cdk/aws-apigateway';
import { Runtime, Tracing } from '@aws-cdk/aws-lambda';
import { NodejsFunction } from '@aws-cdk/aws-lambda-nodejs';
import { Aws, CfnCondition, Construct, Duration, Fn, NestedStack, NestedStackProps } from "@aws-cdk/core";
import * as path from 'path';

export interface ApiDocsProps extends NestedStackProps {
    readonly restApi: RestApi;
    readonly invokeUrl: string;
    readonly authorizationType: string;
}

export class ApiDocsNestedStack extends NestedStack {

    constructor(scope: Construct, id: string, props: ApiDocsProps) {

        super(scope, id, props);

        new CfnCondition(this,
            'IsChinaRegionCondition',
            { expression: Fn.conditionEquals(Aws.PARTITION, 'aws-cn') });
            
        const apiDocFunction = new NodejsFunction(this, 'api-docs-function', {
            runtime: Runtime.NODEJS_14_X,
            memorySize: 2048,
            timeout: Duration.seconds(15),
            handler: 'handler',
            entry: path.join(__dirname, './swagger-ui/app.js'),
            tracing: Tracing.ACTIVE,
            bundling: {
                nodeModules: [
                    'yamljs',
                    'serverless-http',
                    'express',
                    'serverless-http',
                    'swagger-ui-express'
                ],
                minify: true,
                commandHooks: {
                    beforeBundling(inputDir: string, outputDir: string): string[] {
                        return [
                            `cp -R ${inputDir}/source/api-deployment/swagger-ui/* ${outputDir}`
                        ]
                    },
                    beforeInstall() {
                        return []
                    },
                    afterBundling(_inputDir: string, _outputDir: string): string[] {
                        return []
                    },
                },
            },
            environment: {
                SWAGGER_SPEC_URL: props.invokeUrl.toString(),
                AUTH_TYPE: props.authorizationType.toString()
            }
        });

        const resource = props?.restApi.root.addResource('api-docs');
        const proxy = resource.addProxy({
            anyMethod: true,
            defaultIntegration: new LambdaIntegration(apiDocFunction, { proxy: true })
        });

        const post = resource.addMethod('GET',
            new LambdaIntegration(apiDocFunction, { proxy: true }),
        )
    }
}
