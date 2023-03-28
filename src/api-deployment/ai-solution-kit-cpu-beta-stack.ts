import * as path from 'path';
import {
  Aws,
  CfnCondition,
  CfnMapping,
  CfnOutput,
  CfnStack,
  Duration,
  Fn,
  Stack,
  StackProps,
} from 'aws-cdk-lib';
import {
  AuthorizationType,
  Cors,
  Deployment,
  EndpointType,
  MethodLoggingLevel,
  RestApi,
  Stage,
} from 'aws-cdk-lib/aws-apigateway';
import {
  Effect,
  PolicyStatement,
} from 'aws-cdk-lib/aws-iam';
import {
  Code,
  Function,
  Runtime,
} from 'aws-cdk-lib/aws-lambda';
import { CfnInclude } from 'aws-cdk-lib/cloudformation-include';
import { Provider } from 'aws-cdk-lib/custom-resources';
import { Construct } from 'constructs';
import {
  DockerImageName,
  ECRDeployment,
} from '../lib/cdk-ecr-deployment/lib';
import { FeatureNestedStack } from './feature-nested-stack';
import { ApiExplorerNestedStack } from './features/api-explorer';
import { CarLicensePlateFeatureNestedStack } from './features/lambda/car-license-plate';
import { CustomOCRFeatureNestedStack } from './features/lambda/custom-ocr';
import { FaceComparisonFeatureNestedStack } from './features/lambda/face-comparison';
import { FaceDetectionFeatureNestedStack } from './features/lambda/face-detection';
import { GeneralOCRFeatureNestedStack } from './features/lambda/general-ocr';
import { GeneralOCRTraditionalChineseFeatureNestedStack } from './features/lambda/general-ocr-traditional-chinese';
import { HumanAttributeRecognitionFeatureNestedStack } from './features/lambda/human-attribute-recognition';
import { HumanImageSegmentationFeatureNestedStack } from './features/lambda/human-image-segmentation';
import { ImageSimilarityFeatureNestedStack } from './features/lambda/image-similarity';
import { ObjectRecognitionFeatureNestedStack } from './features/lambda/object-recognition';
import { PornographyDetectionFeatureNestedStack } from './features/lambda/pornography-detection';
import { TextSimilarityFeatureNestedStack } from './features/lambda/text-similarity';

import { CarLicensePlateSageMakerFeatureNestedStack } from './features/sagemaker/car-license-plate-sagemaker';
import { CustomOCRCpuBetaSageMakerFeatureNestedStack } from './features/sagemaker/custom-ocr-cpu-beta-sagemaker';
import { FaceComparisonSageMakerFeatureNestedStack } from './features/sagemaker/face-comparison-sagemaker';
import { FaceDetectionSageMakerFeatureNestedStack } from './features/sagemaker/face-detection-sagemaker';
import { GeneralOCRSageMakerFeatureNestedStack } from './features/sagemaker/general-ocr-sagemaker';
import { GeneralOCRTraditionalChineseSageMakerFeatureNestedStack } from './features/sagemaker/general-ocr-traditional-chinese-sagemaker';
import { HumanAttributeRecognitionSageMakerFeatureNestedStack } from './features/sagemaker/human-attribute-recognition-sagemaker';
import { HumanImageSegmentationSageMakerFeatureNestedStack } from './features/sagemaker/human-image-segmentation-sagemaker';
import { ImageSimilaritySageMakerFeatureNestedStack } from './features/sagemaker/image-similarity-sagemaker';
import { ObjectRecognitionSageMakerFeatureNestedStack } from './features/sagemaker/object-recognition-sagemaker';
import { PornographyDetectionSageMakerFeatureNestedStack } from './features/sagemaker/pornography-detection-sagemaker';
import { SuperResolutionSageMakerFeatureNestedStack } from './features/sagemaker/super-resolution-sagemaker';
import { TextSimilaritySageMakerFeatureNestedStack } from './features/sagemaker/text-similarity-sagemaker';

export interface FeatureProps {
  readonly featureStack: FeatureNestedStack;
  readonly title: string;
  readonly description: string;
  readonly defaultInstall: string;
  readonly sageMakerInstanceTypes?: string[];
}

export interface AISolutionKitStackProps extends StackProps {
  readonly ecrRegistry: string;
}

export class AISolutionKitStack extends Stack {
  constructor(scope: Construct, id: string, props: AISolutionKitStackProps) {

    super(scope, id, props);
    this.templateOptions.description = '(SO8023) - AI Solution Kit - Template version v1.3.0. Get started https://www.amazonaws.cn/solutions/ai-solution-kit.';

    const cfnTemplate = new CfnInclude(this, 'CfnTemplate', {
      templateFile: path.join(__dirname, 'parameter-group.template'),
    });

    const api = new RestApi(this, 'AiSolutionKitApi', {
      restApiName: 'AI Solution Kit API',
      description: 'AI Solutions Kit REST API. Get started https://www.amazonaws.cn/solutions/ai-solution-kit.',
      deploy: false,
      defaultCorsPreflightOptions: {
        allowHeaders: [
          'Content-Type',
          'X-Amz-Date',
          'Authorization',
          'X-Api-Key',
        ],
        allowMethods: ['POST', 'OPTION'],
        allowCredentials: true,
        allowOrigins: Cors.ALL_ORIGINS,
      },
      endpointConfiguration: {
        types: [EndpointType.REGIONAL],
      },
    });

    const apiLambda = new Function(this, 'apihandler', {
      handler: 'api_resource.lambda_handler',
      runtime: Runtime.PYTHON_3_9,
      code: Code.fromAsset(path.join(__dirname, '../lib/api_resource'), {
        bundling: {
          image: Runtime.PYTHON_3_9.bundlingImage,
          command: [
            'bash', '-c', [
              'cp -r /asset-input/* /asset-output/',
              'pip install -r requirements.txt --no-cache-dir --target /asset-output',
            ].join(' && '),
          ],
        },
      }),
      memorySize: 2048,
      timeout: Duration.minutes(2),
      environment: {
        REST_API_ID: api.restApiId,
        STAGE_NAME: cfnTemplate.getParameter('APIGatewayStageName').valueAsString,
        CUSTOM_AUTH_TYPE: cfnTemplate.getParameter('APIGatewayAuthorization').valueAsString,
      },
    });

    const updateCustomResourceProvider = new Provider(this, 'apiprovider', {
      onEventHandler: apiLambda,
    });

    apiLambda.addToRolePolicy(
      new PolicyStatement({
        effect: Effect.ALLOW,
        actions: [
          'apigateway:*',
        ],
        resources: [
          '*',
        ],
      }),
    );

    const ecrDeployment = new ECRDeployment(this, 'ai-solution-kit-deployment', {
      src: new DockerImageName(''),
      dest: new DockerImageName(''),
    });

    const authType = `${cfnTemplate.getParameter('APIGatewayAuthorization').valueAsString}` as AuthorizationType;

    const deployment = new Deployment(this, 'new_deployment', {
      api: api,
    });

    const deploymentStage = new Stage(this, 'ai-solution-kit-prod', {
      stageName: cfnTemplate.getParameter('APIGatewayStageName').valueAsString,
      deployment: deployment,
      dataTraceEnabled: true,
      loggingLevel: MethodLoggingLevel.INFO,
    });

    const chinaCondition = new CfnCondition(this,
      'IsChinaRegionCondition',
      { expression: Fn.conditionEquals(Aws.PARTITION, 'aws-cn') });

    const invokeUrl = Fn.conditionIf(
      'IsChinaRegionCondition',
      `https://${api.restApiId}.execute-api.${Aws.REGION}.amazonaws.com.cn/${cfnTemplate.getParameter('APIGatewayStageName').valueAsString}`,
      `https://${api.restApiId}.execute-api.${Aws.REGION}.amazonaws.com/${cfnTemplate.getParameter('APIGatewayStageName').valueAsString}`,
    );

    // Feature: API Explorer
    {
      const apiExplorer = new ApiExplorerNestedStack(this, 'Api-Explorer', {
        restApi: api,
        invokeUrl: invokeUrl.toString(),
        authorizationType: cfnTemplate.getParameter('APIGatewayAuthorization').valueAsString,
      });
      (apiExplorer.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionAPIExplorer');
      this.addOutput(cfnTemplate, api.restApiId, 'api-explorer', 'API Explorer', 'ConditionAPIExplorer');
    }

    // Feature: General OCR
    {
      const generalOCR = new GeneralOCRFeatureNestedStack(this, 'General-OCR', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props?.ecrRegistry,
        lambdaMemorySize: 8192,
      });
      (generalOCR.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionGeneralOCR');
      this.addOutput(cfnTemplate, api.restApiId, 'general-ocr-advanced', 'General OCR Advanced', 'ConditionGeneralOCR');
      this.addOutput(cfnTemplate, api.restApiId, 'general-ocr-standard', 'General OCR Standard', 'ConditionGeneralOCR');
    }

    // Feature: General OCR SageMaker
    {
      const generalOCRSageMaker = new GeneralOCRSageMakerFeatureNestedStack(this, 'General-OCR-SageMaker', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props?.ecrRegistry,
      });
      (generalOCRSageMaker.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionGeneralOCRSageMaker');
      this.addOutput(cfnTemplate, api.restApiId, 'general-ocr-standard-ml', 'General OCR Standard SageMaker', 'ConditionGeneralOCRSageMaker');
    }

    // Feature: General OCR - Traditional Chinese
    {
      const generalOCRTraditionalChinese = new GeneralOCRTraditionalChineseFeatureNestedStack(this, 'General-OCR-Traditional-Chinese', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
        lambdaMemorySize: 8192,
      });
      (generalOCRTraditionalChinese.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionGeneralOCRTraditionalChinese');
      this.addOutput(cfnTemplate, api.restApiId, 'general-ocr-traditional-chinese', 'General OCR Traditional Chinese', 'ConditionGeneralOCRTraditionalChinese');
    }

    // Feature: General OCR - Traditional Chinese SageMaker
    {
      const generalOCRTraditionalChineseSageMaker = new GeneralOCRTraditionalChineseSageMakerFeatureNestedStack(this, 'General-OCR-Traditional-Chinese-SageMaker', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
      });
      (generalOCRTraditionalChineseSageMaker.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionGeneralOCRTraditionalChineseSageMaker');
      this.addOutput(cfnTemplate, api.restApiId, 'general-ocr-traditional-chinese-ml', 'General OCR Traditional Chinese SageMaker', 'ConditionGeneralOCRTraditionalChineseSageMaker');
    }

    // Feature: Custom OCR
    {
      const customOCRFeatureNestedStack = new CustomOCRFeatureNestedStack(this, 'Custom-OCR', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
        lambdaMemorySize: 10240,
      });
      (customOCRFeatureNestedStack.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionCustomOCR');
      this.addOutput(cfnTemplate, api.restApiId, 'custom-ocr', 'Custom OCR', 'ConditionCustomOCR');
    }

    // Feature: Custom OCR SageMaker
    {
      const customOCRSageMakerFeatureNestedStack = new CustomOCRCpuBetaSageMakerFeatureNestedStack(this, 'Custom-OCR-SageMaker', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
      });
      (customOCRSageMakerFeatureNestedStack.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionCustomOCRSageMaker');
      this.addOutput(cfnTemplate, api.restApiId, 'custom-ocr-ml', 'Custom OCR SageMaker', 'ConditionCustomOCRSageMaker');
    }

    // Feature: Car Licenst Plate
    {
      const carLicensePlate = new CarLicensePlateFeatureNestedStack(this, 'Car-License-Plate', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
        lambdaMemorySize: 8192,
      });
      (carLicensePlate.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionCarLicensePlate');
      this.addOutput(cfnTemplate, api.restApiId, 'car-license-plate', 'Car License Plate', 'ConditionCarLicensePlate');
    }

    // Feature: Car Licenst Plate SageMaker
    {
      const carLicensePlateSageMaker = new CarLicensePlateSageMakerFeatureNestedStack(this, 'Car-License-Plate-SageMaker', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
      });
      (carLicensePlateSageMaker.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionCarLicensePlateSageMaker');
      this.addOutput(cfnTemplate, api.restApiId, 'car-license-plate-ml', 'Car License Plate SageMaker', 'ConditionCarLicensePlateSageMaker');
    }

    // Feature: Face Comparison
    {
      const faceComparison = new FaceComparisonFeatureNestedStack(this, 'Face-Comparison', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
        lambdaMemorySize: 8192,
      });
      (faceComparison.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionFaceComparison');
      this.addOutput(cfnTemplate, api.restApiId, 'face-comparison', 'Face Comparison', 'ConditionFaceComparison');
    }

    // Feature: Face Comparison SageMaker
    {
      const faceComparisonSageMaker = new FaceComparisonSageMakerFeatureNestedStack(this, 'Face-Comparison-SageMaker', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
      });
      (faceComparisonSageMaker.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionFaceComparisonSageMaker');
      this.addOutput(cfnTemplate, api.restApiId, 'face-comparison-ml', 'Face Comparison SageMaker', 'ConditionFaceComparisonSageMaker');
    }

    // Feature: Face Detection
    {
      const faceDetection = new FaceDetectionFeatureNestedStack(this, 'Face-Detection', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
        lambdaMemorySize: 8192,
      });
      (faceDetection.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionFaceDetection');
      this.addOutput(cfnTemplate, api.restApiId, 'face-detection', 'Face Detection', 'ConditionFaceDetection');
    }

    // Feature: Face Detection SageMaker
    {
      const faceDetectionSageMaker = new FaceDetectionSageMakerFeatureNestedStack(this, 'Face-Detection-SageMaker', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
      });
      (faceDetectionSageMaker.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionFaceDetectionSageMaker');
      this.addOutput(cfnTemplate, api.restApiId, 'face-detection-ml', 'Face Detection SageMaker', 'ConditionFaceDetectionSageMaker');
    }

    // Feature: Human Attribute Recognition
    {
      const humanAttributeRecognition = new HumanAttributeRecognitionFeatureNestedStack(this, 'Human-Attribute-Recognition', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
        lambdaMemorySize: 8192,
      });
      (humanAttributeRecognition.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionHumanAttributeRecognition');
      this.addOutput(cfnTemplate, api.restApiId, 'human-attribute', 'Human Attribute Recognition', 'ConditionHumanAttributeRecognition');
    }

    // Feature: Human Attribute Recognition SageMaker
    {
      const humanAttributeRecognitionSageMaker = new HumanAttributeRecognitionSageMakerFeatureNestedStack(this, 'Human-Attribute-Recognition-SageMaker', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
      });
      (humanAttributeRecognitionSageMaker.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionHumanAttributeRecognitionSageMaker');
      this.addOutput(cfnTemplate, api.restApiId, 'human-attribute-ml', 'Human Attribute Recognition SageMaker', 'ConditionHumanAttributeRecognitionSageMaker');
    }

    // Feature: Human Image Segmentation
    {
      const humanImageSegmentation = new HumanImageSegmentationFeatureNestedStack(this, 'Human-Image-Segmentation', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
        lambdaMemorySize: 10240,
      });
      (humanImageSegmentation.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionHumanImageSegmentation');
      this.addOutput(cfnTemplate, api.restApiId, 'human-segmentation', 'Human Image Segmentation', 'ConditionHumanImageSegmentation');
    }

    // Feature: Human Image Segmentation SageMaker
    {
      const humanImageSegmentationSageMaker = new HumanImageSegmentationSageMakerFeatureNestedStack(this, 'Human-Image-Segmentation-SageMaker', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
      });
      (humanImageSegmentationSageMaker.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionHumanImageSegmentationSageMaker');
      this.addOutput(cfnTemplate, api.restApiId, 'human-segmentation-ml', 'Human Image Segmentation SageMaker', 'ConditionHumanImageSegmentationSageMaker');
    }

    // Feature: Pornography Detection
    {
      const pornographyDetection = new PornographyDetectionFeatureNestedStack(this, 'Pornography-Detection', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
        lambdaMemorySize: 8192,
      });
      (pornographyDetection.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionPornographyDetection');
      this.addOutput(cfnTemplate, api.restApiId, 'pornography-detection', 'Pornography Detection', 'ConditionPornographyDetection');
    }

    // Feature: Pornography Detection SageMaker
    {
      const pornographyDetectionSageMaker = new PornographyDetectionSageMakerFeatureNestedStack(this, 'Pornography-Detection-SageMaker', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
      });
      (pornographyDetectionSageMaker.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionPornographyDetectionSageMaker');
      this.addOutput(cfnTemplate, api.restApiId, 'pornography-detection-ml', 'Pornography Detection SageMaker', 'ConditionPornographyDetectionSageMaker');
    }

    // Feature: Object Recognition
    {
      const objectRecognition = new ObjectRecognitionFeatureNestedStack(this, 'Object-Recognition', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
        lambdaMemorySize: 10240,
      });
      (objectRecognition.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionObjectRecognition');
      this.addOutput(cfnTemplate, api.restApiId, 'object-recognition', 'Object Recognition', 'ConditionObjectRecognition');
    }

    // Feature: Object Recognition SageMaker
    {
      const objectRecognitionSageMaker = new ObjectRecognitionSageMakerFeatureNestedStack(this, 'Object-Recognition-SageMaker', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
      });
      (objectRecognitionSageMaker.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionObjectRecognitionSageMaker');
      this.addOutput(cfnTemplate, api.restApiId, 'object-recognition-ml', 'Object Recognition SageMaker', 'ConditionObjectRecognitionSageMaker');
    }

    // Feature: Text Similarity
    {
      const textSimilarity = new TextSimilarityFeatureNestedStack(this, 'Text-Similarity', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
        lambdaMemorySize: 8192,
      });
      (textSimilarity.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionTextSimilarity');
      this.addOutput(cfnTemplate, api.restApiId, 'text-similarity', 'Text Similarity', 'ConditionTextSimilarity');
    }

    // Feature: Text Similarity SageMaker
    {
      const textSimilaritySageMaker = new TextSimilaritySageMakerFeatureNestedStack(this, 'Text-Similarity-SageMaker', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
      });
      (textSimilaritySageMaker.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionTextSimilaritySageMaker');
      this.addOutput(cfnTemplate, api.restApiId, 'text-similarity-ml', 'Text Similarity SageMaker', 'ConditionTextSimilaritySageMaker');
    }

    // Feature: Image Similarity
    {
      const imageSimilarity = new ImageSimilarityFeatureNestedStack(this, 'Image-Similarity', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
        lambdaMemorySize: 8192,
      });
      (imageSimilarity.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionImageSimilarity');
      this.addOutput(cfnTemplate, api.restApiId, 'image-similarity', 'Image Similarity', 'ConditionImageSimilarity');
    }

    // Feature: Image Similarity SageMaker
    {
      const imageSimilaritySageMaker = new ImageSimilaritySageMakerFeatureNestedStack(this, 'Image-Similarity-SageMaker', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
      });
      (imageSimilaritySageMaker.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionImageSimilaritySageMaker');
      this.addOutput(cfnTemplate, api.restApiId, 'image-similarity-ml', 'Image Similarity SageMaker', 'ConditionImageSimilaritySageMaker');
    }

    // Feature: Super Resolution SageMaker
    {
      const superResolutionSageMaker = new SuperResolutionSageMakerFeatureNestedStack(this, 'Super-Resolution-SageMaker', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
      });
      (superResolutionSageMaker.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionImageSuperResolutionSageMaker');
      this.addOutput(cfnTemplate, api.restApiId, 'super-resolution-ml', 'Super Resolution SageMaker', 'ConditionImageSuperResolutionSageMaker');
    }

    // Stage base URL
    {
      new CfnOutput(this, 'Stage base URL', {
        value: `${invokeUrl.toString()}/`,
        description: 'Stage base URL',
      });
    }
  }

  private addOutput(cfnTemplate: CfnInclude, restApiId: string, apiPath: string, outputName: string, conditionName: string) {
    const invokeUrl = Fn.conditionIf(
      'IsChinaRegionCondition',
      `https://${restApiId}.execute-api.${Aws.REGION}.amazonaws.com.cn/${cfnTemplate.getParameter('APIGatewayStageName').valueAsString}/${apiPath}/`,
      `https://${restApiId}.execute-api.${Aws.REGION}.amazonaws.com/${cfnTemplate.getParameter('APIGatewayStageName').valueAsString}/${apiPath}/`,
    );
    new CfnOutput(this, outputName, {
      value: invokeUrl.toString(),
      description: `Invoke URL for ${outputName}`,
    }).condition = cfnTemplate.getCondition(conditionName);
  }
}
