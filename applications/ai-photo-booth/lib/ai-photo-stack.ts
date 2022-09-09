import { CfnOutput, RemovalPolicy, Stack, StackProps } from 'aws-cdk-lib';
import { AllowedMethods, Distribution, OriginAccessIdentity, ViewerProtocolPolicy } from 'aws-cdk-lib/aws-cloudfront';
import { S3Origin } from 'aws-cdk-lib/aws-cloudfront-origins';
import { CanonicalUserPrincipal, PolicyStatement } from 'aws-cdk-lib/aws-iam';
import { BlockPublicAccess, Bucket } from 'aws-cdk-lib/aws-s3';
import { BucketDeployment, Source } from 'aws-cdk-lib/aws-s3-deployment';
import { Construct } from 'constructs';
import * as path from 'path';
import * as fs from 'fs';

export class AiPhotoStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // Content bucket
    const siteBucket = new Bucket(this, 'SiteBucket', {
      // bucketName: 'ai-photo-studio',
      publicReadAccess: false,
      blockPublicAccess: BlockPublicAccess.BLOCK_ALL,
      /**
       * The default removal policy is RETAIN, which means that cdk destroy will not attempt to delete
       * the new bucket, and it will remain in your account until manually deleted. By setting the policy to
       * DESTROY, cdk destroy will attempt to delete the bucket, but will error if the bucket is not empty.
       */
      removalPolicy: RemovalPolicy.DESTROY, // NOT recommended for production code
      /**
       * For sample purposes only, if you create an S3 bucket then populate it, stack destruction fails.  This
       * setting will enable full cleanup of the demo.
       */
      autoDeleteObjects: true // NOT recommended for production code
    });
    new CfnOutput(this, 'bucketName', { value: siteBucket.bucketName });
    new CfnOutput(this, 'bucketURL', { value: siteBucket.bucketWebsiteUrl });

    // Grant access to CloudFront
    const cloudfrontOAI = new OriginAccessIdentity(this, 'CloudFront-OAI', {
      comment: `OriginAccessIdentity (OAI) for ${id}`
    });

    siteBucket.addToResourcePolicy(new PolicyStatement({
      actions: ['s3:GetObject'],
      resources: [siteBucket.arnForObjects('*')],
      principals: [new CanonicalUserPrincipal(cloudfrontOAI.cloudFrontOriginAccessIdentityS3CanonicalUserId)]
    }));

    // CloudFront distribution
    const distribution = new Distribution(this, 'SiteDistribution', {
      defaultRootObject: 'index.html',
      defaultBehavior: {
        origin: new S3Origin(siteBucket, { originAccessIdentity: cloudfrontOAI }),
        compress: true,
        allowedMethods: AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
        viewerProtocolPolicy: ViewerProtocolPolicy.REDIRECT_TO_HTTPS
      }
    });
    new CfnOutput(this, 'DistributionId', { value: distribution.distributionId });

    console.log('context value: ', this.node.tryGetContext('api'));
    try {
      fs.writeFileSync(
        path.resolve(__dirname, './config/site-config.js'),
        `API_ENDPOINT='${this.node.tryGetContext('api')}'`,
        { flag: 'w+' });
    } catch (err) {
      console.error(err);
    }

    // Deploy site contents to S3 bucket
    new BucketDeployment(this, 'DeployWithInvalidation', {
      sources: [
        Source.asset(path.resolve(__dirname, '../reactStaticWebsite/build')),
        Source.asset(path.resolve(__dirname, './config'))
      ],
      destinationBucket: siteBucket,
      distribution,
      distributionPaths: ['/*']
    });
  }
}
