import logging
import os
from dataclasses import dataclass

from botocore.exceptions import ClientError

from common.ddb_service.client import DynamoDbUtilsService
from common.stepfunction_service.client import StepFunctionUtilsService
from create_model._types import ModelJob, CreateModelStatus

bucket_name = os.environ.get('S3_BUCKET')
model_table = os.environ.get('DYNAMODB_TABLE')
stepfunction_arn = os.environ.get('SFN_ARN')

sfn_arn = os.environ.get('')

logger = logging.getLogger('boto3')
ddb_service = DynamoDbUtilsService(logger=logger)
stepfunctions_client = StepFunctionUtilsService(logger=logger)


@dataclass
class Event:
    model_id: str
    status: str


def update_train_job_api(raw_event, context):
    event = Event(**raw_event)

    try:
        raw_training_job = ddb_service.get_item(table=model_table, key_values={'id': event.model_id})
        if raw_training_job is None:
            return {
                'statusCode': 200,
                'error': f'training model with id {event.model_id} is not found'
            }

        model_job = ModelJob(**raw_training_job)
        train_job_exec(model_job, CreateModelStatus[event.status])

        ddb_service.update_item(
            table=model_table,
            key={'id': event.model_id},
            field_name='job_status',
            value=event.status
        )

    except ClientError as e:
        logger.error(e)
        return {
            'statusCode': 200,
            'error': str(e)
        }

    return {
        'statusCode': 200,
        'trainJob': {
            'id': model_job.id,
            'status': model_job.job_status.value,
            's3_base': model_job.s3_location,
            'model_type': model_job.model_type,
            'sagemaker_id': model_job.sagemaker_job_id
        }
    }


def train_job_exec(model_job: ModelJob, action: CreateModelStatus):
    if model_job.job_status == CreateModelStatus.Creating and \
            (action != CreateModelStatus.Fail or action != CreateModelStatus.Complete):
        raise Exception(f'model creation job is currently under progress, so cannot be updated')

    if action == CreateModelStatus.Creating:
        # todo: start train step function
        stepfunctions_client.invoke_step_function(state_machine_arn=stepfunction_arn, func_input={
            'job_id': model_job.id
        })
        return
    elif action == CreateModelStatus.Initial:
        raise Exception('please create a new model creation job for this,'
                        f' not allowed overwrite old model creation job')
    else:
        # todo: other action
        return
