import {
  App,
  Stack,
  StackProps,
} from 'aws-cdk-lib';

import { Construct } from 'constructs';
import { SdTrainDeployStack } from './sd-train/sd-train-deploy-stack';


export class Middleware extends Stack {
  constructor(scope: Construct, id: string, props: StackProps = {}) {
    super(scope, id, props);

  }
}

// for development, use account/region from cdk cli
const devEnv = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

const app = new App();

// new Middleware(app, 'stable-diffusion-extensions-dev', { env: devEnv });

// new TxtImgInferenceCdkStack(app, 'TxtImgInferenceCdkStack-dev', { env: devEnv });

// new SdTrainDeployStack(app, 'SdTrainDeployStack-dev', { env: devEnv });


new SdTrainDeployStack(app, 'SdDreamBoothTrainStack', { env: devEnv });

// new SDAsyncInferenceStack(app, 'SdAsyncInferenceStack-dev', {
//   env: devEnv,
//   api_gate_way: trainStack.apiGateway,
//   // api_id: restful_api_id,
//   s3_bucket: trainStack.s3Bucket,
//   training_table: trainStack.trainingTable });

// inferenceStack.addDependency(trainStack)

app.synth();
