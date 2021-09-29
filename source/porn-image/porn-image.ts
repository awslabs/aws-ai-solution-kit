import * as cdk from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda';
import * as s3 from '@aws-cdk/aws-s3';
import * as path from 'path';
import * as apigateway from '@aws-cdk/aws-apigateway';
import * as s3deploy from '@aws-cdk/aws-s3-deployment';
import * as efs from "@aws-cdk/aws-efs";
import * as ec2 from "@aws-cdk/aws-ec2";
import * as cr from '@aws-cdk/custom-resources';
import {AiKitsRestApi} from '../lib/ai-kits-rest-api';
import {EfsModelLambda} from '../lib/efs-model-lambda';
import {CustomResource} from '@aws-cdk/core';

export class PornImageStack extends cdk.Stack {
    constructor(app: cdk.App, id: string, props?: cdk.StackProps) {
        super(app, id, props);
        this.templateOptions.description = `(SO8023-porn) - AI Solution Kits - Porn Image Detection. Template version v1.0.0`;

        const porn_image_lambda = new EfsModelLambda(this, 'porn_image_lambda', {
            mountPath: '/mnt/lambda',
            objects: [
                'https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/porn-image-model/v1.0.0/resnest50_fast_4s2x40d.bin',
                'https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/porn-image-model/v1.0.0/resnest50_fast_4s2x40d.mapping',
                'https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/porn-image-model/v1.0.0/resnest50_fast_4s2x40d.xml'
            ],
            handler: 'porn_image_app.lambda_handler',
            code: lambda.Code.fromAsset(path.join(__dirname, './src'), {
                bundling: {
                    image: lambda.Runtime.PYTHON_3_8.bundlingImage,
                    command: [
                        'bash', '-c', [
                            `cp -r /asset-input/* /asset-output/`,
                        ].join(' && ')
                    ],
                }
            }),
            runtime: lambda.Runtime.PYTHON_3_8,
            layerPath: path.join(__dirname, '/src'),
            timeout: cdk.Duration.seconds(30),
            memorySize: 1024,
            environment: {
                PYTHONPATH: '/var/runtime:/opt:/opt/python/lib/python3.8/site-packages:python:python/lib/python3.8/site-packages',
                ACCESS_POINT: '/mnt/lambda',
            }
        });

        const api = new AiKitsRestApi(this, "aikits", {
            apiName: "PornImageRESTAPI",
            stageName: 'prod',
            resourcePath: 'porn',
            postFunction: porn_image_lambda.function,
        });
        // api.addMethod('POST', efs_lambda.function);
    }
}

