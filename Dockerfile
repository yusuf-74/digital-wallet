FROM python:3.12.10-slim

WORKDIR /app

COPY ./requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir