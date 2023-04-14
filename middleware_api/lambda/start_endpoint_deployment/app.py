import json

def lambda_handler(event, context):
    # Parse the input data
    print(f"event is {event}")
    input_data = json.loads(event['Input'])

    # Do some processing with the input data
    output_data = {'result': input_data['number'] * 2}

    # Return the output data
    return {'Output': json.dumps(output_data)}