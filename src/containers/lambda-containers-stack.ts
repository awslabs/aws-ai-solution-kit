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
    
    const GeneralOCRAdvanced = new DockerImageFunction(
      this,
      'general-ocr-advanced',
      {
        functionName: 'general-ocr-advanced',
        code: DockerImageCode.fromImageAsset('src/containers/general-ocr/model-advanced',
          {
            file: 'Dockerfile.lambda',
          },
        ),
      },
    );

    const GeneralOCRAdvancedSageMaker = new DockerImageFunction(
      this,
      'general-ocr-advanced-sm',
      {
        functionName: 'general-ocr-advanced-sm',
        code: DockerImageCode.fromImageAsset('src/containers/general-ocr/model-advanced',
          {
            file: 'Dockerfile.sagemaker',
          },
        ),
      },
    );
  }

  private buildLambdaImage(imageName: string, codeDirectory: string) {
    // example: this.buildLambdaImage('general-ocr-advanced', 'src/containers/models/general-ocr/model-advanced');
    new DockerImageFunction(
      this,
      imageName,
      {
        functionName: imageName,
        code: DockerImageCode.fromImageAsset(codeDirectory),
      },
    );
  }
}
