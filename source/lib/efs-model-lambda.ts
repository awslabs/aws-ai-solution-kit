import * as cdk from '@aws-cdk/core';
import { Construct, CustomResource, RemovalPolicy, CfnResource } from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda';
import { LayerVersion, Runtime, RuntimeFamily, Code, Function } from '@aws-cdk/aws-lambda';
import * as path from 'path';
import * as efs from "@aws-cdk/aws-efs";
import * as ec2 from "@aws-cdk/aws-ec2";
import * as cr from '@aws-cdk/custom-resources';
import { ILayerVersion } from "@aws-cdk/aws-lambda/lib/layers";

export interface EfsModelLambdaProps {
    readonly mountPath: string;
    readonly objects: string[];
    readonly handler: string;
    readonly code: Code;
    readonly runtime: lambda.Runtime;
    readonly layerPath?: string;
    readonly layers?: ILayerVersion[];
    readonly timeout?: cdk.Duration;
    readonly memorySize?: number;
    readonly environment?: {
        [key: string]: string;
    };
}

export class EfsModelLambda extends Construct {
    public function: Function
    layer: ILayerVersion;

    constructor(scope: Construct, id: string, props: EfsModelLambdaProps) {
        super(scope, id);

        const vpc = new ec2.Vpc(this, `aikits-vpc`.toLowerCase(), {
            cidr: '10.0.0.0/16',
            natGateways: 1,
            maxAzs: 3,
            subnetConfiguration: [
                {
                    name: 'private-subnet-aikits',
                    subnetType: ec2.SubnetType.PRIVATE,
                    cidrMask: 28,
                },
                {
                    name: 'public-subnet-aikits',
                    subnetType: ec2.SubnetType.PUBLIC,
                    cidrMask: 28,
                },
            ],
        });

        const securityGroup = new ec2.SecurityGroup(this, 'SecurityGroup', { vpc: vpc, });
        securityGroup.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.allTraffic());
        const lfs = new efs.FileSystem(this, `${id}-lambda-file-system`, {
            vpc: vpc,
            encrypted: true,
            lifecyclePolicy: efs.LifecyclePolicy.AFTER_14_DAYS,
            performanceMode: efs.PerformanceMode.GENERAL_PURPOSE,
            throughputMode: efs.ThroughputMode.PROVISIONED,
            provisionedThroughputPerSecond: cdk.Size.mebibytes(10),
            removalPolicy: cdk.RemovalPolicy.DESTROY,
        });
        // create a new access point from the filesystem
        const accessPoint = lfs.addAccessPoint('AccessPoint', {
            path: '/efs',
            createAcl: {
                ownerUid: '1000',
                ownerGid: '1000',
                permissions: '777',
            },
            // enforce the POSIX identity so lambda function will access with this identity
            posixUser: {
                uid: '1000',
                gid: '1000',
            },
        });

        const filesystem = lambda.FileSystem.fromEfsAccessPoint(accessPoint, props.mountPath)
        //copy model to efs
        const efsLambda = new lambda.Function(this, `efshandler`, {
            runtime: props.runtime,
            code: lambda.Code.fromAsset(path.join(__dirname, '../lib/s3_to_efs'), {
                bundling: {
                    image: lambda.Runtime.PYTHON_3_8.bundlingImage,
                    command: [
                        'bash', '-c', [
                            `cp -r /asset-input/* /asset-output/`,
                            `pip install -r requirements.txt --no-cache-dir --target /asset-output`
                        ].join(' && ')
                    ],
                }
            }),
            handler: "s3_to_efs.lambda_handler",
            memorySize: 512,
            timeout: cdk.Duration.minutes(10),
            vpc: vpc,
            allowPublicSubnet: true,
            vpcSubnets: {
                subnetType: ec2.SubnetType.PRIVATE,
            },
            securityGroups: [securityGroup],
            filesystem: filesystem,
        });

        const efsProvider = new cr.Provider(this, `provider`, {
            onEventHandler: efsLambda,
            // vpc: vpc,
        });

        const customResource = new CustomResource(this, `cr`, {
            serviceToken: efsProvider.serviceToken,
            resourceType: "Custom::EfsModelLambda",
            properties: {
                MountPath: props.mountPath,
                Objects: props.objects,
            },
            removalPolicy: RemovalPolicy.DESTROY,
        });

        if (props.layerPath != null) {
            this.layer = new lambda.LayerVersion(this, 'function_layer', {
                compatibleRuntimes: [
                    props.runtime,
                ],
                code: lambda.Code.fromAsset(props.layerPath, {
                    bundling: {
                        image: lambda.Runtime.PYTHON_3_8.bundlingImage,
                        command: [
                            'bash', '-c', [
                                `cd /asset-input`,
                                `pip install -r requirements.txt --no-cache-dir --target /asset-output`
                            ].join(' && ')
                        ],
                    }
                }),
                description: 'Lambda Layer',
            });
        }

        this.function = new lambda.Function(this, `app`, {
            runtime: lambda.Runtime.PYTHON_3_8,
            code: props.code,
            handler: props.handler,
            memorySize: props.memorySize,
            timeout: props.timeout,
            vpc: vpc,
            allowPublicSubnet: true,
            layers: props.layerPath == null ? [] : [this.layer],
            vpcSubnets: {
                subnetType: ec2.SubnetType.PRIVATE,
            },
            securityGroups: [securityGroup],
            filesystem: filesystem,
            environment: props.environment,
        });

        vpc.publicSubnets.forEach((subnet) => {
            const cfnSubnet = subnet.node.defaultChild as ec2.CfnSubnet
            cfnSubnet.addMetadata('cfn_nag', {
                rules_to_suppress: [
                    {
                        "id": "W33",
                    }
                ]
            });
        });

        const lambdaRolePolicy = efsLambda.role!.node.findChild('DefaultPolicy');
        (lambdaRolePolicy.node.defaultChild as cdk.CfnResource).cfnOptions.metadata = {
            cfn_nag: {
                rules_to_suppress: [
                    {
                        id: 'W12',
                    }
                ]
            }
        };

        const funRolePolicy = this.function.role!.node.findChild('DefaultPolicy');
        (funRolePolicy.node.defaultChild as cdk.CfnResource).cfnOptions.metadata = {
            cfn_nag: {
                rules_to_suppress: [
                    {
                        id: 'W12',
                    }
                ]
            }
        };

        const func = this.function.node.defaultChild as CfnResource
        func.addMetadata('cfn_nag', {
            rules_to_suppress: [
                {
                    "id": "W58",
                },
                {
                    "id": "W92",
                }
            ]
        });

        const efsFunc = efsLambda.node.defaultChild as CfnResource
        efsFunc.addMetadata('cfn_nag', {
            rules_to_suppress: [
                {
                    "id": "W58",
                },
                {
                    "id": "W92",
                }
            ]
        });

        
        const sg = securityGroup.node.defaultChild as CfnResource
        sg.addMetadata('cfn_nag', {
            rules_to_suppress: [
                {
                    "id": "W40",
                },
                {
                    "id": "W42",
                },
                {
                    "id": "W9",
                },
                {
                    "id": "W2",
                },
                {
                    "id": "W5",
                }
            ]
        });

        const vpcResource = vpc.node.defaultChild as CfnResource
        vpcResource.addMetadata('cfn_nag', {
            rules_to_suppress: [
                {
                    "id": "W60",
                }
            ]
        });

        (customResource.node.defaultChild as CfnResource).addMetadata('cfn_nag', {
            rules_to_suppress: [
                {
                    "id": "W58",
                }
            ]
        });
    }
}
