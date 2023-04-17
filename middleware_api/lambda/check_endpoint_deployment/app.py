import boto3

sagemaker = boto3.client('sagemaker')

def lambda_handler(event, context):
    # Parse the input data
    print(f"event is {event}")

    stage = event["Payload"]['stage']
    if stage == 'Training':
        # name = event['name']
        # training_details = describe_training_job(name)
        # print(training_details)
        # status = training_details['HyperParameterTuningJobStatus']
        # if status == 'Completed':
        #     s3_output_path = training_details['TrainingJobDefinition']['OutputDataConfig']['S3OutputPath']
        #     model_data_url = os.path.join(s3_output_path, training_details['BestTrainingJob']['TrainingJobName'], 'output/model.tar.gz')
        #     event['message'] = 'HPO tunning job "{}" complete. Model data uploaded to "{}"'.format(name, model_data_url)
        #     event['model_data_url'] = model_data_url
        #     event['best_training_job'] = training_details['BestTrainingJob']['TrainingJobName']
        # elif status == 'Failed':
        #     failure_reason = training_details['FailureReason']
        #     event['message'] = 'Training job failed. {}'.format(failure_reason)
        print("Status check for training not implemented yet!")
    elif stage == 'Deployment':
        name = event["Payload"]['endpoint_name']
        endpoint_details = describe_endpoint(name)
        status = endpoint_details['EndpointStatus']
        if status == 'InService':
            event["Payload"]['message'] = 'Deployment completed for endpoint "{}".'.format(name)
        elif status == 'Failed':
            failure_reason = endpoint_details['FailureReason']
            event["Payload"]['message'] = 'Deployment failed for endpoint "{}". {}'.format(name, failure_reason)
        elif status == 'RollingBack':
            event["Payload"]['message'] = 'Deployment failed for endpoint "{}", rolling back to previously deployed version.'.format(name)
    event['status'] = status
    return event

# def describe_training_job(name):
#     """ Describe SageMaker training job identified by input name.
#     Args:
#         name (string): Name of SageMaker training job to describe.
#     Returns:
#         (dict)
#         Dictionary containing metadata and details about the status of the training job.
#     """
#     try:
#         response = sagemaker.describe_hyper_parameter_tuning_job(
#             HyperParameterTuningJobName=name
#         )
#     except Exception as e:
#         print(e)
#         print('Unable to describe hyperparameter tunning job.')
#         raise(e)
#     return response

def describe_endpoint(name):
    """ Describe SageMaker endpoint identified by input name.
    Args:
        name (string): Name of SageMaker endpoint to describe.
    Returns:
        (dict)
        Dictionary containing metadata and details about the status of the endpoint.
    """
    try:
        response = sagemaker.describe_endpoint(
            EndpointName=name
        )
    except Exception as e:
        print(e)
        print('Unable to describe endpoint.')
        raise(e)
    return response
