import * as ec2 from '@aws-cdk/aws-ec2';
import * as iam from '@aws-cdk/aws-iam';
import { Construct } from 'constructs';
import { Construct as CoreConstruct } from '@aws-cdk/core';
/**
 * @stability stable
 */
export interface ECRDeploymentProps {
    /**
     * The source of the docker image.
     *
     * @stability stable
     */
    readonly src: IImageName;
    /**
     * The destination of the docker image.
     *
     * @stability stable
     */
    readonly dest: IImageName;
    /**
     * The amount of memory (in MiB) to allocate to the AWS Lambda function which replicates the files from the CDK bucket to the destination bucket.
     *
     * If you are deploying large files, you will need to increase this number
     * accordingly.
     *
     * @default 512
     * @stability stable
     */
    readonly memoryLimit?: number;
    /**
     * Execution role associated with this function.
     *
     * @default - A role is automatically created
     * @stability stable
     */
    readonly role?: iam.IRole;
    /**
     * The VPC network to place the deployment lambda handler in.
     *
     * @default None
     * @stability stable
     */
    readonly vpc?: ec2.IVpc;
    /**
     * Where in the VPC to place the deployment lambda handler.
     *
     * Only used if 'vpc' is supplied.
     *
     * @default - the Vpc default strategy if not specified
     * @stability stable
     */
    readonly vpcSubnets?: ec2.SubnetSelection;
    /**
     * The environment variable to set.
     *
     * @stability stable
     */
    readonly environment?: {
        [key: string]: string;
    };
}
/**
 * @stability stable
 */
export interface IImageName {
    /**
     * The uri of the docker image.
     *
     * The uri spec follows https://github.com/containers/skopeo
     *
     * @stability stable
     */
    readonly uri: string;
    /**
     * The credentials of the docker image.
     *
     * Format `user:[password]`
     *
     * @stability stable
     */
    creds?: string;
}
/**
 * @stability stable
 */
export declare class DockerImageName implements IImageName {
    private name;
    creds?: string | undefined;
    /**
     * @stability stable
     */
    constructor(name: string, creds?: string | undefined);
    /**
     * The uri of the docker image.
     *
     * The uri spec follows https://github.com/containers/skopeo
     *
     * @stability stable
     */
    get uri(): string;
}
/**
 * @stability stable
 */
export declare class S3ArchiveName implements IImageName {
    creds?: string | undefined;
    private name;
    /**
     * @stability stable
     */
    constructor(p: string, ref?: string, creds?: string | undefined);
    /**
     * The uri of the docker image.
     *
     * The uri spec follows https://github.com/containers/skopeo
     *
     * @stability stable
     */
    get uri(): string;
}
/**
 * @stability stable
 */
export declare class ECRDeployment extends CoreConstruct {
    private handler;
    /**
     * @stability stable
     */
    constructor(scope: Construct, id: string, props: ECRDeploymentProps);
    /**
     * @stability stable
     */
    get serviceToken(): string
    private renderSingletonUuid;
}
