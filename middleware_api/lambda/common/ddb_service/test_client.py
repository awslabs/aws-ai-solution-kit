# import os
# from typing import TypedDict
# from unittest import TestCase
#
# import pytest
#
# from layer.common.constants_ import ACM_METADATA_TABLE
# from layer.ddb_service.client import DynamoDbUtilsService
#
# os.environ.setdefault('AWS_PROFILE', 'cloudfront_ext')
# os.environ.setdefault(ACM_METADATA_TABLE, 'acm_table')
#
#
# class RandomTable(TypedDict):
#     pass
#
#
# @pytest.mark.skip(reason="dev only")
# class TestDynamoDbUtilsClient(TestCase):
#     def test_get_item(self):
#         ddb_client = DynamoDbUtilsService()
#         resp = ddb_client.get_item(table='my-test-table', key_values={
#             'id': '112233'
#         })
#         print(resp)
#         # obj =
#
#     def test_scan(self):
#         ddb_client = DynamoDbUtilsService()
#         resp = ddb_client.scan(table='my-test-table', filters={
#             'id': '112233',
#             'is_working': True
#         })
#         print(resp)
#
#     def test_update_item(self):
#         table = 'CloudFrontExtnConsoleStack-StepFunctionRpTsConstructacmmetadataAE01DAD1-16BIG5AUPKUGO'
#         ddb_client = DynamoDbUtilsService()
#         ddb_client.update_item(table=table, key={'taskToken': 'a36d4a88-94f1-4a16-b996-6e03fb7dd5e8',
#                                                  'domainName': 'refactoring-009.erinzh.com'}, field_name='taskStatus',
#                                value='CERT_ISSUED')
#
#         # self.fail()
