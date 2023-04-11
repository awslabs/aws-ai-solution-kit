import dataclasses
from enum import Enum
from typing import Optional


class CreateModelStatus(Enum):
    Initial = 'Initial'
    Train = 'Train'
    Complete = 'Complete'
    Fail = 'Fail'


@dataclasses.dataclass
class Model:
    id: str
    s3_location: str
    model_type: str
    status: CreateModelStatus
    sagemaker_job_id: Optional[str] = None
