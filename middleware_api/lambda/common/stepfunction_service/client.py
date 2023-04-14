import json
import logging
from typing import Any

import boto3

from common.stepfunction_service.types_ import StartExecutionOutput


class StepFunctionUtilsService:

    def __init__(self, region='us-east-1', logging_level=logging.INFO, logger=None):
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger('boto3')
            self.logger.setLevel(logging_level)
        self.stepf_client = boto3.client('stepfunctions')

    def set_task(self, token: str, task: str, output: Any = None):
        task_name = task.lower()
        try:
            if task_name == 'success':
                self.stepf_client.send_task_success(
                    taskToken=token,
                    output=json.dumps(output, default=str)
                )
            elif task_name == 'failure':
                self.stepf_client.send_task_failure(
                    taskToken=token,
                    error=json.dumps(output)
                )
            elif task_name == 'heartbeat':
                self.stepf_client.send_task_heartbeat(
                    taskToken=token
                )
            else:
                raise Exception('unknown task type [%s]', task)
        except Exception as e:
            self.logger.error(f'send task error {e}')
            raise e

    def invoke_step_function(self, state_machine_arn: str, func_input: Any) -> str:
        self.logger.info('start to invoke step function with input %s', func_input)
        try:
            resp = self.stepf_client.start_execution(
                stateMachineArn=state_machine_arn,
                input=json.dumps(func_input, default=str)
            )
            self.logger.info('step function invoked: %s', resp)
            named_ = StartExecutionOutput(**resp)
            return named_['executionArn']
        except Exception as e:
            self.logger.error(f'error invoking step function {state_machine_arn}: {e}')
            raise e

