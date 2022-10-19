#FROM 727897471807.dkr.ecr.cn-north-1.amazonaws.com.cn/pytorch-inference:1.12.1-gpu-py38-cu113-ubuntu20.04-sagemaker
FROM 763104351884.dkr.ecr.us-west-2.amazonaws.com/pytorch-inference:1.12.1-gpu-py38-cu113-ubuntu20.04-sagemaker

ARG FUNCTION_DIR="/opt/ml/model"

ARG MODEL_URL="https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/green-screen-matting"
ARG MODEL_VERSION="1.2.0"

ADD / ${FUNCTION_DIR}/

RUN pip install -r ${FUNCTION_DIR}/requirements.txt


RUN mkdir -p ${FUNCTION_DIR}/model
#RUN yum install -y wget
RUN wget -c $MODEL_URL/$MODEL_VERSION/chroma-key.onnx -O ${FUNCTION_DIR}/model/chroma-key.onnx

WORKDIR ${FUNCTION_DIR}
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PYTHONIOENCODING="utf8"
ENV MODEL_NAME="standard"
ENV MODEL_PATH="${FUNCTION_DIR}/model/"

ENTRYPOINT ["python", "predictor.py"]