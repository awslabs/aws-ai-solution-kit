import {
  CfnOutput,
  CfnParameter,
  aws_apigateway as apigw,
} from 'aws-cdk-lib';
import { AccessLogFormat, LogGroupLogDestination } from 'aws-cdk-lib/aws-apigateway';
import { Resource } from 'aws-cdk-lib/aws-apigateway/lib/resource';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';

export class RestApiGateway {
  public apiGateway: apigw.RestApi;
  public readonly apiKey: string;
  public readonly routers: {[key: string]: Resource} = {};
  private readonly scope: Construct;

  constructor(scope: Construct, routes: string[]) {
    this.scope = scope;
    [this.apiGateway, this.apiKey] = this.createApigw();
    for (let route of routes) {
      this.routers[route] = this.apiGateway.root.addResource(route);
    }
  }

  private createApigw(): [apigw.RestApi, string] {
    const apiKeyParam = new CfnParameter(this.scope, 'sd-extension-api-key', {
      type: 'String',
      description: 'API Key for Stable Diffusion extension',
      // API Key value should be at least 20 characters
      default: '09876543210987654321',
    });

    const apiAccessLogGroup = new logs.LogGroup(
      this.scope,
      'aigc-api-logs',
    );

    // Create an API Gateway, will merge with existing API Gateway
    const api = new apigw.RestApi(this.scope, 'train-deploy-api', {
      restApiName: 'Stable Diffusion Train and Deploy API',
      description:
                'This service is used to train and deploy Stable Diffusion models.',
      deployOptions: {
        accessLogDestination: new LogGroupLogDestination(apiAccessLogGroup),
        accessLogFormat: AccessLogFormat.clf(),
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigw.Cors.ALL_ORIGINS, // You can also provide a list of specific origins ['https://example.com']
        allowMethods: apigw.Cors.ALL_METHODS, // You can also provide a list of specific methods ['GET', 'POST', 'OPTIONS']
        allowHeaders: ['Content-Type', 'X-Amz-Date', 'Authorization', 'X-Api-Key', 'X-Amz-Security-Token', 'X-Amz-User-Agent'], // Customize as needed
      },
    });

    // Add API Key to the API Gateway
    const apiKey = api.addApiKey('sd-extension-api-key', {
      apiKeyName: 'sd-extension-api-key',
      value: apiKeyParam.valueAsString,
    });

    const usagePlan = api.addUsagePlan('sd-extension-api-usage-plan', {});
    usagePlan.addApiKey(apiKey);
    usagePlan.addApiStage({
      stage: api.deploymentStage,
    });
    // Output the API Gateway URL
    new CfnOutput(this.scope, 'train-deploy-api-url', {
      value: api.url,
    });

    return [api, apiKeyParam.valueAsString];
  }
}
