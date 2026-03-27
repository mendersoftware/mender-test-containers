FROM python:3.13-alpine

RUN apk add --no-cache git curl bash gcc musl-dev

COPY requirements_py3.txt .

RUN pip3 install -r requirements_py3.txt
