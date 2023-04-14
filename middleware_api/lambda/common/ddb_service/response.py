import json
from datetime import datetime
from typing import TypedDict, Any, cast


# fixme: discover a better way for json serialization, maybe customize constructor
class Response(TypedDict):
    statusCode: int
    body: Any


def to_json_serializable(obj: Any) -> Any:
    if obj is None:
        return ''
    elif isinstance(obj, list):
        result = []
        for item in obj:
            result.append(to_json_serializable(item))
        return result
    elif isinstance(obj, datetime):
        return json.dumps(obj, indent=4, sort_keys=True, default=str)
    elif isinstance(obj, (int, float, str, bool)):
        return obj
    elif isinstance(obj, dict):
        to_obj = cast({}, obj)
        result = {}
        for key, val in to_obj.items():
            result[key] = to_json_serializable(val)
        return result
    else:
        return obj
