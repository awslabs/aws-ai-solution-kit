# Use the official PyTorch image as the base
FROM pytorch/pytorch:1.9.0-cuda11.1-cudnn8-runtime

# Set the working directory
WORKDIR /opt/ml/code

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the custom training script into the container
COPY train.py /opt/ml/code/train.py

# Set the default command for the container
ENTRYPOINT ["python", "train.py"]