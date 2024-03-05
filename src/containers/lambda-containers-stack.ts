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

    const LayoutAnalysisSageMaker = new DockerImageFunction(
      this,
      'layout-analysis-sagemaker',
      {
        functionName: 'layout-analysis-sagemaker',
        code: DockerImageCode.fromImageAsset('src/containers/layout-analysis/model',
          {
            file: 'Dockerfile.sagemaker',
          },
        ),
      },
    );
  }
}
