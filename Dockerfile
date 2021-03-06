FROM python:3.8-alpine

WORKDIR /code
VOLUME /db /records /logs

ENV DB_URL sqlite:///db/db.sqlite3
ENV DATA_PATH /
ENV LOG_PATH /logs

CMD ["python", "-m", "app"]

RUN apk add --update --no-cache fuse ffmpeg \
    --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ --allow-untrusted

COPY requirements.txt /requirements.txt
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        build-base python3-dev libffi-dev coreutils openssl-dev && \
    pip install --no-cache-dir -r /requirements.txt && \
    apk del .tmp-build-deps

COPY . /code

ARG COMMIT
ENV RELEASE=$COMMIT
