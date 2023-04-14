import json

def lambda_handler(event, context):
    # Parse the input data
    print(f"event is {event}")

    # Return the output data
    return {'Output': json.dumps(event),
            'status': 'InService'}