import { aws_lambda as lambda, Duration, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export class OCRBusinessLicenseModelStack extends Stack {
    constructor(scope: Construct, id: string, props?: StackProps) {
        super(scope, id, props);

        this.templateOptions.description = '(SO8023-ocr) - AI Solution Kits - Infer OCR with Object Detector. Template version v1.0.0';
        /**
          * Lambda Image Function
          */
        const BusinessLicenseOCR = new lambda.DockerImageFunction(
            this,
            'BusinessLicenseOCR',
            {
                code: lambda.DockerImageCode.fromImageAsset('src/OCR-China-business-license/model'),
                timeout: Duration.seconds(30),
                memorySize: 4096
            }
        )
    }
}
