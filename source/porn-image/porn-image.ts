import * as lambda from '@aws-cdk/aws-lambda';
import * as cdk from '@aws-cdk/core';
import * as path from 'path';
import { AiKitsRestApi } from '../lib/ai-kits-rest-api';
import { EfsModelLambda } from '../lib/efs-model-lambda';

export class PornImageStack extends cdk.Stack {
    constructor(app: cdk.App, id: string, props?: cdk.StackProps) {
        super(app, id, props);
        this.templateOptions.description = `(SO8023-porn) - AI Solution Kits - Porn Image Detection. Template version v1.0.0`;

        const modelVersion = new cdk.CfnParameter(this, "modelVersion", {
            default: 'v1.0.0',
            type: 'String',
            description: 'Pre-trained model version, this parameter works only for testing, please do NOT change the default value.'
        });

        const porn_image_lambda = new EfsModelLambda(this, 'porn_image_lambda', {
            mountPath: '/mnt/lambda',
            objects: [
                `https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/porn-image-model/${modelVersion.valueAsString}/resnest50_fast_4s2x40d.mapping`,
                `https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/porn-image-model/${modelVersion.valueAsString}/resnest50_fast_4s2x40d.bin`,
                `https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/porn-image-model/${modelVersion.valueAsString}/resnest50_fast_4s2x40d.xml`
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
    }
}

