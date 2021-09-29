ARG REGISTRY_URI
FROM ${REGISTRY_URI}

RUN pip3 install --no-cache numpy \
    flask \
    gevent \
    base64image
# Set up the program in the image

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE

RUN mkdir -p /opt/ml/model
ENV PATH="/opt/ml/model:${PATH}"

COPY model /opt/ml/model
WORKDIR /opt/ml/model
RUN chmod +x /opt/ml/model/entrypoint.sh
ENTRYPOINT ["/opt/ml/model/entrypoint.sh"]