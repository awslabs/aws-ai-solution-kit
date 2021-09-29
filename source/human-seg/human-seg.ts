import * as cdk from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda';
import * as path from 'path';
import {AiKitsRestApi} from '../lib/ai-kits-rest-api';
import {EfsModelLambda} from '../lib/efs-model-lambda';

export class HumanSegStack extends cdk.Stack {
    constructor(app: cdk.App, id: string, props?: cdk.StackProps) {
        super(app, id, props);
        this.templateOptions.description = `(SO8023-seg) - AI Solution Kits - Human Image Segmentation. Template version v1.0.0`;

        const human_seg_lambda = new EfsModelLambda(this, 'human_seg_lambda', {
            mountPath: '/mnt/lambda',
            objects: [
                'https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/human-seg-model/v1.0.0/humanseg_720.onnx',
            ],
            handler: 'human_seg_app.lambda_handler',
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
            timeout: cdk.Duration.minutes(1),
            memorySize: 10240,
            environment: {
                PYTHONPATH: '/var/runtime:/opt:/opt/python/lib/python3.8/site-packages:python:python/lib/python3.8/site-packages',
                ACCESS_POINT: '/mnt/lambda',
            }
        });

        const api = new AiKitsRestApi(this, "aikits", {
            apiName: "HumanSegRESTAPI",
            stageName: 'prod',
            resourcePath: 'seg',
            postFunction: human_seg_lambda.function,
        });
        // api.addMethod('POST', efs_lambda.function);
    }
}

