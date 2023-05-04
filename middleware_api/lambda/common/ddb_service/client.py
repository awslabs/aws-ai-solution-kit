import datetime
import enum
import json
import logging
from decimal import Decimal
from typing import Any, List, Dict

import boto3
from botocore.exceptions import ClientError

from common.ddb_service.types_ import GetItemOutput, ScanOutput


class DynamoDbUtilsService:

    def __init__(self, logging_level=logging.INFO, logger=None):
        self.client = boto3.client('dynamodb')
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger('boto3')
            self.logger.setLevel(logging_level)

    def put_items(self, table: str, entries: Dict[str, Any]) -> Any:
        if not table:
            raise Exception('table name is required')

        try:
            if not entries or len(entries) == 0:
                return None

            ddb_data = DynamoDbUtilsService._serialize(entries)
            resp = self.client.put_item(
                TableName=table,
                Item=ddb_data
            )
            # todo: check if failed raise an error

            return resp
        except Exception as e:
            self.logger.error(f'table {table} put item failed -> {entries}: {e}')
            raise Exception(f'table {table} put item failed -> {entries}: {e}')

    def update_item(self, table: str, key: Dict[str, Any], field_name: str, value: Any):
        search_keys = self._serialize(key)
        value = self._convert(value)
        try:
            self.client.update_item(
                TableName=table,
                Key=search_keys,
                UpdateExpression=f"set {field_name} = :r",
                ExpressionAttributeValues={
                    ':r': value
                },
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as e:
            self.logger.error('keys: %s -> %s: %s', key, field_name, value)
            raise Exception(f'dynamodb update failed with table {table}, key: {key}, field: {field_name}, value: {value}, error: {e}')

    def get_item(self, table: str, key_values: Dict[str, Any]) -> Dict[str, Any]:
        try:
            search_keys = self._serialize(key_values)

            resp = self.client.get_item(
                TableName=table,
                Key=search_keys
            )
            named_ = GetItemOutput(**resp)
            if 'Item' not in named_:
                return dict()
            res = self.deserialize(named_['Item'])
            return res
        except ClientError as e:
            self.logger.error(f'table {table} keys_values: {key_values}')
            raise Exception(f'table {table} get_item failed with keys_values: {key_values}, e: {e}')

    def scan(self, table: str, filters: Dict[str, Any]) -> List[Dict[str, Dict[str, Any]]]:
        prepare_filter_expressions = []
        prefix = ':'
        expression_values = {}
        for key, val in filters.items():
            if isinstance(val, list):
                print(key)
                val_keys = ''
                i = 0
                for v in val:
                    k = f'{prefix}{key}{str(i)}'
                    i += 1
                    val_keys += f'{k}, '
                    expression_values[k] = self._convert(v)

                prepare_filter_expressions.append('{} in ({})'.format(key, val_keys[:len(val_keys) - 2]))
            else:
                prepare_filter_expressions.append('{} = {}'.format(key, prefix+key))
                expression_values[prefix+key] = self._convert(val)
        filter_expressions = ' AND '.join(prepare_filter_expressions)
        # expression_values = self._serialize(filters, prefix)

        resp = self.client.scan(
            TableName=table,
            FilterExpression=filter_expressions,
            ExpressionAttributeValues=expression_values
        )
        self.logger.info('scan response: %s', json.dumps(resp))
        named_ = ScanOutput(**resp)
        # FIXME: handle failures
        return named_['Items']

    def get_all(self, table: str) -> List[dict[str, Any]]:
        resp = self.client.scan(TableName=table)
        named_ = ScanOutput(**resp)
        result = []
        for item in named_['Items']:
            result.append(self.deserialize(item))
        return result

    def delete_item(self, table: str, keys: dict[str, Any]):
        keys = self._serialize(keys)
        self.client.delete_item(
            TableName=table,
            Key=keys
        )
        # FIXME: handle failures

    def close(self):
        self.client.close()

    @staticmethod
    def _serialize(entries: dict[str, Any], prefix: str = '') -> dict[str, Any]:
        if not dict:
            return {}
        result = dict()
        for key, val in entries.items():
            resolved_val = DynamoDbUtilsService._convert(val)
            if resolved_val:
                result["{}{}".format(prefix, key)] = resolved_val
        return result

    @staticmethod
    # serializer = boto3.dynamodb.types.TypeSerializer()
    # low_level_copy = {k: serializer.serialize(v) for k,v in python_data.items()}
    def _convert(val):
        if val is None:
            return None
        if isinstance(val, bool):
            return {'BOOL': val}
        elif isinstance(val, list):
            val_arr = []
            for item in val:
                val_arr.append(DynamoDbUtilsService._convert(item))
            return {'L': val_arr}
        elif isinstance(val, float) or isinstance(val, int) or isinstance(val, Decimal):
            return {'N': str(val)}
        elif isinstance(val, str):
            return {'S': str(val)}
        elif isinstance(val, enum.Enum):
            return {'S': str(val.value)}
        elif isinstance(val, dict):
            res = {}
            for key, val in val.items():
                if val is not None:
                    res[key] = DynamoDbUtilsService._convert(val)

            return {'M': res}
        elif isinstance(val, datetime.datetime):
            return {'S': str(val)}
        else:
            raise Exception(f'unknown type {val} at type: {type(val)}')

    @staticmethod
    def deserialize(rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
        boto3.resource('dynamodb')
        # To go from low-level format to python
        deserializer = boto3.dynamodb.types.TypeDeserializer()
        python_data = {k: deserializer.deserialize(v) for k, v in rows.items()}
        return python_data
