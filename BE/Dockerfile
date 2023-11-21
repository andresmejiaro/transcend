FROM python:3.7-alpine AS builder

EXPOSE 8000
WORKDIR /app

RUN apk add --no-cache bash

COPY server .

COPY django_project_setup.sh /app/django_project_setup.sh
RUN chmod +x /app/django_project_setup.sh

ENTRYPOINT [ "/app/django_project_setup.sh" ]

# CMD ["/bin/sh", "-c", "source /app/django_venv/bin/activate && python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000"]