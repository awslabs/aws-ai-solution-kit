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
        code: DockerImageCode.fromImageAsset('src/containers/general-ocr/model-advanced'),
      },
    );

    const GeneralOCRStandard = new DockerImageFunction(
      this,
      'general-ocr-standard',
      {
        functionName: 'general-ocr-standard',
        code: DockerImageCode.fromImageAsset('src/containers/general-ocr/model-standard'),
      },
    );

    const GeneralOCRTraditionalStandard = new DockerImageFunction(
      this,
      'general-ocr-traditional-standard',
      {
        functionName: 'general-ocr-traditional-standard',
        code: DockerImageCode.fromImageAsset('src/containers/general-ocr-traditional/model-standard'),
      },
    );

    const NudityDetection = new DockerImageFunction(
      this,
      'pornography-detection',
      {
        functionName: 'pornography-detection',
        code: DockerImageCode.fromImageAsset('src/containers/pornography-detection/model'),
      },
    );

    const HumanImageSegmentation = new DockerImageFunction(
      this,
      'human-image-segmentation',
      {
        functionName: 'human-image-segmentation',
        code: DockerImageCode.fromImageAsset('src/containers/human-image-segmentation/model'),
      },
    );

    /**
         * @deprecated use `ImageSuperResolutionGPU`
         */
    const ImageSuperResolutionLambda = new DockerImageFunction(
      this,
      'image-super-resolution-lambda',
      {
        functionName: 'image-super-resolution-lambda',
        code: DockerImageCode.fromImageAsset('src/containers/image-super-resolution-lambda/model'),
      },
    );

    const CNBusinessLicense = new DockerImageFunction(
      this,
      'cn-business-license',
      {
        functionName: 'cn-business-license',
        code: DockerImageCode.fromImageAsset('src/containers/ocr-cn-business-license/model'),
      },
    );

    const ObjectRecognition = new DockerImageFunction(
      this,
      'object-recognition',
      {
        functionName: 'object-recognition',
        code: DockerImageCode.fromImageAsset('src/containers/object-recognition/model'),
      },
    );

    const FaceComparison = new DockerImageFunction(
      this,
      'face-comparison',
      {
        functionName: 'face-comparison',
        code: DockerImageCode.fromImageAsset('src/containers/face-comparison/model'),
      },
    );

    const FaceDetection = new DockerImageFunction(
      this,
      'face-detection',
      {
        functionName: 'face-detection',
        code: DockerImageCode.fromImageAsset('src/containers/face-detection/model'),
      },
    );

    const HumanAttribute = new DockerImageFunction(
      this,
      'human-attribute',
      {
        functionName: 'human-attribute',
        code: DockerImageCode.fromImageAsset('src/containers/human-attribute/model'),
      },
    );

    const LicensePlate = new DockerImageFunction(
      this,
      'car-license-plate',
      {
        functionName: 'car-license-plate',
        code: DockerImageCode.fromImageAsset('src/containers/license-plate/model'),
      },
    );

    const CustomOcr = new DockerImageFunction(
      this,
      'custom-ocr',
      {
        functionName: 'custom-ocr',
        code: DockerImageCode.fromImageAsset('src/containers/custom-ocr/model'),
      },
    );

    const TextSimilarity = new DockerImageFunction(
      this,
      'text-similarity',
      {
        functionName: 'text-similarity',
        code: DockerImageCode.fromImageAsset('src/containers/text-similarity/model'),
      },
    );

    const ImageSimilarity = new DockerImageFunction(
      this,
      'image-similarity',
      {
        functionName: 'image-similarity',
        code: DockerImageCode.fromImageAsset('src/containers/image-similarity/model'),
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
