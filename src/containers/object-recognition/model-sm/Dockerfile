FROM 727897471807.dkr.ecr.cn-north-1.amazonaws.com.cn/pytorch-inference:1.11.0-gpu-py38-cu113-ubuntu20.04-sagemaker

ARG FUNCTION_DIR="/opt/ml/model"
ARG MODEL_URL="https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/object-detection"
ARG MODEL_VERSION="1.2.0"

ADD / ${FUNCTION_DIR}/

RUN pip3 install -r ${FUNCTION_DIR}/requirements.txt

RUN mkdir -p ${FUNCTION_DIR}/model
RUN wget -c ${MODEL_URL}/${MODEL_VERSION}/yolox_l.onnx -O ${FUNCTION_DIR}/model/yolox_l.onnx

WORKDIR ${FUNCTION_DIR}
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PYTHONIOENCODING="utf8"
ENV MODEL_VERSION=MODEL_VERSION
ENV MODEL_PATH="${FUNCTION_DIR}/model/"

ENTRYPOINT ["python", "predictor.py"]
