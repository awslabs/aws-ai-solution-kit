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
      'general-ocr-standard-sm',
      {
        functionName: 'general-ocr-standard-sm',
        code: DockerImageCode.fromImageAsset('src/containers/general-ocr/model-standard',
          {
            file: 'Dockerfile.sagemaker',
          },
        ),
      },
    );

    const GeneralOCRTraditionalStandard = new DockerImageFunction(
      this,
      'general-ocr-traditional-standard',
      {
        functionName: 'general-ocr-traditional-standard',
        code: DockerImageCode.fromImageAsset('src/containers/general-ocr-traditional/model-standard',
          {
            file: 'Dockerfile.lambda',
          },
        ),
      },
    );

    const GeneralOCRTraditionalStandardSageMaker = new DockerImageFunction(
      this,
      'general-ocr-traditional-standard-sm',
      {
        functionName: 'general-ocr-traditional-standard-sm',
        code: DockerImageCode.fromImageAsset('src/containers/general-ocr-traditional/model-standard',
          {
            file: 'Dockerfile.sagemaker',
          },
        ),
      },
    );

    const NudityDetection = new DockerImageFunction(
      this,
      'pornography-detection',
      {
        functionName: 'pornography-detection',
        code: DockerImageCode.fromImageAsset('src/containers/pornography-detection/model',
          {
            file: 'Dockerfile.lambda',
          },
        ),
      },
    );

    const NudityDetectionSageMaker = new DockerImageFunction(
      this,
      'pornography-detection-sm',
      {
        functionName: 'pornography-detection-sm',
        code: DockerImageCode.fromImageAsset('src/containers/pornography-detection/model',
          {
            file: 'Dockerfile.sagemaker',
          },
        ),
      },
    );

    const HumanImageSegmentation = new DockerImageFunction(
      this,
      'human-image-segmentation',
      {
        functionName: 'human-image-segmentation',
        code: DockerImageCode.fromImageAsset('src/containers/human-image-segmentation/model',
          {
            file: 'Dockerfile.lambda',
          },
        ),
      },
    );

    const HumanImageSegmentationSageMaker = new DockerImageFunction(
      this,
      'human-image-segmentation-sm',
      {
        functionName: 'human-image-segmentation-sm',
        code: DockerImageCode.fromImageAsset('src/containers/human-image-segmentation/model',
          {
            file: 'Dockerfile.sagemaker',
          },
        ),
      },
    );

    const ObjectRecognition = new DockerImageFunction(
      this,
      'object-recognition',
      {
        functionName: 'object-recognition',
        code: DockerImageCode.fromImageAsset('src/containers/object-recognition/model',
          {
            file: 'Dockerfile.lambda',
          },
        ),
      },
    );

    const ObjectRecognitionSageMaker = new DockerImageFunction(
      this,
      'object-recognition-sm',
      {
        functionName: 'object-recognition-sm',
        code: DockerImageCode.fromImageAsset('src/containers/object-recognition/model',
          {
            file: 'Dockerfile.sagemaker',
          },
        ),
      },
    );

    const FaceComparison = new DockerImageFunction(
      this,
      'face-comparison',
      {
        functionName: 'face-comparison',
        code: DockerImageCode.fromImageAsset('src/containers/face-comparison/model',
          {
            file: 'Dockerfile.lambda',
          },
        ),
      },
    );

    const FaceComparisonSageMaker = new DockerImageFunction(
      this,
      'face-comparison-sm',
      {
        functionName: 'face-comparison-sm',
        code: DockerImageCode.fromImageAsset('src/containers/face-comparison/model',
          {
            file: 'Dockerfile.sagemaker',
          },
        ),
      },
    );

    const FaceDetection = new DockerImageFunction(
      this,
      'face-detection',
      {
        functionName: 'face-detection',
        code: DockerImageCode.fromImageAsset('src/containers/face-detection/model',
          {
            file: 'Dockerfile.lambda',
          },
        ),
      },
    );

    const FaceDetectionSageMaker = new DockerImageFunction(
      this,
      'face-detection-sm',
      {
        functionName: 'face-detection-sm',
        code: DockerImageCode.fromImageAsset('src/containers/face-detection/model',
          {
            file: 'Dockerfile.sagemaker',
          },
        ),
      },
    );

    const HumanAttribute = new DockerImageFunction(
      this,
      'human-attribute',
      {
        functionName: 'human-attribute',
        code: DockerImageCode.fromImageAsset('src/containers/human-attribute/model',
          {
            file: 'Dockerfile.lambda',
          },
        ),
      },
    );

    const HumanAttributeSageMaker = new DockerImageFunction(
      this,
      'human-attribute-sm',
      {
        functionName: 'human-attribute-sm',
        code: DockerImageCode.fromImageAsset('src/containers/human-attribute/model',
          {
            file: 'Dockerfile.sagemaker',
          },
        ),
      },
    );

    const LicensePlate = new DockerImageFunction(
      this,
      'car-license-plate',
      {
        functionName: 'car-license-plate',
        code: DockerImageCode.fromImageAsset('src/containers/license-plate/model',
          {
            file: 'Dockerfile.lambda',
          },
        ),
      },
    );

    const LicensePlateSageMaker = new DockerImageFunction(
      this,
      'car-license-plate-sm',
      {
        functionName: 'car-license-plate-sm',
        code: DockerImageCode.fromImageAsset('src/containers/license-plate/model',
          {
            file: 'Dockerfile.sagemaker',
          },
        ),
      },
    );

    const CustomOcr = new DockerImageFunction(
      this,
      'custom-ocr',
      {
        functionName: 'custom-ocr',
        code: DockerImageCode.fromImageAsset('src/containers/custom-ocr/model',
          {
            file: 'Dockerfile.lambda',
          },
        ),
      },
    );

    const CustomOcrSageMaker = new DockerImageFunction(
      this,
      'custom-ocr-sm',
      {
        functionName: 'custom-ocr-sm',
        code: DockerImageCode.fromImageAsset('src/containers/custom-ocr/model',
          {
            file: 'Dockerfile.sagemaker',
          },
        ),
      },
    );

    const TextSimilarity = new DockerImageFunction(
      this,
      'text-similarity',
      {
        functionName: 'text-similarity',
        code: DockerImageCode.fromImageAsset('src/containers/text-similarity/model',
          {
            file: 'Dockerfile.lambda',
          },
        ),
      },
    );

    const TextSimilaritySageMaker = new DockerImageFunction(
      this,
      'text-similarity-sm',
      {
        functionName: 'text-similarity-sm',
        code: DockerImageCode.fromImageAsset('src/containers/text-similarity/model',
          {
            file: 'Dockerfile.sagemaker',
          },
        ),
      },
    );

    const ImageSimilarity = new DockerImageFunction(
      this,
      'image-similarity',
      {
        functionName: 'image-similarity',
        code: DockerImageCode.fromImageAsset('src/containers/image-similarity/model',
          {
            file: 'Dockerfile.lambda',
          },
        ),
      },
    );

    const ImageSimilaritySageMaker = new DockerImageFunction(
      this,
      'image-similarity-sm',
      {
        functionName: 'image-similarity-sm',
        code: DockerImageCode.fromImageAsset('src/containers/image-similarity/model',
          {
            file: 'Dockerfile.sagemaker',
          },
        ),
      },
    );

    const ImageSuperResolution = new DockerImageFunction(
      this,
      'image-super-resolution',
      {
        functionName: 'image-super-resolution',
        code: DockerImageCode.fromImageAsset('src/containers/image-super-resolution/model',
          {
            file: 'Dockerfile.lambda',
          },
        ),
      },
    );

    const ImageSuperResolutionSageMaker = new DockerImageFunction(
      this,
      'image-super-resolution-sm',
      {
        functionName: 'image-super-resolution-sm',
        code: DockerImageCode.fromImageAsset('src/containers/image-super-resolution/model',
          {
            file: 'Dockerfile.sagemaker',
          },
        ),
      },
    );
  }
}
