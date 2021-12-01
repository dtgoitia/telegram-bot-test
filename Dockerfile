FROM python:3.9.5-slim-buster

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# COPY ./requirements/prod.txt /requirements/prod.txt
COPY ./requirements/dev.txt /requirements/dev.txt
RUN pip install --no-cache-dir -r /requirements/dev.txt \
    && rm -rf /requirements
