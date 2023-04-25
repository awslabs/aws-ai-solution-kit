import dataclasses
from enum import Enum
from typing import Optional, Any


class CreateModelStatus(Enum):
    Initial = 'Initial'
    Creating = 'Creating'
    Complete = 'Complete'
    Fail = 'Fail'


class CheckPointStatus(Enum):
    Initial = 'Initial'
    Active = 'Active'
    Disabled = 'Disabled'


@dataclasses.dataclass
class ModelJob:
    id: str
    name: str
    checkpoint_id: str
    model_type: str
    job_status: CreateModelStatus
    output_s3_location: Optional[str] = ''  # output location
    params: Optional[dict[str, Any]] = None

    def __post_init__(self):
        if type(self.job_status) == str:
            self.job_status = CreateModelStatus[self.job_status]

        # if self.params is not None and len(self.params) > 0:
        #     for key, val in self.params.items():
        #         if type(val) == Decimal:
        #             self.params[key] = float(val)


@dataclasses.dataclass
class CheckPoint:
    id: str
    checkpoint_type: str
    s3_location: str
    checkpoint_status: CheckPointStatus
    version: str = 'v1.0'  # todo: this is for the future
    checkpoint_names: Optional[list[str]] = None  # the actual checkpoint file names
    params: Optional[dict[str, Any]] = None

    def __post_init__(self):
        if type(self.checkpoint_status) == str:
            self.checkpoint_status = CheckPointStatus[self.checkpoint_status]


class TrainJobStatus(Enum):
    Initial = 'Initial'
    Training = 'Training'
    Complete = 'Complete'
    Fail = 'Fail'


@dataclasses.dataclass
class TrainJob:
    id: str
    model_id: str
    train_type: str
    job_status: TrainJobStatus
    input_s3_location: str
    checkpoint_id: str
    sagemaker_train_name: Optional[str] = ''
    sagemaker_sfn_arn: Optional[str] = ''
    params: Optional[dict[str, Any]] = None
    # { 'model': 'model.tar', 'data1': 'data1.tar' }
    # base s3: s3://bucket/dreambooth/123-123-0123/

    def __post_init__(self):
        if type(self.job_status) == str:
            self.job_status = TrainJobStatus[self.job_status]


@dataclasses.dataclass
class MultipartFileReq:
    filename: str
    parts_number: int

