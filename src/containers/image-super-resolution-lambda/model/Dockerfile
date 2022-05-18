FROM public.ecr.aws/lambda/python:3.9

ARG FUNCTION_DIR="/opt/program"
ARG MODEL_URL="https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/super-resolution-model"
ARG MODEL_VERSION="v1.0.0"

ADD / ${FUNCTION_DIR}/

RUN python3 -m pip install -r ${FUNCTION_DIR}/requirements.txt
RUN pip3 install --target ${FUNCTION_DIR} awslambdaric

RUN mkdir -p ${FUNCTION_DIR}/model/advanced
RUN yum install -y wget
RUN wget -c ${MODEL_URL}/${MODEL_VERSION}/Real_ESRGAN_x2.onnx -O ${FUNCTION_DIR}/model/Real_ESRGAN_x2.onnx
RUN wget -c ${MODEL_URL}/${MODEL_VERSION}/Real_ESRGAN_x4.onnx -O ${FUNCTION_DIR}/model/Real_ESRGAN_x4.onnx

WORKDIR ${FUNCTION_DIR}
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PYTHONIOENCODING="utf8"
ENV MODEL_PATH="${FUNCTION_DIR}/model/"

ENTRYPOINT [ "python3", "-m", "awslambdaric" ]
CMD [ "super_resolution_app.handler" ]