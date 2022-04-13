"use strict";
var _a, _b, _c;
Object.defineProperty(exports, "__esModule", { value: true });
exports.ECRDeployment = exports.S3ArchiveName = exports.DockerImageName = void 0;
const JSII_RTTI_SYMBOL_1 = Symbol.for("jsii.rtti");
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
const child_process = require("child_process");
const path = require("path");
const iam = require("@aws-cdk/aws-iam");
const lambda = require("@aws-cdk/aws-lambda");
const cdk = require("@aws-cdk/core");
// eslint-disable-next-line no-duplicate-imports, import/order
const core_1 = require("@aws-cdk/core");
function getCode() {
    // if (!(process.env.CI || process.env.NO_PREBUILT_LAMBDA)) {
    //     try {
    //         console.log('Try to get prebuilt lambda');
    //         const installScript = path.join(__dirname, '../lambda/install.js');
    //         const prebuiltPath = path.join(__dirname, '../lambda/out');
    //         child_process.execSync(`${process.argv0} ${installScript} ${prebuiltPath}`);
    //         return lambda.Code.fromAsset(prebuiltPath);
    //     }
    //     catch (err) {
    //         console.warn(`Can not get prebuilt lambda: ${err}`);
    //     }
    // }
    console.log('Build lambda from scratch');
    return lambda.Code.fromDockerBuild(path.join(__dirname, '../lambda'));
}
/**
 * @stability stable
 */
class DockerImageName {
    /**
     * @stability stable
     */
    constructor(name, creds) {
        this.name = name;
        this.creds = creds;
    }
    /**
     * The uri of the docker image.
     *
     * The uri spec follows https://github.com/containers/skopeo
     *
     * @stability stable
     */
    get uri() { return `docker://${this.name}`; }
}
exports.DockerImageName = DockerImageName;
_a = JSII_RTTI_SYMBOL_1;
DockerImageName[_a] = { fqn: "cdk-ecr-deployment.DockerImageName", version: "1.0.2" };
/**
 * @stability stable
 */
class S3ArchiveName {
    /**
     * @stability stable
     */
    constructor(p, ref, creds) {
        this.creds = creds;
        this.name = p;
        if (ref) {
            this.name += ':' + ref;
        }
    }
    /**
     * The uri of the docker image.
     *
     * The uri spec follows https://github.com/containers/skopeo
     *
     * @stability stable
     */
    get uri() { return `s3://${this.name}`; }
}
exports.S3ArchiveName = S3ArchiveName;
_b = JSII_RTTI_SYMBOL_1;
S3ArchiveName[_b] = { fqn: "cdk-ecr-deployment.S3ArchiveName", version: "1.0.2" };
/**
 * @stability stable
 */
class ECRDeployment extends core_1.Construct {
    /**
     * @stability stable
     */
    constructor(scope, id, props) {
        var _d;
        super(scope, id);
        const memoryLimit = (_d = props.memoryLimit) !== null && _d !== void 0 ? _d : 512;
        this.handler = new lambda.SingletonFunction(this, 'CustomResourceHandler', {
            uuid: this.renderSingletonUuid(memoryLimit),
            code: getCode(),
            runtime: lambda.Runtime.GO_1_X,
            handler: 'main',
            environment: props.environment,
            lambdaPurpose: 'Custom::CDKECRDeployment',
            timeout: cdk.Duration.minutes(15),
            role: props.role,
            memorySize: memoryLimit,
            vpc: props.vpc,
            vpcSubnets: props.vpcSubnets,
        });

        const handlerRole = this.handler.role;
        if (!handlerRole) {
            throw new Error('lambda.SingletonFunction should have created a Role');
        }
        handlerRole.addToPrincipalPolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
                'ecr:GetAuthorizationToken',
                'ecr:BatchCheckLayerAvailability',
                'ecr:GetDownloadUrlForLayer',
                'ecr:GetRepositoryPolicy',
                'ecr:DescribeRepositories',
                'ecr:ListImages',
                'ecr:DescribeImages',
                'ecr:BatchGetImage',
                'ecr:ListTagsForResource',
                'ecr:DescribeImageScanFindings',
                'ecr:InitiateLayerUpload',
                'ecr:UploadLayerPart',
                'ecr:CompleteLayerUpload',
                'ecr:PutImage',
                'ecr:DeleteRepository',
                'ecr:BatchDeleteImage',
            ],
            resources: ['*'],
        }));
        handlerRole.addToPrincipalPolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
                's3:GetObject',
            ],
            resources: ['*'],
        }));
        // new cdk.CustomResource(this, 'CustomResource', {
        //     serviceToken: this.handler.functionArn,
        //     resourceType: 'Custom::CDKBucketDeployment',
        //     properties: {
        //         SrcImage: props.src.uri,
        //         SrcCreds: props.src.creds,
        //         DestImage: props.dest.uri,
        //         DestCreds: props.dest.creds,
        //     },
        // });
    };
    /**
     * @stability stable
     */
    get serviceToken() {
        return this.handler.functionArn;
    }

    renderSingletonUuid(memoryLimit) {
        let uuid = 'bd07c930-edb9-4112-a20f-03f096f53666';
        // if user specify a custom memory limit, define another singleton handler
        // with this configuration. otherwise, it won't be possible to use multiple
        // configurations since we have a singleton.
        // if (memoryLimit) {
        //     if (cdk.Token.isUnresolved(memoryLimit)) {
        //         throw new Error('Can\'t use tokens when specifying "memoryLimit" since we use it to identify the singleton custom resource handler');
        //     }
        //     uuid += `-${memoryLimit.toString()}MiB`;
        // }
        return uuid;
    }
}
exports.ECRDeployment = ECRDeployment;
_c = JSII_RTTI_SYMBOL_1;
ECRDeployment[_c] = { fqn: "cdk-ecr-deployment.ECRDeployment", version: "1.0.2" };
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiaW5kZXguanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlcyI6WyIuLi9zcmMvaW5kZXgudHMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6Ijs7Ozs7QUFBQSxxRUFBcUU7QUFDckUsc0NBQXNDO0FBR3RDLCtDQUErQztBQUMvQyw2QkFBNkI7QUFFN0Isd0NBQXdDO0FBQ3hDLDhDQUE4QztBQUM5QyxxQ0FBcUM7QUFHckMsOERBQThEO0FBQzlELHdDQUEyRDtBQWlDM0QsU0FBUyxPQUFPO0lBQ2QsSUFBSSxDQUFDLENBQUMsT0FBTyxDQUFDLEdBQUcsQ0FBQyxFQUFFLElBQUksT0FBTyxDQUFDLEdBQUcsQ0FBQyxrQkFBa0IsQ0FBQyxFQUFFO1FBQ3ZELElBQUk7WUFDRixPQUFPLENBQUMsR0FBRyxDQUFDLDRCQUE0QixDQUFDLENBQUM7WUFFMUMsTUFBTSxhQUFhLEdBQUcsSUFBSSxDQUFDLElBQUksQ0FBQyxTQUFTLEVBQUUsc0JBQXNCLENBQUMsQ0FBQztZQUNuRSxNQUFNLFlBQVksR0FBRyxJQUFJLENBQUMsSUFBSSxDQUFDLFNBQVMsRUFBRSxlQUFlLENBQUMsQ0FBQztZQUMzRCxhQUFhLENBQUMsUUFBUSxDQUFDLEdBQUcsT0FBTyxDQUFDLEtBQUssSUFBSSxhQUFhLElBQUksWUFBWSxFQUFFLENBQUMsQ0FBQztZQUU1RSxPQUFPLE1BQU0sQ0FBQyxJQUFJLENBQUMsU0FBUyxDQUFDLFlBQVksQ0FBQyxDQUFDO1NBQzVDO1FBQUMsT0FBTyxHQUFHLEVBQUU7WUFDWixPQUFPLENBQUMsSUFBSSxDQUFDLGdDQUFnQyxHQUFHLEVBQUUsQ0FBQyxDQUFDO1NBQ3JEO0tBQ0Y7SUFFRCxPQUFPLENBQUMsR0FBRyxDQUFDLDJCQUEyQixDQUFDLENBQUM7SUFFekMsT0FBTyxNQUFNLENBQUMsSUFBSSxDQUFDLGVBQWUsQ0FBQyxJQUFJLENBQUMsSUFBSSxDQUFDLFNBQVMsRUFBRSxXQUFXLENBQUMsQ0FBQyxDQUFDO0FBQ3hFLENBQUM7Ozs7QUFFRCxNQUFhLGVBQWU7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V0FBVztZQUNqQyxZQUFZLEVBQUUsNkJBQTZCO1lBQzNDLFVBQVUsRUFBRTtnQkFDVixRQUFRLEVBQUUsS0FBSyxDQUFDLEdBQUcsQ0FBQyxHQUFHO2dCQUN2QixRQUFRLEVBQUUsS0FBSyxDQUFDLEdBQUcsQ0FBQyxLQUFLO2dCQUN6QixTQUFTLEVBQUUsS0FBSyxDQUFDLElBQUksQ0FBQyxHQUFHO2dCQUN6QixTQUFTLEVBQUUsS0FBSyxDQUFDLElBQUksQ0FBQyxLQUFLO2FBQzVCO1NBQ0YsQ0FBQyxDQUFDO0lBQ0wsQ0FBQztJQUVPLG1CQUFtQixDQUFDLFdBQW9CO1FBQzlDLElBQUksSUFBSSxHQUFHLHNDQUFzQyxDQUFDO1FBRWxELDBFQUEwRTtRQUMxRSwyRUFBMkU7UUFDM0UsNENBQTRDO1FBQzVDLElBQUksV0FBVyxFQUFFO1lBQ2YsSUFBSSxHQUFHLENBQUMsS0FBSyxDQUFDLFlBQVksQ0FBQyxXQUFXLENBQUMsRUFBRTtnQkFDdkMsTUFBTSxJQUFJLEtBQUssQ0FBQyxtSEFBbUgsQ0FBQyxDQUFDO2FBQ3RJO1lBRUQsSUFBSSxJQUFJLElBQUksV0FBVyxDQUFDLFFBQVEsRUFBRSxLQUFLLENBQUM7U0FDekM7UUFFRCxPQUFPLElBQUksQ0FBQztJQUNkLENBQUM7O0FBN0VILHNDQThFQyIsInNvdXJjZXNDb250ZW50IjpbIi8vIENvcHlyaWdodCBBbWF6b24uY29tLCBJbmMuIG9yIGl0cyBhZmZpbGlhdGVzLiBBbGwgUmlnaHRzIFJlc2VydmVkLlxuLy8gU1BEWC1MaWNlbnNlLUlkZW50aWZpZXI6IEFwYWNoZS0yLjBcblxuXG5pbXBvcnQgKiBhcyBjaGlsZF9wcm9jZXNzIGZyb20gJ2NoaWxkX3Byb2Nlc3MnO1xuaW1wb3J0ICogYXMgcGF0aCBmcm9tICdwYXRoJztcbmltcG9ydCAqIGFzIGVjMiBmcm9tICdAYXdzLWNkay9hd3MtZWMyJztcbmltcG9ydCAqIGFzIGlhbSBmcm9tICdAYXdzLWNkay9hd3MtaWFtJztcbmltcG9ydCAqIGFzIGxhbWJkYSBmcm9tICdAYXdzLWNkay9hd3MtbGFtYmRhJztcbmltcG9ydCAqIGFzIGNkayBmcm9tICdAYXdzLWNkay9jb3JlJztcbmltcG9ydCB7IENvbnN0cnVjdCB9IGZyb20gJ2NvbnN0cnVjdHMnO1xuXG4vLyBlc2xpbnQtZGlzYWJsZS1uZXh0LWxpbmUgbm8tZHVwbGljYXRlLWltcG9ydHMsIGltcG9ydC9vcmRlclxuaW1wb3J0IHsgQ29uc3RydWN0IGFzIENvcmVDb25zdHJ1Y3QgfSBmcm9tICdAYXdzLWNkay9jb3JlJztcblxuZXhwb3J0IGludGVyZmFjZSBFQ1JEZXBsb3ltZW50UHJvcHMge1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgXG4gIHJlYWRvbmx5IHNyYzogSUltYWdlTmFtZTtcblxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcbiAgcmVhZG9ubHkgZGVzdDogSUltYWdlTmFtZTtcblxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcbiAgcmVhZG9ubHkgbWVtb3J5TGltaXQ/OiBudW1iZXI7XG5cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIFxuICByZWFkb25seSByb2xlPzogaWFtLklSb2xlO1xuXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcbiAgcmVhZG9ubHkgdnBjPzogZWMyLklWcGM7XG5cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgXG4gIHJlYWRvbmx5IHZwY1N1Ym5ldHM/OiBlYzIuU3VibmV0U2VsZWN0aW9uO1xuXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBcbiAgcmVhZG9ubHkgZW52aXJvbm1lbnQ/OiB7IFtrZXk6IHN0cmluZ106IHN0cmluZyB9O1xufVxuXG5leHBvcnQgaW50ZXJmYWNlIElJbWFnZU5hbWUge1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIFxuICByZWFkb25seSB1cmk6IHN0cmluZztcblxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgXG4gIGNyZWRzPzogc3RyaW5nO1xufVxuXG5mdW5jdGlvbiBnZXRDb2RlKCk6IGxhbWJkYS5Bc3NldENvZGUge1xuICBpZiAoIShwcm9jZXNzLmVudi5DSSB8fCBwcm9jZXNzLmVudi5OT19QUkVCVUlMVF9MQU1CREEpKSB7XG4gICAgdHJ5IHtcbiAgICAgIGNvbnNvbGUubG9nKCdUcnkgdG8gZ2V0IHByZWJ1aWx0IGxhbWJkYScpO1xuXG4gICAgICBjb25zdCBpbnN0YWxsU2NyaXB0ID0gcGF0aC5qb2luKF9fZGlybmFtZSwgJy4uL2xhbWJkYS9pbnN0YWxsLmpzJyk7XG4gICAgICBjb25zdCBwcmVidWlsdFBhdGggPSBwYXRoLmpvaW4oX19kaXJuYW1lLCAnLi4vbGFtYmRhL291dCcpO1xuICAgICAgY2hpbGRfcHJvY2Vzcy5leGVjU3luYyhgJHtwcm9jZXNzLmFyZ3YwfSAke2luc3RhbGxTY3JpcHR9ICR7cHJlYnVpbHRQYXRofWApO1xuXG4gICAgICByZXR1cm4gbGFtYmRhLkNvZGUuZnJvbUFzc2V0KHByZWJ1aWx0UGF0aCk7XG4gICAgfSBjYXRjaCAoZXJyKSB7XG4gICAgICBjb25zb2xlLndhcm4oYENhbiBub3QgZ2V0IHByZWJ1aWx0IGxhbWJkYTogJHtlcnJ9YCk7XG4gICAgfVxuICB9XG5cbiAgY29uc29sZS5sb2coJ0J1aWxkIGxhbWJkYSBmcm9tIHNjcmF0Y2gnKTtcblxuICByZXR1cm4gbGFtYmRhLkNvZGUuZnJvbURvY2tlckJ1aWxkKHBhdGguam9pbihfX2Rpcm5hbWUsICcuLi9sYW1iZGEnKSk7XG59XG5cbmV4cG9ydCBjbGFzcyBEb2NrZXJJbWFnZU5hbWUgaW1wbGVtZW50cyBJSW1hZ2VOYW1lIHtcbiAgcHVibGljIGNvbnN0cnVjdG9yKHByaXZhdGUgbmFtZTogc3RyaW5nLCBwdWJsaWMgY3JlZHM/OiBzdHJpbmcpIHsgfVxuICBwdWJsaWMgZ2V0IHVyaSgpOiBzdHJpbmcgeyByZXR1cm4gYGRvY2tlcjovLyR7dGhpcy5uYW1lfWA7IH1cbn1cblxuZXhwb3J0IGNsYXNzIFMzQXJjaGl2ZU5hbWUgaW1wbGVtZW50cyBJSW1hZ2VOYW1lIHtcbiAgcHJpdmF0ZSBuYW1lOiBzdHJpbmc7XG4gIHB1YmxpYyBjb25zdHJ1Y3RvcihwOiBzdHJpbmcsIHJlZj86IHN0cmluZywgcHVibGljIGNyZWRzPzogc3RyaW5nKSB7XG4gICAgdGhpcy5uYW1lID0gcDtcbiAgICBpZiAocmVmKSB7XG4gICAgICB0aGlzLm5hbWUgKz0gJzonICsgcmVmO1xuICAgIH1cbiAgfVxuICBwdWJsaWMgZ2V0IHVyaSgpOiBzdHJpbmcgeyByZXR1cm4gYHMzOi8vJHt0aGlzLm5hbWV9YDsgfVxufVxuXG5leHBvcnQgY2xhc3MgRUNSRGVwbG95bWVudCBleHRlbmRzIENvcmVDb25zdHJ1Y3Qge1xuICBjb25zdHJ1Y3RvcihzY29wZTogQ29uc3RydWN0LCBpZDogc3RyaW5nLCBwcm9wczogRUNSRGVwbG95bWVudFByb3BzKSB7XG4gICAgc3VwZXIoc2NvcGUsIGlkKTtcbiAgICBjb25zdCBtZW1vcnlMaW1pdCA9IHByb3BzLm1lbW9yeUxpbWl0ID8/IDUxMjtcbiAgICBjb25zdCBoYW5kbGVyID0gbmV3IGxhbWJkYS5TaW5nbGV0b25GdW5jdGlvbih0aGlzLCAnQ3VzdG9tUmVzb3VyY2VIYW5kbGVyJywge1xuICAgICAgdXVpZDogdGhpcy5yZW5kZXJTaW5nbGV0b25VdWlkKG1lbW9yeUxpbWl0KSxcbiAgICAgIGNvZGU6IGdldENvZGUoKSxcbiAgICAgIHJ1bnRpbWU6IGxhbWJkYS5SdW50aW1lLkdPXzFfWCxcbiAgICAgIGhhbmRsZXI6ICdtYWluJyxcbiAgICAgIGVudmlyb25tZW50OiBwcm9wcy5lbnZpcm9ubWVudCxcbiAgICAgIGxhbWJkYVB1cnBvc2U6ICdDdXN0b206OkNES0VDUkRlcGxveW1lbnQnLFxuICAgICAgdGltZW91dDogY2RrLkR1cmF0aW9uLm1pbnV0ZXMoMTUpLFxuICAgICAgcm9sZTogcHJvcHMucm9sZSxcbiAgICAgIG1lbW9yeVNpemU6IG1lbW9yeUxpbWl0LFxuICAgICAgdnBjOiBwcm9wcy52cGMsXG4gICAgICB2cGNTdWJuZXRzOiBwcm9wcy52cGNTdWJuZXRzLFxuICAgIH0pO1xuXG4gICAgY29uc3QgaGFuZGxlclJvbGUgPSBoYW5kbGVyLnJvbGU7XG4gICAgaWYgKCFoYW5kbGVyUm9sZSkgeyB0aHJvdyBuZXcgRXJyb3IoJ2xhbWJkYS5TaW5nbGV0b25GdW5jdGlvbiBzaG91bGQgaGF2ZSBjcmVhdGVkIGEgUm9sZScpOyB9XG5cbiAgICBoYW5kbGVyUm9sZS5hZGRUb1ByaW5jaXBhbFBvbGljeShcbiAgICAgIG5ldyBpYW0uUG9saWN5U3RhdGVtZW50KHtcbiAgICAgICAgZWZmZWN0OiBpYW0uRWZmZWN0LkFMTE9XLFxuICAgICAgICBhY3Rpb25zOiBbXG4gICAgICAgICAgJ2VjcjpHZXRBdXRob3JpemF0aW9uVG9rZW4nLFxuICAgICAgICAgICdlY3I6QmF0Y2hDaGVja0xheWVyQXZhaWxhYmlsaXR5JyxcbiAgICAgICAgICAnZWNyOkdldERvd25sb2FkVXJsRm9yTGF5ZXInLFxuICAgICAgICAgICdlY3I6R2V0UmVwb3NpdG9yeVBvbGljeScsXG4gICAgICAgICAgJ2VjcjpEZXNjcmliZVJlcG9zaXRvcmllcycsXG4gICAgICAgICAgJ2VjcjpMaXN0SW1hZ2VzJyxcbiAgICAgICAgICAnZWNyOkRlc2NyaWJlSW1hZ2VzJyxcbiAgICAgICAgICAnZWNyOkJhdGNoR2V0SW1hZ2UnLFxuICAgICAgICAgICdlY3I6TGlzdFRhZ3NGb3JSZXNvdXJjZScsXG4gICAgICAgICAgJ2VjcjpEZXNjcmliZUltYWdlU2NhbkZpbmRpbmdzJyxcbiAgICAgICAgICAnZWNyOkluaXRpYXRlTGF5ZXJVcGxvYWQnLFxuICAgICAgICAgICdlY3I6VXBsb2FkTGF5ZXJQYXJ0JyxcbiAgICAgICAgICAnZWNyOkNvbXBsZXRlTGF5ZXJVcGxvYWQnLFxuICAgICAgICAgICdlY3I6UHV0SW1hZ2UnLFxuICAgICAgICBdLFxuICAgICAgICByZXNvdXJjZXM6IFsnKiddLFxuICAgICAgfSkpO1xuICAgIGhhbmRsZXJSb2xlLmFkZFRvUHJpbmNpcGFsUG9saWN5KG5ldyBpYW0uUG9saWN5U3RhdGVtZW50KHtcbiAgICAgIGVmZmVjdDogaWFtLkVmZmVjdC5BTExPVyxcbiAgICAgIGFjdGlvbnM6IFtcbiAgICAgICAgJ3MzOkdldE9iamVjdCcsXG4gICAgICBdLFxuICAgICAgcmVzb3VyY2VzOiBbJyonXSxcbiAgICB9KSk7XG5cbiAgICBuZXcgY2RrLkN1c3RvbVJlc291cmNlKHRoaXMsICdDdXN0b21SZXNvdXJjZScsIHtcbiAgICAgIHNlcnZpY2VUb2tlbjogaGFuZGxlci5mdW5jdGlvbkFybixcbiAgICAgIHJlc291cmNlVHlwZTogJ0N1c3RvbTo6Q0RLQnVja2V0RGVwbG95bWVudCcsXG4gICAgICBwcm9wZXJ0aWVzOiB7XG4gICAgICAgIFNyY0ltYWdlOiBwcm9wcy5zcmMudXJpLFxuICAgICAgICBTcmNDcmVkczogcHJvcHMuc3JjLmNyZWRzLFxuICAgICAgICBEZXN0SW1hZ2U6IHByb3BzLmRlc3QudXJpLFxuICAgICAgICBEZXN0Q3JlZHM6IHByb3BzLmRlc3QuY3JlZHMsXG4gICAgICB9LFxuICAgIH0pO1xuICB9XG5cbiAgcHJpdmF0ZSByZW5kZXJTaW5nbGV0b25VdWlkKG1lbW9yeUxpbWl0PzogbnVtYmVyKSB7XG4gICAgbGV0IHV1aWQgPSAnYmQwN2M5MzAtZWRiOS00MTEyLWEyMGYtMDNmMDk2ZjUzNjY2JztcblxuICAgIC8vIGlmIHVzZXIgc3BlY2lmeSBhIGN1c3RvbSBtZW1vcnkgbGltaXQsIGRlZmluZSBhbm90aGVyIHNpbmdsZXRvbiBoYW5kbGVyXG4gICAgLy8gd2l0aCB0aGlzIGNvbmZpZ3VyYXRpb24uIG90aGVyd2lzZSwgaXQgd29uJ3QgYmUgcG9zc2libGUgdG8gdXNlIG11bHRpcGxlXG4gICAgLy8gY29uZmlndXJhdGlvbnMgc2luY2Ugd2UgaGF2ZSBhIHNpbmdsZXRvbi5cbiAgICBpZiAobWVtb3J5TGltaXQpIHtcbiAgICAgIGlmIChjZGsuVG9rZW4uaXNVbnJlc29sdmVkKG1lbW9yeUxpbWl0KSkge1xuICAgICAgICB0aHJvdyBuZXcgRXJyb3IoJ0NhblxcJ3QgdXNlIHRva2VucyB3aGVuIHNwZWNpZnlpbmcgXCJtZW1vcnlMaW1pdFwiIHNpbmNlIHdlIHVzZSBpdCB0byBpZGVudGlmeSB0aGUgc2luZ2xldG9uIGN1c3RvbSByZXNvdXJjZSBoYW5kbGVyJyk7XG4gICAgICB9XG5cbiAgICAgIHV1aWQgKz0gYC0ke21lbW9yeUxpbWl0LnRvU3RyaW5nKCl9TWlCYDtcbiAgICB9XG5cbiAgICByZXR1cm4gdXVpZDtcbiAgfVxufVxuIl19