// Import the required CDK modules
import * as path from "path";
import { Duration, aws_sns as sns } from "aws-cdk-lib";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as stepfunctions from "aws-cdk-lib/aws-stepfunctions";
import * as stepfunctionsTasks from "aws-cdk-lib/aws-stepfunctions-tasks";
import { SnsPublishProps } from "aws-cdk-lib/aws-stepfunctions-tasks";
import { Construct } from "constructs";
import * as iam from "aws-cdk-lib/aws-iam";

export interface SagemakerInferenceProps {
    snsTopic: sns.Topic;
    snsErrorTopic: sns.Topic;
    inferenceJobName: string;
    endpointDeploymentJobName: string;
}

export class SagemakerInferenceStateMachine {
    public readonly stateMachineArn: string;
    private readonly scope: Construct;

    constructor(scope: Construct, props: SagemakerInferenceProps) {
        this.scope = scope;
        this.stateMachineArn = this.sagemakerStepFunction(
            props.snsTopic,
            props.snsErrorTopic,
            props.inferenceJobName,
            props.endpointDeploymentJobName,
        ).stateMachineArn;
    }

    private sagemakerStepFunction(
        snsTopic: sns.Topic,
        snsErrorTopic: sns.Topic,
        inferenceJobName: string,
        endpointDeploymentJobName: string 
    ): stepfunctions.StateMachine {
        const lambdaPolicy = // Grant Lambda permission to invoke SageMaker endpoint
            new iam.PolicyStatement({
                actions: [
                    "sagemaker:*",
                    "s3:Get*",
                    "s3:List*",
                    "s3:PutObject",
                    "s3:GetObject",
                    "sns:*",
                    "states:*",
                    "lambda:*",
                    "iam:*",
                    "sts:*",
                    "ecr:*",
                ],
                resources: ["*"],
            });

        // Define the Lambda functions
        const lambdaStartDeploy = new lambda.Function(
            this.scope,
            "LambdaModelDeploy",
            {
                runtime: lambda.Runtime.PYTHON_3_9,
                handler: "app.lambda_handler",
                code: lambda.Code.fromAsset(
                    path.join(
                        __dirname,
                        "../../../middleware_api/lambda/start_endpoint_deployment"
                    )
                ),
                environment: {
                    SNS_INFERENCE_SUCCESS: snsTopic.topicArn,
                    SNS_INFERENCE_ERROR: snsErrorTopic.topicArn,
                    DDB_INFERENCE_TABLE_NAME: inferenceJobName,
                    DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME: endpointDeploymentJobName
                },
            }
        );

        const lambdaCheckDeploymentStatus = new lambda.Function(
            this.scope,
            "LambdaModelAwait",
            {
                runtime: lambda.Runtime.PYTHON_3_9,
                handler: "app.lambda_handler",
                code: lambda.Code.fromAsset(
                    path.join(
                        __dirname,
                        "../../../middleware_api/lambda/check_endpoint_deployment"
                    )
                ),
                environment: {
                    SNS_INFERENCE_SUCCESS: snsTopic.topicName,
                    SNS_INFERENCE_ERROR: snsErrorTopic.topicName,
                    DDB_INFERENCE_TABLE_NAME: inferenceJobName,
                    DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME: endpointDeploymentJobName
                },
            }
        );

        // Create the SageMaker execution role
        const sagemakerRole = new iam.Role(this.scope, 'SagemakerExecutionRole', {
            assumedBy: new iam.ServicePrincipal('sagemaker.amazonaws.com'),
        });
  
        // Attach policies to the SageMaker execution role as needed
        sagemakerRole.addManagedPolicy(
            iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonS3FullAccess')
        );
        sagemakerRole.addManagedPolicy(
            iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSNSFullAccess"')
        )

            // Create a custom IAM policy to allow Lambda to pass the SageMaker execution role
        const sagemakerPassRolePolicy = new iam.PolicyStatement({
            actions: ['iam:PassRole'],
            resources: [sagemakerRole.roleArn],
        });

        lambdaStartDeploy.addToRolePolicy(lambdaPolicy);
        lambdaStartDeploy.addToRolePolicy(sagemakerPassRolePolicy)
        lambdaCheckDeploymentStatus.addToRolePolicy(lambdaPolicy);
        lambdaCheckDeploymentStatus.addToRolePolicy(sagemakerPassRolePolicy)

        // Define the Step Functions tasks
        const startDeploymentTask = new stepfunctionsTasks.LambdaInvoke(
            this.scope,
            "StartDeployment",
            {
                lambdaFunction: lambdaStartDeploy,
            }
        );

        const checkStatusDeploymentTask = new stepfunctionsTasks.LambdaInvoke(
            this.scope,
            "CheckStatusDeployment",
            {
                lambdaFunction: lambdaCheckDeploymentStatus,
            }
        );

        const checkDeploymentBranch = new stepfunctions.Choice(
            this.scope,
            "CheckDeploymentBranch"
        );

        const waitStatusDeploymentTask = new stepfunctions.Wait(
            this.scope,
            "WaitStatusDeployment",
            {
                time: stepfunctions.WaitTime.duration(Duration.minutes(2)),
            }
        );

        // Step to send SNS notification
        const sendNotification = new stepfunctionsTasks.SnsPublish(
            this.scope,
            "SendNotification",
            <SnsPublishProps>{
                topic: snsTopic,
                message: stepfunctions.TaskInput.fromText(
                    "EndPoint Creation job completed"
                ),
            }
        );

        // Define the Step Functions state machine
        const stateMachineDefinition = startDeploymentTask
            .next(checkStatusDeploymentTask)
            .next(
                checkDeploymentBranch
                    .when(
                        stepfunctions.Condition.stringEquals(
                            "$.Payload.status",
                            "Creating"
                        ),
                        waitStatusDeploymentTask.next(checkStatusDeploymentTask)
                    )
                    .when(
                        stepfunctions.Condition.stringEquals(
                            "$.Payload.status",
                            "InService"
                        ),
                        sendNotification
                    )
                    .afterwards()
            );

        return new stepfunctions.StateMachine(this.scope, "StateMachine", {
            definition: stateMachineDefinition,
        });
    }
}
