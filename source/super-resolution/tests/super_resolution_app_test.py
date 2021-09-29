import json
import pytest
import logging
import os
from os import environ

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
environ['ACCESS_POINT'] = BASE_DIR + '/model'

from src import super_resolution_app


def test_lambda_handler():
    event = {
        "body": {
            "url": "https://xiaotih.s3.us-west-2.amazonaws.com/AIKits/dog.png",
            "scale": "2"
        }
    }
    result = super_resolution_app.lambda_handler(event=event, context='')
    body = json.loads(result['body'])
    print(body['normal'])

test_lambda_handler()