FROM public.ecr.aws/lambda/python:3.9

ARG FUNCTION_DIR="/opt/ml/code/"
COPY requirements.txt ${FUNCTION_DIR}/requirements.txt
RUN python3.9 -m pip install -r ${FUNCTION_DIR}/requirements.txt

COPY main.py parser_factory.py ${FUNCTION_DIR}/
COPY parsers/ ${FUNCTION_DIR}/parsers/

ARG OCR_MODEL_URL="https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/infer-ocr-model/standard"
ARG OCR_MODEL_VERSION="v1.0.0"
ARG FD_MODEL_URL="https://aws-gcr-solutions-assets.s3.cn-northwest-1.amazonaws.com.cn/ai-solution-kit/face-detection"
ARG FD_MODEL_VERSION="1.2.0"

RUN yum install -y wget
RUN mkdir -p ${FUNCTION_DIR}/ocr_model
RUN wget -c $OCR_MODEL_URL/$OCR_MODEL_VERSION/classifier.onnx -O ${FUNCTION_DIR}/ocr_model/classifier.onnx
RUN wget -c $OCR_MODEL_URL/$OCR_MODEL_VERSION/det_standard.onnx -O ${FUNCTION_DIR}/ocr_model/det_standard.onnx
RUN wget -c $OCR_MODEL_URL/$OCR_MODEL_VERSION/keys_v1.txt -O ${FUNCTION_DIR}/ocr_model/keys_v1.txt
RUN wget -c $OCR_MODEL_URL/$OCR_MODEL_VERSION/rec_standard.onnx -O ${FUNCTION_DIR}/ocr_model/rec_standard.onnx
RUN mkdir -p ${FUNCTION_DIR}/fd_model
RUN wget -c ${FD_MODEL_URL}/${FD_MODEL_VERSION}/det.onnx -O ${FUNCTION_DIR}/fd_model/det.onnx

WORKDIR ${FUNCTION_DIR}

# Command can be overwritten by providing a different command in the template directly.
ENTRYPOINT ["python"]
