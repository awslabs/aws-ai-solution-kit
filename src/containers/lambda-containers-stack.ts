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

    const ImagePIIDetection = new DockerImageFunction(
      this,
      'photo-pii-detection',
      {
        functionName: 'photo-pii-detection',
        code: DockerImageCode.fromImageAsset('src/containers/image-pii-detection',
          {
            file: 'Dockerfile',
          },
        ),
      },
    );
  }
}
