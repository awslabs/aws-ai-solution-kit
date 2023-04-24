# Authenticate to a public registry: aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws
FROM public.ecr.aws/lambda/python:3.9-x86_64

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}
COPY requirements.txt .

# Install dependencies 
RUN pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.lambda_handler" ]