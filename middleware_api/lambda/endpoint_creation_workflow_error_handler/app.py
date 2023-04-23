import boto3

def lambda_handler(event, context):
    # Parse the input data
    # update the checkpoint creation job status for the failure reason 
    print(f"event is {event}")
   
    return event