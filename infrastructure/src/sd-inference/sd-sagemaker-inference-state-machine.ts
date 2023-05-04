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
    s3_bucket_name: string;
    endpointDeploymentJobName: string;
    userNotifySNS: sns.Topic; 
    inference_ecr_url: string;
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
            props.s3_bucket_name,
            props.endpointDeploymentJobName,
            props.userNotifySNS,
            props.inference_ecr_url
        ).stateMachineArn;
    }

    private sagemakerStepFunction(
        snsTopic: sns.Topic,
        snsErrorTopic: sns.Topic,
        inferenceJobName: string,
        s3BucketName: string,
        endpointDeploymentJobName: string,
        userNotifySNS: sns.Topic,
        inference_ecr_url: string,
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
                    "dynamodb:*"
                ],
                resources: ["*"],
            });

        const lambdaErrorHandler = new lambda.Function(
            this.scope,
            "InferenceWorkflowErrorHandler",
            {
                runtime: lambda.Runtime.PYTHON_3_9,
                handler: "app.lambda_handler",
                code: lambda.Code.fromAsset(
                    path.join(
                        __dirname,
                        "../../../middleware_api/lambda/endpoint_creation_workflow_error_handler"
                    )
                ),
                // Add any environment variables needed for the error handler Lambda
                environment: {
                    SNS_INFERENCE_SUCCESS: snsTopic.topicArn,
                    SNS_INFERENCE_ERROR: snsErrorTopic.topicArn,
                    DDB_INFERENCE_TABLE_NAME: inferenceJobName,
                    DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME: endpointDeploymentJobName,
                    SNS_NOTIFY_TOPIC_ARN: userNotifySNS.topicArn,
                    S3_BUCKET_NAME: s3BucketName,
                    INFERENCE_ECR_IMAGE_URL: inference_ecr_url
                },
            }
        );
            
        lambdaErrorHandler.addToRolePolicy(lambdaPolicy);
            
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
                    DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME: endpointDeploymentJobName,
                    SNS_NOTIFY_TOPIC_ARN: userNotifySNS.topicArn,
                    S3_BUCKET_NAME: s3BucketName,
                    INFERENCE_ECR_IMAGE_URL: inference_ecr_url
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
                    DDB_ENDPOINT_DEPLOYMENT_TABLE_NAME: endpointDeploymentJobName,
                    SNS_NOTIFY_TOPIC_ARN: userNotifySNS.topicArn,
                    S3_BUCKET_NAME: s3BucketName,
                    INFERENCE_ECR_IMAGE_URL: inference_ecr_url
                },
            }
        );

        //TODO: still not working for assume sagemaker service, need to work it later
        lambdaStartDeploy.addToRolePolicy(lambdaPolicy)
        lambdaCheckDeploymentStatus.addToRolePolicy(lambdaPolicy);

        // Add the trust relationship for SageMaker service principal to both Lambda roles
        const sagemakerAssumeRolePolicy = new iam.PolicyStatement({
            actions: ['sts:AssumeRole'],
            effect: iam.Effect.ALLOW,
            principals: [new iam.ServicePrincipal('sagemaker.amazonaws.com')],
        });
  
        (lambdaStartDeploy.role as iam.Role).assumeRolePolicy?.addStatements(sagemakerAssumeRolePolicy);
        (lambdaCheckDeploymentStatus.role as iam.Role).assumeRolePolicy?.addStatements(sagemakerAssumeRolePolicy);
        lambdaCheckDeploymentStatus.role?.grant(new iam.ServicePrincipal('sagemaker.amazonaws.com'))


        // Define the Step Functions tasks
        const errorHandlerTask = new stepfunctionsTasks.LambdaInvoke(
            this.scope,
            "ErrorHandlerTask",
            {
                lambdaFunction: lambdaErrorHandler,
            }
        );

        const startDeploymentTask = new stepfunctionsTasks.LambdaInvoke(
            this.scope,
            "StartDeployment",
            {
                lambdaFunction: lambdaStartDeploy,
            }
        ).addCatch(errorHandlerTask, {
            errors: ["States.ALL"],
            resultPath: "$.error",
        });

        const checkStatusDeploymentTask = new stepfunctionsTasks.LambdaInvoke(
            this.scope,
            "CheckStatusDeployment",
            {
                lambdaFunction: lambdaCheckDeploymentStatus,
            }
        ).addCatch(errorHandlerTask, {
            errors: ["States.ALL"],
            resultPath: "$.error",
        });

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
