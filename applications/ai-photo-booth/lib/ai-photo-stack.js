"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AiPhotoStack = void 0;
const aws_cdk_lib_1 = require("aws-cdk-lib");
const aws_cloudfront_1 = require("aws-cdk-lib/aws-cloudfront");
const aws_cloudfront_origins_1 = require("aws-cdk-lib/aws-cloudfront-origins");
const aws_iam_1 = require("aws-cdk-lib/aws-iam");
const aws_s3_1 = require("aws-cdk-lib/aws-s3");
const aws_s3_deployment_1 = require("aws-cdk-lib/aws-s3-deployment");
const path = require("path");
const fs = require("fs");
class AiPhotoStack extends aws_cdk_lib_1.Stack {
    constructor(scope, id, props) {
        super(scope, id, props);
        // Content bucket
        const siteBucket = new aws_s3_1.Bucket(this, 'SiteBucket', {
            // bucketName: 'ai-photo-studio',
            publicReadAccess: false,
            blockPublicAccess: aws_s3_1.BlockPublicAccess.BLOCK_ALL,
            /**
             * The default removal policy is RETAIN, which means that cdk destroy will not attempt to delete
             * the new bucket, and it will remain in your account until manually deleted. By setting the policy to
             * DESTROY, cdk destroy will attempt to delete the bucket, but will error if the bucket is not empty.
             */
            removalPolicy: aws_cdk_lib_1.RemovalPolicy.DESTROY,
            /**
             * For sample purposes only, if you create an S3 bucket then populate it, stack destruction fails.  This
             * setting will enable full cleanup of the demo.
             */
            autoDeleteObjects: true // NOT recommended for production code
        });
        new aws_cdk_lib_1.CfnOutput(this, 'bucketName', { value: siteBucket.bucketName });
        new aws_cdk_lib_1.CfnOutput(this, 'bucketURL', { value: siteBucket.bucketWebsiteUrl });
        // Grant access to CloudFront
        const cloudfrontOAI = new aws_cloudfront_1.OriginAccessIdentity(this, 'CloudFront-OAI', {
            comment: `OriginAccessIdentity (OAI) for ${id}`
        });
        siteBucket.addToResourcePolicy(new aws_iam_1.PolicyStatement({
            actions: ['s3:GetObject'],
            resources: [siteBucket.arnForObjects('*')],
            principals: [new aws_iam_1.CanonicalUserPrincipal(cloudfrontOAI.cloudFrontOriginAccessIdentityS3CanonicalUserId)]
        }));
        // CloudFront distribution
        const distribution = new aws_cloudfront_1.Distribution(this, 'SiteDistribution', {
            defaultRootObject: 'index.html',
            defaultBehavior: {
                origin: new aws_cloudfront_origins_1.S3Origin(siteBucket, { originAccessIdentity: cloudfrontOAI }),
                compress: true,
                allowedMethods: aws_cloudfront_1.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                viewerProtocolPolicy: aws_cloudfront_1.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
            }
        });
        new aws_cdk_lib_1.CfnOutput(this, 'DistributionId', { value: distribution.distributionId });
        console.log('context value: ', this.node.tryGetContext('api'));
        try {
            fs.writeFileSync(path.resolve(__dirname, './config/site-config.js'), `API_ENDPOINT='${this.node.tryGetContext('api')}'`, { flag: 'w+' });
        }
        catch (err) {
            console.error(err);
        }
        // Deploy site contents to S3 bucket
        new aws_s3_deployment_1.BucketDeployment(this, 'DeployWithInvalidation', {
            sources: [
                aws_s3_deployment_1.Source.asset(path.resolve(__dirname, '../reactStaticWebsite/build')),
                aws_s3_deployment_1.Source.asset(path.resolve(__dirname, './config'))
            ],
            destinationBucket: siteBucket,
            distribution,
            distributionPaths: ['/*']
        });
    }
}
exports.AiPhotoStack = AiPhotoStack;
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiYWktcGhvdG8tc3RhY2suanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlcyI6WyJhaS1waG90by1zdGFjay50cyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiOzs7QUFBQSw2Q0FBMEU7QUFDMUUsK0RBQXNIO0FBQ3RILCtFQUE4RDtBQUM5RCxpREFBOEU7QUFDOUUsK0NBQStEO0FBQy9ELHFFQUF5RTtBQUV6RSw2QkFBNkI7QUFDN0IseUJBQXlCO0FBRXpCLE1BQWEsWUFBYSxTQUFRLG1CQUFLO0lBQ3JDLFlBQVksS0FBZ0IsRUFBRSxFQUFVLEVBQUUsS0FBa0I7UUFDMUQsS0FBSyxDQUFDLEtBQUssRUFBRSxFQUFFLEVBQUUsS0FBSyxDQUFDLENBQUM7UUFFeEIsaUJBQWlCO1FBQ2pCLE1BQU0sVUFBVSxHQUFHLElBQUksZUFBTSxDQUFDLElBQUksRUFBRSxZQUFZLEVBQUU7WUFDaEQsaUNBQWlDO1lBQ2pDLGdCQUFnQixFQUFFLEtBQUs7WUFDdkIsaUJBQWlCLEVBQUUsMEJBQWlCLENBQUMsU0FBUztZQUM5Qzs7OztlQUlHO1lBQ0gsYUFBYSxFQUFFLDJCQUFhLENBQUMsT0FBTztZQUNwQzs7O2VBR0c7WUFDSCxpQkFBaUIsRUFBRSxJQUFJLENBQUMsc0NBQXNDO1NBQy9ELENBQUMsQ0FBQztRQUNILElBQUksdUJBQVMsQ0FBQyxJQUFJLEVBQUUsWUFBWSxFQUFFLEVBQUUsS0FBSyxFQUFFLFVBQVUsQ0FBQyxVQUFVLEVBQUUsQ0FBQyxDQUFDO1FBQ3BFLElBQUksdUJBQVMsQ0FBQyxJQUFJLEVBQUUsV0FBVyxFQUFFLEVBQUUsS0FBSyxFQUFFLFVBQVUsQ0FBQyxnQkFBZ0IsRUFBRSxDQUFDLENBQUM7UUFFekUsNkJBQTZCO1FBQzdCLE1BQU0sYUFBYSxHQUFHLElBQUkscUNBQW9CLENBQUMsSUFBSSxFQUFFLGdCQUFnQixFQUFFO1lBQ3JFLE9BQU8sRUFBRSxrQ0FBa0MsRUFBRSxFQUFFO1NBQ2hELENBQUMsQ0FBQztRQUVILFVBQVUsQ0FBQyxtQkFBbUIsQ0FBQyxJQUFJLHlCQUFlLENBQUM7WUFDakQsT0FBTyxFQUFFLENBQUMsY0FBYyxDQUFDO1lBQ3pCLFNBQVMsRUFBRSxDQUFDLFVBQVUsQ0FBQyxhQUFhLENBQUMsR0FBRyxDQUFDLENBQUM7WUFDMUMsVUFBVSxFQUFFLENBQUMsSUFBSSxnQ0FBc0IsQ0FBQyxhQUFhLENBQUMsK0NBQStDLENBQUMsQ0FBQztTQUN4RyxDQUFDLENBQUMsQ0FBQztRQUVKLDBCQUEwQjtRQUMxQixNQUFNLFlBQVksR0FBRyxJQUFJLDZCQUFZLENBQUMsSUFBSSxFQUFFLGtCQUFrQixFQUFFO1lBQzlELGlCQUFpQixFQUFFLFlBQVk7WUFDL0IsZUFBZSxFQUFFO2dCQUNmLE1BQU0sRUFBRSxJQUFJLGlDQUFRLENBQUMsVUFBVSxFQUFFLEVBQUUsb0JBQW9CLEVBQUUsYUFBYSxFQUFFLENBQUM7Z0JBQ3pFLFFBQVEsRUFBRSxJQUFJO2dCQUNkLGNBQWMsRUFBRSwrQkFBYyxDQUFDLHNCQUFzQjtnQkFDckQsb0JBQW9CLEVBQUUscUNBQW9CLENBQUMsaUJBQWlCO2FBQzdEO1NBQ0YsQ0FBQyxDQUFDO1FBQ0gsSUFBSSx1QkFBUyxDQUFDLElBQUksRUFBRSxnQkFBZ0IsRUFBRSxFQUFFLEtBQUssRUFBRSxZQUFZLENBQUMsY0FBYyxFQUFFLENBQUMsQ0FBQztRQUU5RSxPQUFPLENBQUMsR0FBRyxDQUFDLGlCQUFpQixFQUFFLElBQUksQ0FBQyxJQUFJLENBQUMsYUFBYSxDQUFDLEtBQUssQ0FBQyxDQUFDLENBQUM7UUFDL0QsSUFBSTtZQUNGLEVBQUUsQ0FBQyxhQUFhLENBQ2QsSUFBSSxDQUFDLE9BQU8sQ0FBQyxTQUFTLEVBQUUseUJBQXlCLENBQUMsRUFDbEQsaUJBQWlCLElBQUksQ0FBQyxJQUFJLENBQUMsYUFBYSxDQUFDLEtBQUssQ0FBQyxHQUFHLEVBQ2xELEVBQUUsSUFBSSxFQUFFLElBQUksRUFBRSxDQUFDLENBQUM7U0FDbkI7UUFBQyxPQUFPLEdBQUcsRUFBRTtZQUNaLE9BQU8sQ0FBQyxLQUFLLENBQUMsR0FBRyxDQUFDLENBQUM7U0FDcEI7UUFFRCxvQ0FBb0M7UUFDcEMsSUFBSSxvQ0FBZ0IsQ0FBQyxJQUFJLEVBQUUsd0JBQXdCLEVBQUU7WUFDbkQsT0FBTyxFQUFFO2dCQUNQLDBCQUFNLENBQUMsS0FBSyxDQUFDLElBQUksQ0FBQyxPQUFPLENBQUMsU0FBUyxFQUFFLDZCQUE2QixDQUFDLENBQUM7Z0JBQ3BFLDBCQUFNLENBQUMsS0FBSyxDQUFDLElBQUksQ0FBQyxPQUFPLENBQUMsU0FBUyxFQUFFLFVBQVUsQ0FBQyxDQUFDO2FBQ2xEO1lBQ0QsaUJBQWlCLEVBQUUsVUFBVTtZQUM3QixZQUFZO1lBQ1osaUJBQWlCLEVBQUUsQ0FBQyxJQUFJLENBQUM7U0FDMUIsQ0FBQyxDQUFDO0lBQ0wsQ0FBQztDQUNGO0FBcEVELG9DQW9FQyIsInNvdXJjZXNDb250ZW50IjpbImltcG9ydCB7IENmbk91dHB1dCwgUmVtb3ZhbFBvbGljeSwgU3RhY2ssIFN0YWNrUHJvcHMgfSBmcm9tICdhd3MtY2RrLWxpYic7XG5pbXBvcnQgeyBBbGxvd2VkTWV0aG9kcywgRGlzdHJpYnV0aW9uLCBPcmlnaW5BY2Nlc3NJZGVudGl0eSwgVmlld2VyUHJvdG9jb2xQb2xpY3kgfSBmcm9tICdhd3MtY2RrLWxpYi9hd3MtY2xvdWRmcm9udCc7XG5pbXBvcnQgeyBTM09yaWdpbiB9IGZyb20gJ2F3cy1jZGstbGliL2F3cy1jbG91ZGZyb250LW9yaWdpbnMnO1xuaW1wb3J0IHsgQ2Fub25pY2FsVXNlclByaW5jaXBhbCwgUG9saWN5U3RhdGVtZW50IH0gZnJvbSAnYXdzLWNkay1saWIvYXdzLWlhbSc7XG5pbXBvcnQgeyBCbG9ja1B1YmxpY0FjY2VzcywgQnVja2V0IH0gZnJvbSAnYXdzLWNkay1saWIvYXdzLXMzJztcbmltcG9ydCB7IEJ1Y2tldERlcGxveW1lbnQsIFNvdXJjZSB9IGZyb20gJ2F3cy1jZGstbGliL2F3cy1zMy1kZXBsb3ltZW50JztcbmltcG9ydCB7IENvbnN0cnVjdCB9IGZyb20gJ2NvbnN0cnVjdHMnO1xuaW1wb3J0ICogYXMgcGF0aCBmcm9tICdwYXRoJztcbmltcG9ydCAqIGFzIGZzIGZyb20gJ2ZzJztcblxuZXhwb3J0IGNsYXNzIEFpUGhvdG9TdGFjayBleHRlbmRzIFN0YWNrIHtcbiAgY29uc3RydWN0b3Ioc2NvcGU6IENvbnN0cnVjdCwgaWQ6IHN0cmluZywgcHJvcHM/OiBTdGFja1Byb3BzKSB7XG4gICAgc3VwZXIoc2NvcGUsIGlkLCBwcm9wcyk7XG5cbiAgICAvLyBDb250ZW50IGJ1Y2tldFxuICAgIGNvbnN0IHNpdGVCdWNrZXQgPSBuZXcgQnVja2V0KHRoaXMsICdTaXRlQnVja2V0Jywge1xuICAgICAgLy8gYnVja2V0TmFtZTogJ2FpLXBob3RvLXN0dWRpbycsXG4gICAgICBwdWJsaWNSZWFkQWNjZXNzOiBmYWxzZSxcbiAgICAgIGJsb2NrUHVibGljQWNjZXNzOiBCbG9ja1B1YmxpY0FjY2Vzcy5CTE9DS19BTEwsXG4gICAgICAvKipcbiAgICAgICAqIFRoZSBkZWZhdWx0IHJlbW92YWwgcG9saWN5IGlzIFJFVEFJTiwgd2hpY2ggbWVhbnMgdGhhdCBjZGsgZGVzdHJveSB3aWxsIG5vdCBhdHRlbXB0IHRvIGRlbGV0ZVxuICAgICAgICogdGhlIG5ldyBidWNrZXQsIGFuZCBpdCB3aWxsIHJlbWFpbiBpbiB5b3VyIGFjY291bnQgdW50aWwgbWFudWFsbHkgZGVsZXRlZC4gQnkgc2V0dGluZyB0aGUgcG9saWN5IHRvXG4gICAgICAgKiBERVNUUk9ZLCBjZGsgZGVzdHJveSB3aWxsIGF0dGVtcHQgdG8gZGVsZXRlIHRoZSBidWNrZXQsIGJ1dCB3aWxsIGVycm9yIGlmIHRoZSBidWNrZXQgaXMgbm90IGVtcHR5LlxuICAgICAgICovXG4gICAgICByZW1vdmFsUG9saWN5OiBSZW1vdmFsUG9saWN5LkRFU1RST1ksIC8vIE5PVCByZWNvbW1lbmRlZCBmb3IgcHJvZHVjdGlvbiBjb2RlXG4gICAgICAvKipcbiAgICAgICAqIEZvciBzYW1wbGUgcHVycG9zZXMgb25seSwgaWYgeW91IGNyZWF0ZSBhbiBTMyBidWNrZXQgdGhlbiBwb3B1bGF0ZSBpdCwgc3RhY2sgZGVzdHJ1Y3Rpb24gZmFpbHMuICBUaGlzXG4gICAgICAgKiBzZXR0aW5nIHdpbGwgZW5hYmxlIGZ1bGwgY2xlYW51cCBvZiB0aGUgZGVtby5cbiAgICAgICAqL1xuICAgICAgYXV0b0RlbGV0ZU9iamVjdHM6IHRydWUgLy8gTk9UIHJlY29tbWVuZGVkIGZvciBwcm9kdWN0aW9uIGNvZGVcbiAgICB9KTtcbiAgICBuZXcgQ2ZuT3V0cHV0KHRoaXMsICdidWNrZXROYW1lJywgeyB2YWx1ZTogc2l0ZUJ1Y2tldC5idWNrZXROYW1lIH0pO1xuICAgIG5ldyBDZm5PdXRwdXQodGhpcywgJ2J1Y2tldFVSTCcsIHsgdmFsdWU6IHNpdGVCdWNrZXQuYnVja2V0V2Vic2l0ZVVybCB9KTtcblxuICAgIC8vIEdyYW50IGFjY2VzcyB0byBDbG91ZEZyb250XG4gICAgY29uc3QgY2xvdWRmcm9udE9BSSA9IG5ldyBPcmlnaW5BY2Nlc3NJZGVudGl0eSh0aGlzLCAnQ2xvdWRGcm9udC1PQUknLCB7XG4gICAgICBjb21tZW50OiBgT3JpZ2luQWNjZXNzSWRlbnRpdHkgKE9BSSkgZm9yICR7aWR9YFxuICAgIH0pO1xuXG4gICAgc2l0ZUJ1Y2tldC5hZGRUb1Jlc291cmNlUG9saWN5KG5ldyBQb2xpY3lTdGF0ZW1lbnQoe1xuICAgICAgYWN0aW9uczogWydzMzpHZXRPYmplY3QnXSxcbiAgICAgIHJlc291cmNlczogW3NpdGVCdWNrZXQuYXJuRm9yT2JqZWN0cygnKicpXSxcbiAgICAgIHByaW5jaXBhbHM6IFtuZXcgQ2Fub25pY2FsVXNlclByaW5jaXBhbChjbG91ZGZyb250T0FJLmNsb3VkRnJvbnRPcmlnaW5BY2Nlc3NJZGVudGl0eVMzQ2Fub25pY2FsVXNlcklkKV1cbiAgICB9KSk7XG5cbiAgICAvLyBDbG91ZEZyb250IGRpc3RyaWJ1dGlvblxuICAgIGNvbnN0IGRpc3RyaWJ1dGlvbiA9IG5ldyBEaXN0cmlidXRpb24odGhpcywgJ1NpdGVEaXN0cmlidXRpb24nLCB7XG4gICAgICBkZWZhdWx0Um9vdE9iamVjdDogJ2luZGV4Lmh0bWwnLFxuICAgICAgZGVmYXVsdEJlaGF2aW9yOiB7XG4gICAgICAgIG9yaWdpbjogbmV3IFMzT3JpZ2luKHNpdGVCdWNrZXQsIHsgb3JpZ2luQWNjZXNzSWRlbnRpdHk6IGNsb3VkZnJvbnRPQUkgfSksXG4gICAgICAgIGNvbXByZXNzOiB0cnVlLFxuICAgICAgICBhbGxvd2VkTWV0aG9kczogQWxsb3dlZE1ldGhvZHMuQUxMT1dfR0VUX0hFQURfT1BUSU9OUyxcbiAgICAgICAgdmlld2VyUHJvdG9jb2xQb2xpY3k6IFZpZXdlclByb3RvY29sUG9saWN5LlJFRElSRUNUX1RPX0hUVFBTXG4gICAgICB9XG4gICAgfSk7XG4gICAgbmV3IENmbk91dHB1dCh0aGlzLCAnRGlzdHJpYnV0aW9uSWQnLCB7IHZhbHVlOiBkaXN0cmlidXRpb24uZGlzdHJpYnV0aW9uSWQgfSk7XG5cbiAgICBjb25zb2xlLmxvZygnY29udGV4dCB2YWx1ZTogJywgdGhpcy5ub2RlLnRyeUdldENvbnRleHQoJ2FwaScpKTtcbiAgICB0cnkge1xuICAgICAgZnMud3JpdGVGaWxlU3luYyhcbiAgICAgICAgcGF0aC5yZXNvbHZlKF9fZGlybmFtZSwgJy4vY29uZmlnL3NpdGUtY29uZmlnLmpzJyksXG4gICAgICAgIGBBUElfRU5EUE9JTlQ9JyR7dGhpcy5ub2RlLnRyeUdldENvbnRleHQoJ2FwaScpfSdgLFxuICAgICAgICB7IGZsYWc6ICd3KycgfSk7XG4gICAgfSBjYXRjaCAoZXJyKSB7XG4gICAgICBjb25zb2xlLmVycm9yKGVycik7XG4gICAgfVxuXG4gICAgLy8gRGVwbG95IHNpdGUgY29udGVudHMgdG8gUzMgYnVja2V0XG4gICAgbmV3IEJ1Y2tldERlcGxveW1lbnQodGhpcywgJ0RlcGxveVdpdGhJbnZhbGlkYXRpb24nLCB7XG4gICAgICBzb3VyY2VzOiBbXG4gICAgICAgIFNvdXJjZS5hc3NldChwYXRoLnJlc29sdmUoX19kaXJuYW1lLCAnLi4vcmVhY3RTdGF0aWNXZWJzaXRlL2J1aWxkJykpLFxuICAgICAgICBTb3VyY2UuYXNzZXQocGF0aC5yZXNvbHZlKF9fZGlybmFtZSwgJy4vY29uZmlnJykpXG4gICAgICBdLFxuICAgICAgZGVzdGluYXRpb25CdWNrZXQ6IHNpdGVCdWNrZXQsXG4gICAgICBkaXN0cmlidXRpb24sXG4gICAgICBkaXN0cmlidXRpb25QYXRoczogWycvKiddXG4gICAgfSk7XG4gIH1cbn1cbiJdfQ==