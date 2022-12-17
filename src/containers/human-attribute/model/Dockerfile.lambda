FROM public.ecr.aws/lambda/python:3.9

ARG FUNCTION_DIR="/opt/program"
ARG MODEL_URL_DET="https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/object-detection"
ARG MODEL_URL_ATTR="https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/human-attribute"

ARG MODEL_VERSION="1.2.0"

ADD / ${FUNCTION_DIR}/

RUN pip3 install -r ${FUNCTION_DIR}/requirements.txt
RUN pip3 install --target ${FUNCTION_DIR} awslambdaric

RUN mkdir -p ${FUNCTION_DIR}/model
RUN yum install -y wget
RUN wget -c ${MODEL_URL_DET}/${MODEL_VERSION}/yolox_l.onnx -O ${FUNCTION_DIR}/model/yolox_l.onnx
RUN wget -c ${MODEL_URL_ATTR}/${MODEL_VERSION}/model_1.onnx -O ${FUNCTION_DIR}/model/model_1.onnx
RUN wget -c ${MODEL_URL_ATTR}/${MODEL_VERSION}/model_2.onnx -O ${FUNCTION_DIR}/model/model_2.onnx
RUN wget -c ${MODEL_URL_ATTR}/${MODEL_VERSION}/model_3.onnx -O ${FUNCTION_DIR}/model/model_3.onnx
RUN wget -c ${MODEL_URL_ATTR}/${MODEL_VERSION}/model_4.onnx -O ${FUNCTION_DIR}/model/model_4.onnx

WORKDIR ${FUNCTION_DIR}
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PYTHONIOENCODING="utf8"
ENV MODEL_VERSION=MODEL_VERSION
ENV MODEL_PATH="${FUNCTION_DIR}/model/"

ENTRYPOINT [ "python3", "-m", "awslambdaric" ]
CMD [ "human_attribute_app.handler" ]
