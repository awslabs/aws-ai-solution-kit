import datetime
from typing import TypedDict


class ResponseMetadata(dict):
    pass


class StartExecutionOutput(TypedDict):
    # The Amazon Resource Name (ARN) that identifies the execution.
    #
    # This member is required.
    executionArn: str

    # The date the execution is started.
    #
    # This member is required.
    startDate: datetime.time

    # Metadata pertaining to the operation's result.
    ResponseMetadata: ResponseMetadata
