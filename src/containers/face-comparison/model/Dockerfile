FROM public.ecr.aws/lambda/python:3.9

ARG FUNCTION_DIR="/opt/program"
ARG MODEL_URL="https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/face-comparison"
ARG MODEL_VERSION="1.2.0"

ADD / ${FUNCTION_DIR}/

RUN pip3 install -r ${FUNCTION_DIR}/requirements.txt
RUN pip3 install --target ${FUNCTION_DIR} awslambdaric

RUN mkdir -p ${FUNCTION_DIR}/model
RUN yum install -y wget
RUN wget -c ${MODEL_URL}/${MODEL_VERSION}/det.onnx -O ${FUNCTION_DIR}/model/det.onnx
RUN wget -c ${MODEL_URL}/${MODEL_VERSION}/w600k_r50.onnx -O ${FUNCTION_DIR}/model/w600k_r50.onnx

WORKDIR ${FUNCTION_DIR}
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PYTHONIOENCODING="utf8"
ENV MODEL_VERSION=MODEL_VERSION
ENV MODEL_PATH="${FUNCTION_DIR}/model/"

ENTRYPOINT [ "python3", "-m", "awslambdaric" ]
CMD [ "face_comparison_app.handler" ]
