import dataclasses
from decimal import Decimal
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
    s3_location: str  # input location
    model_type: str
    job_status: CreateModelStatus
    params: Optional[dict[str, Any]] = None

    def __post_init__(self):
        if type(self.job_status) == str:
            self.job_status = CreateModelStatus[self.job_status]

        # if self.params is not None and len(self.params) > 0:
        #     for key, val in self.params.items():
        #         if type(val) == Decimal:
        #             self.params[key] = float(val)
