FROM public.ecr.aws/lambda/python:3.9

ARG FUNCTION_DIR="/opt/program"
# Lite version
ARG MODEL_URL="https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/infer-ocr-model/standard"
ARG MODEL_VERSION="v1.0.0"

ADD / ${FUNCTION_DIR}/

RUN pip3 install -r ${FUNCTION_DIR}/requirements.txt
RUN pip3 install --target ${FUNCTION_DIR} awslambdaric

RUN mkdir -p ${FUNCTION_DIR}/model
RUN yum install -y wget
RUN wget -c $MODEL_URL/$MODEL_VERSION/classifier.onnx -O ${FUNCTION_DIR}/model/classifier.onnx
RUN wget -c $MODEL_URL/$MODEL_VERSION/det_standard.onnx -O ${FUNCTION_DIR}/model/det_standard.onnx
RUN wget -c $MODEL_URL/$MODEL_VERSION/keys_v1.txt -O ${FUNCTION_DIR}/model/keys_v1.txt
RUN wget -c $MODEL_URL/$MODEL_VERSION/rec_standard.onnx -O ${FUNCTION_DIR}/model/rec_standard.onnx

WORKDIR ${FUNCTION_DIR}
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PYTHONIOENCODING="utf8"
ENV MODEL_NAME="standard"
ENV MODEL_PATH="${FUNCTION_DIR}/model/"

ENTRYPOINT [ "python3", "-m", "awslambdaric" ]
CMD [ "infer_ocr_app.handler" ]