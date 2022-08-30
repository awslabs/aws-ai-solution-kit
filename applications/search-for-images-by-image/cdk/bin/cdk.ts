#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { CdkStack } from '../lib/cdk-stack';
import { BootstraplessStackSynthesizer, CompositeECRRepositoryAspect } from 'cdk-bootstrapless-synthesizer';

const app = new cdk.App();
new CdkStack(app, 'AI-Solution-Kit-workshop', {
  synthesizer: synthesizer()
  /* If you don't specify 'env', this stack will be environment-agnostic.
   * Account/Region-dependent features and context lookups will not work,
   * but a single synthesized template can be deployed anywhere. */

  /* Uncomment the next line to specialize this stack for the AWS Account
   * and Region that are implied by the current CLI configuration. */
  // env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },

  /* Uncomment the next line if you know exactly what Account and Region you
   * want to deploy the stack to. */
  // env: { account: '123456789012', region: 'us-east-1' },

  /* For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html */
});

new CdkStack(app, 'AI-Solution-Kit-workshop-3G', {
  lambdaMemorySize: 3008,
  synthesizer: synthesizer()
});

function synthesizer() {
  return process.env.USE_BSS ? new BootstraplessStackSynthesizer() : undefined;
}