FROM public.ecr.aws/lambda/python:3.9

ARG FUNCTION_DIR="/opt/program"
ARG MODEL_URL="https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/text-similarity"
ARG MODEL_VERSION="1.2.0"

ADD / ${FUNCTION_DIR}/

RUN pip3 install -i https://mirrors.aliyun.com/pypi/simple/ -r ${FUNCTION_DIR}/requirements.txt
RUN pip3 install -i https://mirrors.aliyun.com/pypi/simple/ --target ${FUNCTION_DIR} awslambdaric

RUN mkdir -p ${FUNCTION_DIR}/model/
RUN yum install -y wget unzip
RUN wget -c ${MODEL_URL}/${MODEL_VERSION}/CoSENT.zip -O ${FUNCTION_DIR}/model/CoSENT.zip
RUN wget -c ${MODEL_URL}/${MODEL_VERSION}/tokenizer.zip -O ${FUNCTION_DIR}/model/tokenizer.zip
RUN unzip ${FUNCTION_DIR}/model/CoSENT.zip -d ${FUNCTION_DIR}/model/
RUN unzip ${FUNCTION_DIR}/model/tokenizer.zip -d ${FUNCTION_DIR}/model/

WORKDIR ${FUNCTION_DIR}
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PYTHONIOENCODING="utf8"
ENV MODEL_PATH="${FUNCTION_DIR}/model/"

ENTRYPOINT [ "python3", "-m", "awslambdaric" ]
CMD [ "text_similarity_app.handler" ]