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
} from "aws-cdk-lib";
import {
  AuthorizationType,
  Cors,
  Deployment,
  EndpointType,
  MethodLoggingLevel,
  RestApi,
  Stage,
} from "aws-cdk-lib/aws-apigateway";
import { Effect, PolicyStatement } from "aws-cdk-lib/aws-iam";
import { Code, Function, Runtime } from "aws-cdk-lib/aws-lambda";
import { CfnInclude } from "aws-cdk-lib/cloudformation-include";
import { Provider } from "aws-cdk-lib/custom-resources";
import { Construct } from "constructs";
import * as path from "path";
import { DockerImageName, ECRDeployment } from "../lib/cdk-ecr-deployment/lib";
import { FeatureNestedStack } from "./feature-nested-stack";
import { GreenScreenMattingSMFeatureNestedStack } from "./features/green-screen-matting-sm";

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

export class AISolutionKitInf1Stack extends Stack {
  constructor(scope: Construct, id: string, props: AISolutionKitStackProps) {
    super(scope, id, props);
    this.templateOptions.description =
      "(SO8023) - AI Solution Kit - Template version v1.2.0. Get started https://www.amazonaws.cn/solutions/ai-solution-kit.";

    const cfnTemplate = new CfnInclude(this, "CfnTemplate", {
      templateFile: path.join(__dirname, "parameter-group-inf1.template"),
    });

    const api = new RestApi(this, "AiSolutionKitApi", {
      restApiName: "AI Solution Kit API",
      description:
        "AI Solutions Kit REST API. Get started https://www.amazonaws.cn/solutions/ai-solution-kit.",
      deploy: false,
      defaultCorsPreflightOptions: {
        allowHeaders: [
          "Content-Type",
          "X-Amz-Date",
          "Authorization",
          "X-Api-Key",
        ],
        allowMethods: ["POST", "OPTION"],
        allowCredentials: true,
        allowOrigins: Cors.ALL_ORIGINS,
      },
      endpointConfiguration: {
        types: [EndpointType.REGIONAL],
      },
    });

    const apiLambda = new Function(this, "apihandler", {
      handler: "api_resource.lambda_handler",
      runtime: Runtime.PYTHON_3_9,
      code: Code.fromAsset(path.join(__dirname, "../lib/api_resource"), {
        bundling: {
          image: Runtime.PYTHON_3_9.bundlingImage,
          command: [
            "bash",
            "-c",
            [
              "cp -r /asset-input/* /asset-output/",
              "pip install -r requirements.txt --no-cache-dir --target /asset-output",
            ].join(" && "),
          ],
        },
      }),
      memorySize: 2048,
      timeout: Duration.seconds(19),
      environment: {
        REST_API_ID: api.restApiId,
        STAGE_NAME: cfnTemplate.getParameter("APIGatewayStageName")
          .valueAsString,
        CUSTOM_AUTH_TYPE: cfnTemplate.getParameter("APIGatewayAuthorization")
          .valueAsString,
      },
    });

    const updateCustomResourceProvider = new Provider(this, "apiprovider", {
      onEventHandler: apiLambda,
    });

    apiLambda.addToRolePolicy(
      new PolicyStatement({
        effect: Effect.ALLOW,
        actions: ["apigateway:*"],
        resources: ["*"],
      })
    );

    const ecrDeployment = new ECRDeployment(
      this,
      "ai-solution-kit-deployment",
      {
        src: new DockerImageName(""),
        dest: new DockerImageName(""),
      }
    );

    const authType = `${
      cfnTemplate.getParameter("APIGatewayAuthorization").valueAsString
    }` as AuthorizationType;

    const deployment = new Deployment(this, "new_deployment", {
      api: api,
    });

    const deploymentStage = new Stage(this, "ai-solution-kit-prod", {
      stageName: cfnTemplate.getParameter("APIGatewayStageName").valueAsString,
      deployment: deployment,
      dataTraceEnabled: true,
      loggingLevel: MethodLoggingLevel.INFO,
    });

    const chinaCondition = new CfnCondition(this, "IsChinaRegionCondition", {
      expression: Fn.conditionEquals(Aws.PARTITION, "aws-cn"),
    });

    const invokeUrl = Fn.conditionIf(
      "IsChinaRegionCondition",
      `https://${api.restApiId}.execute-api.${Aws.REGION}.amazonaws.com.cn/${
        cfnTemplate.getParameter("APIGatewayStageName").valueAsString
      }`,
      `https://${api.restApiId}.execute-api.${Aws.REGION}.amazonaws.com/${
        cfnTemplate.getParameter("APIGatewayStageName").valueAsString
      }`
    );
    // Feature: Green Screen Matting SM
    {
      const greenScreenMatting = new GreenScreenMattingSMFeatureNestedStack(
        this,
        "Human-Image-Segmentation",
        {
          restApi: api,
          customAuthorizationType: authType,
          ecrDeployment: ecrDeployment,
          updateCustomResourceProvider: updateCustomResourceProvider,
          ecrRegistry: props.ecrRegistry,
        }
      );
      (greenScreenMatting.nestedStackResource as CfnStack).cfnOptions.condition = cfnTemplate.getCondition(
        "ConditionHumanImageSegmentation"
      );
      this.addOutput(
        cfnTemplate,
        api.restApiId,
        "human-segmentation",
        "Human Image Segmentation",
        "ConditionHumanImageSegmentation"
      );
    }
  }

  private addOutput(
    cfnTemplate: CfnInclude,
    restApiId: string,
    apiPath: string,
    outputName: string,
    conditionName: string
  ) {
    const invokeUrl = Fn.conditionIf(
      "IsChinaRegionCondition",
      `https://${restApiId}.execute-api.${Aws.REGION}.amazonaws.com.cn/${
        cfnTemplate.getParameter("APIGatewayStageName").valueAsString
      }/${apiPath}/`,
      `https://${restApiId}.execute-api.${Aws.REGION}.amazonaws.com/${
        cfnTemplate.getParameter("APIGatewayStageName").valueAsString
      }/${apiPath}/`
    );
    new CfnOutput(this, outputName, {
      value: invokeUrl.toString(),
      description: `Invoke URL for ${outputName}`,
    }).condition = cfnTemplate.getCondition(conditionName);
  }
}
