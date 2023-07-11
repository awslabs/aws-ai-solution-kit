const { awscdk, typescript } = require('projen');
const apiDocDeps = [
  'express@^4.17.3',
  'serverless-http@^2.6.1',
  'swagger-ui-express@^4.3.0',
  'yamljs@^0.3.0',
  'deasync@^0.1.26',
  'aws-sdk@^2.1001.0',
];

const project = new awscdk.AwsCdkTypeScriptApp({
  cdkVersion: '2.87.0',
  minNodeVersion: '18.0.0',
  name: 'ai-solution-kit',
  license: 'Apache-2.0',
  licensed: true,
  // appEntrypoint: 'containers.ts',
  appEntrypoint: 'main.ts',
  defaultReleaseBranch: 'v1.4.0',
  buildWorkflow: true,
  buildWorkflowTriggers: { pullRequest: {}, push: {} },
  mutableBuild: true,
  githubOptions: {
    mergify: false,
  },
  autoApproveUpgrades: false,
  eslint: true,
  defaultReleaseBranch: 'main',
  deps: [
    'aws-cdk-lib',
    'constructs',
    'source-map-support',
    'cdk-bootstrapless-synthesizer@^2.1.1',
    ...apiDocDeps,
  ], /* Runtime dependencies of this module. */
  tsconfig: {
    compilerOptions: {
      noUnusedLocals: false,
    },
  },
  context: {
    ecrRegistry: 'public.ecr.aws/aws-gcr-solutions/aws-gcr-ai-solution-kit',
  },
  description: 'AWS AI Solution Kit CDK project',
  devDeps: [
    // '@aws-cdk/assertions',
  ], /* Build dependencies for this module. */
  gitignore: [
    'src/api-images',
    'deployment/global-s3-assets/',
    'deployment/regional-s3-assets/',
  ],
  pullRequestTemplate: true,
  pullRequestTemplateContents: [
    '## Description',
    '',
    'Please include a summary of the changes and the related issue. Please also include relevant motivation and context. List any dependencies that are required for this change.',
    '',
    'Fixes # (issue)',
    '',
    '## Type of change',
    '',
    'Please delete options that are not relevant.',
    '',
    '- [ ] Bug fix (non-breaking change which fixes an issue)',
    '- [ ] New feature (non-breaking change which adds functionality)',
    '- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)',
    '- [ ] This change requires a documentation update',
  ],
  watchExcludes: [
    'README.md',
    'cdk*.json',
    '**/*.d.ts',
    '**/*.js',
    'tsconfig.json',
    'package*.json',
    'yarn.lock',
    'node_modules',
  ],
});

project.addTask('post-compile-containers', {
  name: 'post-compile-containers',
  description: 'Runs after successful compilation for containers',
  steps: [
    {
      exec: 'cdk synth -q -c build-container=true',
    },
  ],
});

project.addTask('build-containers', {
  name: 'Build containers',
  description: 'Build containers with src/containers/lambda-containers-stack.ts for AI API models',
  steps: [
    {
      spawn: 'default',
    },
    {
      spawn: 'pre-compile',
    },
    {
      spawn: 'compile',
    },
    {
      spawn: 'post-compile-containers',
    },
    {
      spawn: 'test',
    },
    {
      spawn: 'package',
    },
  ],
});

project.addTask('deploy-containers', {
  name: 'Deploy containers',
  description: 'Deploy containers to AWS ECR with src/containers/lambda-containers-stack.ts for AI API models',
  steps: [
    {
      exec: 'cdk deploy -c deploy-container=true',
    },
  ],
});

project.addFields({
  version: '1.2.0',
});

project.synth();