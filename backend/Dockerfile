FROM python:3.7-alpine AS builder

EXPOSE 8000
WORKDIR /app

RUN apk add --no-cache bash \
    && apk add --no-cache --virtual .build-deps \
        build-base \
        jpeg-dev \
        zlib-dev

COPY server .

COPY requirements.txt .

COPY django_project_setup.sh /app/django_project_setup.sh
COPY wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/django_project_setup.sh
RUN chmod +x /app/wait-for-it.sh

ENTRYPOINT [ "/app/django_project_setup.sh" ]