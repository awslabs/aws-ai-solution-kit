FROM public.ecr.aws/lambda/python:3.9

ARG FUNCTION_DIR="/opt/program"
ARG MODEL_URL="https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/porn-image-model"
ARG MODEL_VERSION="v1.0.0"

ADD / ${FUNCTION_DIR}/

RUN pip3 install -i https://mirrors.aliyun.com/pypi/simple/ -r ${FUNCTION_DIR}/requirements.txt
RUN pip3 install -i https://mirrors.aliyun.com/pypi/simple/ --target ${FUNCTION_DIR} awslambdaric

RUN mkdir -p ${FUNCTION_DIR}/model/advanced
RUN yum install -y wget
RUN wget -c ${MODEL_URL}/${MODEL_VERSION}/resnest50_fast_4s2x40d.mapping -O ${FUNCTION_DIR}/model/resnest50_fast_4s2x40d.mapping
RUN wget -c ${MODEL_URL}/${MODEL_VERSION}/resnest50_fast_4s2x40d.bin -O ${FUNCTION_DIR}/model/resnest50_fast_4s2x40d.bin
RUN wget -c ${MODEL_URL}/${MODEL_VERSION}/resnest50_fast_4s2x40d.xml -O ${FUNCTION_DIR}/model/resnest50_fast_4s2x40d.xml

WORKDIR ${FUNCTION_DIR}
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PYTHONIOENCODING="utf8"
ENV MODEL_PATH="${FUNCTION_DIR}/model/"

ENTRYPOINT [ "python3", "-m", "awslambdaric" ]
CMD [ "image_detection_app.handler" ]