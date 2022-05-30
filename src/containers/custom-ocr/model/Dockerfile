FROM public.ecr.aws/lambda/python:3.9

ARG FUNCTION_DIR="/opt/program"
# Lite version
ARG MODEL_URL_OCR="https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/infer-ocr-model/standard"
ARG MODEL_VERSION_OCR="v1.0.0"
ARG MODEL_URL_CUSTOM="https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/custom-ocr"
ARG MODEL_VERSION_CUSTOM="1.2.0"

ADD / ${FUNCTION_DIR}/

RUN pip3 install -i https://mirrors.aliyun.com/pypi/simple/ -r ${FUNCTION_DIR}/requirements.txt
RUN pip3 install -i https://mirrors.aliyun.com/pypi/simple/ --target ${FUNCTION_DIR} awslambdaric

RUN mkdir -p ${FUNCTION_DIR}/model
RUN yum install -y wget unzip
RUN wget -c $MODEL_URL_OCR/$MODEL_VERSION_OCR/classifier.onnx -O ${FUNCTION_DIR}/model/classifier.onnx
RUN wget -c $MODEL_URL_OCR/$MODEL_VERSION_OCR/det_standard.onnx -O ${FUNCTION_DIR}/model/det_standard.onnx
RUN wget -c $MODEL_URL_OCR/$MODEL_VERSION_OCR/keys_v1.txt -O ${FUNCTION_DIR}/model/keys_v1.txt
RUN wget -c $MODEL_URL_OCR/$MODEL_VERSION_OCR/rec_standard.onnx -O ${FUNCTION_DIR}/model/rec_standard.onnx
RUN wget -c $MODEL_URL_CUSTOM/$MODEL_VERSION_CUSTOM/custom_ocr.zip -O ${FUNCTION_DIR}/model/custom_ocr.zip
RUN unzip ${FUNCTION_DIR}/model/custom_ocr.zip -d ${FUNCTION_DIR}/model/

WORKDIR ${FUNCTION_DIR}
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PYTHONIOENCODING="utf8"
ENV MODEL_NAME="standard"
ENV MODEL_PATH="${FUNCTION_DIR}/model/"

ENTRYPOINT [ "python3", "-m", "awslambdaric" ]
CMD [ "custom_ocr_app.handler" ]