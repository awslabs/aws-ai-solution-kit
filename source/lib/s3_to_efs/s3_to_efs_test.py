import json
import pytest
import logging
import os
from os import environ

import s3_to_efs


def test_lambda_handler():
    event = {
        "ResourceProperties": {
            "Objects": [
                'https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/porn-image-model/v1.0.0/resnest50_fast_4s2x40d.bin',
                'https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/porn-image-model/v1.0.0/resnest50_fast_4s2x40d.mapping',
                'https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/porn-image-model/v1.0.0/resnest50_fast_4s2x40d.xml'],
            "MountPath": "/",
        }
    }
    result = s3_to_efs.lambda_handler(event=event, context='')
    assert 1
