import dataclasses
from enum import Enum
from typing import Optional, Any


class CreateModelStatus(Enum):
    Initial = 'Initial'
    Creating = 'Creating'
    Complete = 'Complete'
    Fail = 'Fail'


@dataclasses.dataclass
class ModelJob:
    id: str
    s3_location: str
    model_type: str
    job_status: CreateModelStatus
    params: Optional[dict[str, Any]] = None
    sagemaker_job_id: Optional[str] = None

    def __post_init__(self):
        if type(self.job_status) == str:
            self.job_status = CreateModelStatus[self.job_status]

