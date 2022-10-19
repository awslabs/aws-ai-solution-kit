#!/usr/bin/env node
import { App, Aspects } from 'aws-cdk-lib';
import { BootstraplessStackSynthesizer, CompositeECRRepositoryAspect } from 'cdk-bootstrapless-synthesizer';
import 'source-map-support/register';
import { AISolutionKitIsolatedStack } from './api-deployment/ai-solution-kit-isolated-stack';
import { AISolutionKitSMStack } from './api-deployment/ai-solution-kit-sm-stack';
import { AISolutionKit3GStack } from './api-deployment/ai-solution-kit-3g-stack';
import { AISolutionKitStack } from './api-deployment/ai-solution-kit-stack';
import { AISolutionKitOcrBlankStack } from './api-deployment/ai-solution-kit-ocr-blank-stack';
import { AISolutionKitChineseOCRStack } from './api-deployment/ai-solution-kit-chinese-ocr-stack';
import { LambdaContainersStack } from './containers/lambda-containers-stack';


const app = new App();
const buildContainers = app.node.tryGetContext('build-container');
const deployContainers = app.node.tryGetContext('deploy-container');

if (buildContainers === 'true' || deployContainers === 'true') {
  console.log('Building containers');
  // Docker images building stack
  new LambdaContainersStack(app, 'Lambda-Containers-Stack', {
    synthesizer: synthesizer(),
    tags: {
      app: 'ai-solution-kit',
    },
  });
} else {
  // CloudFormation deployment stack - Default
  const ecrRegistry = app.node.tryGetContext('ecrRegistry');
  console.log('Use ECR Resistry: ' + ecrRegistry);

  new AISolutionKitStack(app, 'AI-Solution-Kit', {
    synthesizer: synthesizer(),
    ecrRegistry: ecrRegistry === 'undefined' ? 'public.ecr.aws/aws-gcr-solutions/aws-gcr-ai-solution-kit' : ecrRegistry,
    tags: {
      app: 'ai-solution-kit',
    },
  });

  new AISolutionKitIsolatedStack(app, 'AI-Solution-Kit-Isolated', {
    synthesizer: synthesizer(),
    ecrRegistry: ecrRegistry === 'undefined' ? 'public.ecr.aws/aws-gcr-solutions/aws-gcr-ai-solution-kit' : ecrRegistry,
    tags: {
      app: 'ai-solution-kit',
    },
  });

  new AISolutionKitSMStack(app, 'AI-Solution-Kit-SM', {
    synthesizer: synthesizer(),
    ecrRegistry: ecrRegistry === 'undefined' ? 'public.ecr.aws/aws-gcr-solutions/aws-gcr-ai-solution-kit' : ecrRegistry,
    tags: {
      app: 'ai-solution-kit',
    },
  });

  new AISolutionKit3GStack(app, 'AI-Solution-Kit-3G', {
    synthesizer: synthesizer(),
    ecrRegistry: ecrRegistry === 'undefined' ? 'public.ecr.aws/aws-gcr-solutions/aws-gcr-ai-solution-kit' : ecrRegistry,
    tags: {
      app: 'ai-solution-kit',
    },
  });

  new AISolutionKitOcrBlankStack(app, 'AI-Solution-Kit-Ocr-Blank', {
    synthesizer: synthesizer(),
    ecrRegistry: ecrRegistry === 'undefined' ? 'public.ecr.aws/aws-gcr-solutions/aws-gcr-ai-solution-kit' : ecrRegistry,
    tags: {
      app: 'ai-solution-kit',
    },
  });

  new AISolutionKitChineseOCRStack(app, 'AI-Solution-Kit-Ocr', {
    synthesizer: synthesizer(),
    ecrRegistry: ecrRegistry === 'undefined' ? 'public.ecr.aws/aws-gcr-solutions/aws-gcr-ai-solution-kit' : ecrRegistry,
    tags: {
      app: 'ai-solution-kit',
    },
  });
}

if (process.env.USE_BSS) {
  Aspects.of(app).add(new CompositeECRRepositoryAspect());
}

app.synth();

function synthesizer() {
  return process.env.USE_BSS ? new BootstraplessStackSynthesizer() : undefined;
}