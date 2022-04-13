import {
    AuthorizationType, CfnMethod, Cors, Deployment, EndpointType,
    LambdaIntegration, Method, MethodLoggingLevel, RestApi, Stage
} from '@aws-cdk/aws-apigateway';
import { Repository } from "@aws-cdk/aws-ecr";
import { DockerImageCode, DockerImageFunction } from "@aws-cdk/aws-lambda";
import {
    Aws, CfnCondition, CfnOutput, CfnParameter, Construct, Duration, Fn, RemovalPolicy, Stack,
    StackProps, CustomResource, NestedStack, NestedStackProps
} from "@aws-cdk/core";
import * as lambda from '@aws-cdk/aws-lambda';
import * as cr from '@aws-cdk/custom-resources';
import * as iam from '@aws-cdk/aws-iam';
import * as path from 'path';
import { PythonFunction } from "@aws-cdk/aws-lambda-python";
import { ECRDeployment, DockerImageName } from '../lib/cdk-ecr-deployment/lib';
import { NestedAiFeatureConstruct } from './lambda-feature-construct';

export interface FeatureNestedStackProps extends NestedStackProps {
    readonly restApi: RestApi;
    readonly ecrDeployment: ECRDeployment;
}

export class FeatureNestedStack extends NestedStack {

    constructor(scope: Construct, id: string, props: FeatureNestedStackProps) {

        super(scope, id, props);
    }
}
