#!/usr/bin/env node
import {
  Stack,
  StackProps,
} from 'aws-cdk-lib';
import {
  DockerImageCode,
  DockerImageFunction,
} from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';
import 'source-map-support/register';

export class LambdaContainersStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const GeneralOCRStandard = new DockerImageFunction(
      this,
      'general-ocr-standard',
      {
        functionName: 'general-ocr-standard',
        code: DockerImageCode.fromImageAsset('src/containers/general-ocr/model-standard',
          {
            file: 'Dockerfile.lambda',
          },
        ),
      },
    );

    const GeneralOCRStandardSageMaker = new DockerImageFunction(
      this,
      'general-ocr-standard-sagemaker',
      {
        functionName: 'general-ocr-standard-sagemaker',
        code: DockerImageCode.fromImageAsset('src/containers/general-ocr/model-standard',
          {
            file: 'Dockerfile.sagemaker',
          },
        ),
      },
    );
  }
}
