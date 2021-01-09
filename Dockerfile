FROM python:3.8-alpine

WORKDIR /code
VOLUME /db /records /logs
ENV DB_URL sqlite:///db/db.sqlite3
ENV AMI_LOG_PATH /db/ami.log
ENV DATA_PATH /

RUN apk add --update --no-cache fuse ffmpeg \
    --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ --allow-untrusted

COPY requirements.txt /requirements.txt
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        build-base python3-dev libffi-dev coreutils openssl-dev && \
    pip install --no-cache-dir -U pip cryptography && \
    pip install --no-cache-dir --no-use-pep517 -r /requirements.txt && \
    apk del .tmp-build-deps

COPY . /code

CMD ["python", "-m", "app"]
