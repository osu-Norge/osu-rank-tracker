FROM python:3.7-alpine3.9

LABEL maintainer="Roxedus"

ENV docker=True

COPY / /app

RUN \
    apk add --no-cache --virtual=build-dependencies  --update gcc musl-dev python3-dev linux-headers && \
    apk add --no-cache --virtual=runtime --update git

RUN python3 -m pip install -r /app/requirements.txt

RUN apk del build-dependencies

WORKDIR /app

CMD python3 /app/run.py