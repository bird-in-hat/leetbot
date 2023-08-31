FROM python:3.11-alpine3.17 as bot-base

WORKDIR /app

RUN addgroup -g 1010 -S app && adduser -u 1010 -S -D -G app app && \
    apk add --virtual .app-deps libxslt file ffmpeg
RUN apk add linux-headers nano

COPY --chown=app:app requirements.txt    ./

RUN pip install --upgrade pip wheel setuptools
RUN pip install -r requirements.txt

COPY --chown=app:app . .
