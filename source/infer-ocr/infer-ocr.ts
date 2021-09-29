import * as cdk from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda';
import * as path from 'path';
import {AiKitsRestApi} from '../lib/ai-kits-rest-api';
import {EfsModelLambda} from '../lib/efs-model-lambda';

export class InferOCRStack extends cdk.Stack {
    constructor(app: cdk.App, id: string, props?: cdk.StackProps) {
        super(app, id, props);
        this.templateOptions.description = `(SO8023-ocr) - AI Solution Kits - Infer OCR. Template version v1.0.0`;

        const infer_ocr_lambda = new EfsModelLambda(this, 'infer_ocr_lambda', {
            mountPath: '/mnt/lambda',
            objects: [
                'https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/infer-ocr-model/v1.0.0/ppocr_keys_v1.txt',
                'https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/infer-ocr-model/v1.0.0/text_classifier.onnx',
                'https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/infer-ocr-model/v1.0.0/text_detector.onnx',
                'https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/infer-ocr-model/v1.0.0/text_recognizer.onnx',
            ],
            handler: 'infer_ocr_app.lambda_handler',
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
            memorySize: 10240,
            environment: {
                PYTHONPATH: '/var/runtime:/opt:/opt/python/lib/python3.8/site-packages:python:python/lib/python3.8/site-packages',
                ACCESS_POINT: '/mnt/lambda',
            }
        });

        const api = new AiKitsRestApi(this, "aikits", {
            apiName: "InferOCRRESTAPI",
            stageName: 'prod',
            resourcePath: 'ocr',
            postFunction: infer_ocr_lambda.function,
        });
        // api.addMethod('POST', efs_lambda.function);
    }
}

