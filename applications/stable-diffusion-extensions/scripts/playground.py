import boto3
import sagemaker
from sagemaker import get_execution_role
from sagemaker.estimator import Estimator
from sagemaker.tuner import IntegerParameter, CategoricalParameter, ContinuousParameter, HyperparameterTuner

# Initial setup for SageMaker
session = sagemaker.Session()
role = get_execution_role()
aws_region = boto3.Session().region_name

# Create ECR repository, we will not build the image, we will use the pre-built image
ecr = boto3.client('ecr')

# Skip the creation of the repository if it already exists
try:
    ecr.describe_repositories(repositoryNames=['sd-extensions'])
except ecr.exceptions.RepositoryNotFoundException:
    ecr.create_repository(repositoryName='sd-extensions')
container_image_uri = ecr.describe_repositories(repositoryNames=['sd-extensions'])['repositories'][0]['repositoryUri']
print(container_image_uri)

# Sample training data is available in this bucket
training_data_bucket = f"jumpstart-cache-prod-{aws_region}"
training_data_prefix = "training-datasets/dogs_sd_finetuning/"

training_dataset_s3_path = f"s3://{training_data_bucket}/{training_data_prefix}"

output_bucket = session.default_bucket()
output_prefix = "jumpstart-example-sd-training"

s3_output_location = f"s3://{output_bucket}/{output_prefix}/output"

# Create an Estimator instance for model training
estimator = Estimator(image_uri=container_image_uri,
                      role=role,
                      instance_count=1,
                      instance_type='ml.m5.large',
                      base_job_name='stable-diffusion-model-training')

###############################################################

# Start the training job, wait for it to complete. note such training data is not used for training, it is just a placeholder
estimator.fit({'training_dataset_s3_path': training_dataset_s3_path}, wait=True)

###############################################################

# Configure hyperparameter tuning (replace with the specific hyperparameters for your algorithm)
hyperparameter_ranges = {'learning_rate': ContinuousParameter(0.001, 0.1)}

# Set the objective metric
objective_metric_name = 'validation:accuracy'

# Create a HyperparameterTuner instance
tuner = HyperparameterTuner(estimator,
                            objective_metric_name,
                            hyperparameter_ranges,
                            max_jobs=10,
                            max_parallel_jobs=2)

# Launch the hyperparameter tuning job
tuner.fit({'train': training_dataset_s3_path})

# Wait for the tuning to complete
tuner.wait()

###############################################################

# Deploy the best model to an endpoint
predictor = tuner.deploy(initial_instance_count=1, instance_type='ml.m5.large')

# Perform real-time inference with the deployed model (replace with the appropriate input for your algorithm)
sample_data = 'your-input-data-for-inference'
response = predictor.predict(sample_data)

###############################################################

# Optional: Delete the endpoint after use
predictor.delete_endpoint()