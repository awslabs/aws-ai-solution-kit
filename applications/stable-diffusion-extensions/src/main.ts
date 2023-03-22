import { App, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export class Middleware extends Stack {
  constructor(scope: Construct, id: string, props: StackProps = {}) {
    super(scope, id, props);

    // define resources here...
  }
}

// for development, use account/region from cdk cli
const devEnv = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

const app = new App();

new Middleware(app, 'stable-diffusion-extensions-dev', { env: devEnv });
// new MyStack(app, 'stable-diffusion-extensions-prod', { env: prodEnv });

app.synth();