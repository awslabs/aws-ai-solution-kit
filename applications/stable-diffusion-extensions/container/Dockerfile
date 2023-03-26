# Using AWS SageMaker's pre-built PyTorch image
FROM 763104351884.dkr.ecr.us-west-2.amazonaws.com/pytorch-training:1.13.1-gpu-py39-cu117-ubuntu20.04-sagemaker

# Set the working directory
WORKDIR /opt/ml/code

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the custom training script into the container
COPY train.py /opt/ml/code/train.py

# define train.py as the script entry point
ENV SAGEMAKER_PROGRAM train.py