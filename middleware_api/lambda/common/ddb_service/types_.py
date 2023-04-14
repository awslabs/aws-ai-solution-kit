from typing import NamedTuple, Any, TypedDict, List

# Represents the output of a GetItem operation.


class ResponseMetadata(dict):
    pass

# Represents the amount of provisioned throughput capacity consumed on a table or
# an index.
class Capacity(NamedTuple):
    # The total number of capacity units consumed on a table or an index.
    CapacityUnits: float

    # The total number of read capacity units consumed on a table or an index.
    ReadCapacityUnits: float

    # The total number of write capacity units consumed on a table or an index.
    WriteCapacityUnits: float


# The capacity units consumed by an operation. The data returned includes the
# total provisioned throughput consumed, along with statistics for the table and
# any indexes involved in the operation. ConsumedCapacity is only returned if the
# request asked for it. For more information, see Provisioned Throughput
# (https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ProvisionedThroughputIntro.html)
# in the Amazon DynamoDB Developer Guide.
class ConsumedCapacity:
    # The total number of capacity units consumed by the operation.
    CapacityUnits: float

    # The amount of throughput consumed on each global index affected by the
    # operation.
    GlobalSecondaryIndexes: dict[str, Capacity]

    # The amount of throughput consumed on each local index affected by the operation.
    LocalSecondaryIndexes: dict[str, Capacity]

    # The total number of read capacity units consumed by the operation.
    ReadCapacityUnits: float

    # The amount of throughput consumed on the table affected by the operation.
    Table: Capacity

    # The name of the table that was affected by the operation.
    TableName: str

    # The total number of write capacity units consumed by the operation. \
    WriteCapacityUnits: float


class GetItemOutput(TypedDict):

    # The capacity units consumed by the GetItem operation. The data returned includes
    # the total provisioned throughput consumed, along with statistics for the table
    # and any indexes involved in the operation. ConsumedCapacity is only returned if
    # the ReturnConsumedCapacity parameter was specified. For more information, see
    # Read/Write Capacity Mode
    # (https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ProvisionedThroughputIntro.html)
    # in the Amazon DynamoDB Developer Guide. ConsumedCapacity *types.ConsumedCapacity
    # A map of attribute names to AttributeValue objects, as specified by
    # ProjectionExpression. Item map[string]types.AttributeValue
    # Metadata pertaining to the operation's result.
    ResponseMetadata: ResponseMetadata

    # The capacity units consumed by the GetItem operation. The data returned includes
    # the total provisioned throughput consumed, along with statistics for the table
    # and any indexes involved in the operation. ConsumedCapacity is only returned if
    # the ReturnConsumedCapacity parameter was specified. For more information, see
    # Read/Write Capacity Mode
    # (https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ProvisionedThroughputIntro.html)
    # in the Amazon DynamoDB Developer Guide.
    ConsumedCapacity: ConsumedCapacity

    # A map of attribute names to AttributeValue objects, as specified by
    # ProjectionExpression.
    Item: dict[str, dict[str, Any]]


# Represents the output of a Scan operation.
class ScanOutput(TypedDict):

    # The capacity units consumed by the Scan operation. The data returned includes
    # the total provisioned throughput consumed, along with statistics for the table
    # and any indexes involved in the operation. ConsumedCapacity is only returned if
    # the ReturnConsumedCapacity parameter was specified. For more information, see
    # Provisioned Throughput
    # (https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ProvisionedThroughputIntro.html)
    # in the Amazon DynamoDB Developer Guide.
    ConsumedCapacity: ConsumedCapacity

    # The number of items in the response. If you set ScanFilter in the request, then
    # Count is the number of items returned after the filter was applied, and
    # ScannedCount is the number of matching items before the filter was applied. If
    # you did not use a filter in the request, then Count is the same as ScannedCount.
    Count: int

    # An array of item attributes that match the scan criteria. Each element in this
    # array consists of an attribute name and the value for that attribute.
    Items: List[dict[str, dict[str, Any]]]

    # The primary key of the item where the operation stopped, inclusive of the
    # previous result set. Use this value to start a new operation, excluding this
    # value in the new request. If LastEvaluatedKey is empty, then the "last page" of
    # results has been processed and there is no more data to be retrieved. If
    # LastEvaluatedKey is not empty, it does not necessarily mean that there is more
    # data in the result set. The only way to know when you have reached the end of
    # the result set is when LastEvaluatedKey is empty.
    LastEvaluatedKey: dict[str, dict[str, Any]]

    # The number of items evaluated, before any ScanFilter is applied. A high
    # ScannedCount value with few, or no, Count results indicates an inefficient Scan
    # operation. For more information, see Count and ScannedCount
    # (https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/QueryAndScan.html#Count)
    # in the Amazon DynamoDB Developer Guide. If you did not use a filter in the
    # request, then ScannedCount is the same as Count.
    ScannedCount: int

    # Metadata pertaining to the operation's result.
    ResponseMetadata: ResponseMetadata
