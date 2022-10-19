import {
  Aws,
  CfnCondition, CustomResource, Duration, Fn, RemovalPolicy, Stack,
  StackProps
} from 'aws-cdk-lib';
import { Repository } from 'aws-cdk-lib/aws-ecr';
import {
  Role,
  ServicePrincipal
} from 'aws-cdk-lib/aws-iam';
import { DockerImageCode, DockerImageFunction } from 'aws-cdk-lib/aws-lambda';
import { CfnInclude } from 'aws-cdk-lib/cloudformation-include';
import { Construct } from 'constructs';
import * as path from 'path';
import {
  DockerImageName,
  ECRDeployment
} from '../lib/cdk-ecr-deployment/lib';
import { FeatureNestedStack } from './feature-nested-stack';

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

// Standalone stack for general OCR API only
export class AISolutionKitChineseOCRStack extends Stack {
  constructor(scope: Construct, id: string, props: AISolutionKitStackProps) {

    super(scope, id, props);
    this.templateOptions.description = '(SO8023) - AI Solution Kit - Template version v1.2.0. Get started https://www.amazonaws.cn/solutions/ai-solution-kit.';

    const ecrDeployment = new ECRDeployment(this, 'ai-solution-kit-deployment', {
      src: new DockerImageName(''),
      dest: new DockerImageName(''),
    });

    // Feature: General OCR Simplified
    {
      Repository.fromRepositoryName(this, `ai-solution-kit-general-ocr-repository`, `ai-solution-kit-general-ocr`);
      const stackRepo = new Repository(this, `ai-solution-kit-general-ocr`, {
        repositoryName: `ai-solution-kit-general-ocr`,
        removalPolicy: RemovalPolicy.RETAIN,
      });

      // Lambda deployment
      const ecrCR = new CustomResource(this, `general-ocr-ecr`, {
        serviceToken: ecrDeployment.serviceToken,
        resourceType: 'Custom::AISolutionKitECRLambda',
        properties: {
          SrcImage: `docker://${props.ecrRegistry}/general-ocr-standard:latest`,
          DestImage: `docker://${stackRepo.repositoryUri}`,
          RepositoryName: `${stackRepo.repositoryName}`,
        },
      });
      const myRole = new Role(this, `general-ocr-role`, {
        assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
      });
      const appFunction = new DockerImageFunction(
        this,
        `general-ocr-app`,
        {
          code: DockerImageCode.fromEcr(
            Repository.fromRepositoryName(this, `general-ocr-lambda`, stackRepo.repositoryName),
            {
              tag: 'latest',
            },
          ),
          timeout: Duration.seconds(19),
          memorySize: 8192,
          role: myRole,
        },
      );
    }
    // Feature: General OCR - Traditional Chinese
    {
      Repository.fromRepositoryName(this, `ai-solution-kit-general-ocr-traditional-chinese-repository`, `ai-solution-kit-general-ocr-traditional-chinese`);
      const stackRepo = new Repository(this, `ai-solution-kit-traditional-chinese-general-ocr`, {
        repositoryName: `ai-solution-kit-general-ocr-traditional-chinese`,
        removalPolicy: RemovalPolicy.RETAIN,
      });

      // Lambda deployment
      const ecrCR = new CustomResource(this, `general-ocr-traditional-chinese-ecr`, {
        serviceToken: ecrDeployment.serviceToken,
        resourceType: 'Custom::AISolutionKitECRLambda',
        properties: {
          SrcImage: `docker://${props.ecrRegistry}/general-ocr-traditional-standard:latest`,
          DestImage: `docker://${stackRepo.repositoryUri}`,
          RepositoryName: `${stackRepo.repositoryName}`,
        },
      });
      const myRole = new Role(this, `general-ocr-traditional-chinese-role`, {
        assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
      });
      const appFunction = new DockerImageFunction(
        this,
        `general-ocr-traditional-chinese-app`,
        {
          code: DockerImageCode.fromEcr(
            Repository.fromRepositoryName(this, `general-ocr-traditional-chinese-lambda`, stackRepo.repositoryName),
            {
              tag: 'latest',
            },
          ),
          timeout: Duration.seconds(19),
          memorySize: 8192,
          role: myRole,
        },
      );
    }

  }

}
