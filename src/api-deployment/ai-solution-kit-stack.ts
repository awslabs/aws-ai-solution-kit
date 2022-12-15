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
import { CarLicensePlateFeatureNestedStack } from './features/car-license-plate';
import { CustomOCRFeatureNestedStack } from './features/custom-ocr';
import { FaceComparisonFeatureNestedStack } from './features/face-comparison';
import { FaceDetectionFeatureNestedStack } from './features/face-detection';
import { GeneralOCRFeatureNestedStack } from './features/general-ocr';
import { GeneralOCRTraditionalChineseFeatureNestedStack } from './features/general-ocr-traditional-chinese';
import { HumanAttributeRecognitionFeatureNestedStack } from './features/human-attribute-recognition';
import { HumanImageSegmentationFeatureNestedStack } from './features/human-image-segmentation';
import { ImageSimilarityFeatureNestedStack } from './features/image-similarity';
import { ObjectRecognitionFeatureNestedStack } from './features/object-recognition';
import { PornographyDetectionFeatureNestedStack } from './features/pornography-detection';
import { SuperResolutionGpuFeatureNestedStack } from './features/super-resolution-gpu';
import { TextSimilarityFeatureNestedStack } from './features/text-similarity';

import { CarLicensePlateSageMakerFeatureNestedStack } from './features/sagemaker/car-license-plate-sagemaker';
import { CustomOCRSageMakerFeatureNestedStack } from './features/sagemaker/custom-ocr-sagemaker';
import { FaceComparisonSageMakerFeatureNestedStack } from './features/sagemaker/face-comparison-sagemaker';

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
    this.templateOptions.description = '(SO8023) - AI Solution Kit - Template version v1.2.0. Get started https://www.amazonaws.cn/solutions/ai-solution-kit.';

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
      timeout: Duration.seconds(19),
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
      const customOCRSageMakerFeatureNestedStack = new CustomOCRSageMakerFeatureNestedStack(this, 'Custom-OCR-SageMaker', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
      });
      (customOCRSageMakerFeatureNestedStack.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionCustomOCRSageMaker');
      this.addOutput(cfnTemplate, api.restApiId, 'custom-ocr', 'Custom OCR SageMaker', 'ConditionCustomOCRSageMaker');
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
      this.addOutput(cfnTemplate, api.restApiId, 'car-license-plate', 'Car License Plate SageMaker', 'ConditionCarLicensePlateSageMaker');
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
      const faceComparison = new FaceComparisonFeatureNestedStack(this, 'Face-Comparison-SageMaker', {
        restApi: api,
        customAuthorizationType: authType,
        ecrDeployment: ecrDeployment,
        updateCustomResourceProvider: updateCustomResourceProvider,
        ecrRegistry: props.ecrRegistry,
      });
      (faceComparison.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionFaceComparisonSageMaker');
      this.addOutput(cfnTemplate, api.restApiId, 'face-comparison', 'Face Comparison SageMaker', 'ConditionFaceComparisonSageMaker');
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

    // Feature: Super Resolution GPU
    {
      const map = new CfnMapping(this, 'instanceTypeMapping', {
        mapping: {
          'yes-ml.g4dn.xlarge': { value: 'ml.g4dn.xlarge' },
          'yes-ml.g4dn.2xlarge': { value: 'ml.g4dn.2xlarge' },
          'yes-ml.g4dn.8xlarge': { value: 'ml.g4dn.8xlarge' },
        },
      });
      const instanceType = map.findInMap(cfnTemplate.getParameter('ImageSuperResolution').valueAsString, 'value');
      const superResolutionGpu = new SuperResolutionGpuFeatureNestedStack(this, 'Super-Resolution', {
        restApi: api,
        customAuthorizationType: authType,
        updateCustomResourceProvider: updateCustomResourceProvider,
        instanceType: instanceType,
      });
      (superResolutionGpu.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition('ConditionImageSuperResolution');
      this.addOutput(cfnTemplate, api.restApiId, 'super-resolution', 'Super Resolution', 'ConditionImageSuperResolution');
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
