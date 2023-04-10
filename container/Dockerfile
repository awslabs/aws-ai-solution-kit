FROM 763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:1.13.1-gpu-py39-cu117-ubuntu20.04-sagemaker

WORKDIR /

COPY ./aigc-webui /opt/ml/code/

# VOLUME /tmp/dev/

RUN alias python=/opt/ml/code/venv/bin/python

ENV SAGEMAKER_PROGRAM sagemaker_dreambooth_train.py

# ENTRYPOINT ["sh", "/app/venv/bin/activate"]
