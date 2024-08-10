FROM python:3.11.8-slim-bullseye AS build

ENV DOCKER_HOME=/docker_home

WORKDIR $DOCKER_HOME

COPY requirements.txt .
RUN pip install -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple

COPY . .

EXPOSE 8000

ENTRYPOINT uvicorn myblog:app --log-config=log_conf.yaml --host 0.0.0.0
