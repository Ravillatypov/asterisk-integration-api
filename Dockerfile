FROM python:3.8-alpine

WORKDIR /code
RUN mkdir /db
ENV DB_URL sqlite:///db/db.sqlite3
ENV AMI_LOG_PATH /db/ami.log

RUN apk add --update --no-cache fuse \
    --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ --allow-untrusted

COPY requirements.txt /requirements.txt
RUN apk add --update --no-cache --virtual .tmp-build-deps build-base python3-dev libffi-dev &&\
    pip install --no-cache-dir --no-use-pep517 -r /requirements.txt && \
    apk del .tmp-build-deps

COPY . /code

CMD ["python", "main.py"]
