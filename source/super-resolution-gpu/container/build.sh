#!/usr/bin/env bash

algorithm_name=ai-kits-super-resolution

account=$(aws sts get-caller-identity --query Account --output text)

# Get the region defined in the current configuration (default to us-west-2 if none defined)
region=$(aws configure get region)
region=${region:-us-west-2}

fullname="${account}.dkr.ecr.${region}.amazonaws.com/${algorithm_name}"
TAG=`date '+%Y%m%d%H%M%S'`

# If the repository doesn't exist in ECR, create it.

aws ecr describe-repositories --repository-names "${algorithm_name}" > /dev/null 2>&1

if [ $? -ne 0 ]
then
    aws ecr create-repository --repository-name "${algorithm_name}" > /dev/null
fi

# Get the login command from ECR in order to pull down the SageMaker PyTorch image
aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin 763104351884.dkr.ecr.${region}.amazonaws.com
# Build the docker image locally with the image name and then push it to ECR
# with the full name.
docker build  -t ${algorithm_name} . --build-arg REGISTRY_URI="763104351884.dkr.ecr.${region}.amazonaws.com/pytorch-inference-neuron:1.7.1-neuron-py36-ubuntu18.04"
docker tag ${algorithm_name} ${fullname}:${TAG}

# Get the login command from ECR and execute it directly
aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin ${account}.dkr.ecr.${region}.amazonaws.com
docker push ${fullname}:${TAG}
