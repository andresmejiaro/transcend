FROM python:3.7-alpine AS builder

EXPOSE 8000
WORKDIR /app

RUN apk add --no-cache bash

COPY DjangoAPI .

# WORKDIR /app/DjangoAPI

COPY djangoscript.sh /app/djangoscript.sh
RUN chmod +x /app/djangoscript.sh

ENTRYPOINT [ "/app/djangoscript.sh" ]

# CMD ["/bin/sh", "-c", "source /app/django_venv/bin/activate && python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000"]