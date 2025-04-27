FROM python:3.13-alpine3.20 as builder

WORKDIR /app


COPY requirements.txt .
RUN apk update && apk add --no-cache \
    postgresql-client \
    musl-dev && \
    pip install --user --no-cache-dir -r requirements.txt && \
    find /root/.local -name '*.pyc' -delete


FROM python:3.13-alpine3.20

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY web/app ./app
COPY web/project ./project
COPY web/manage.py ./


RUN find /usr/local -type d -name '__pycache__' -exec rm -rf {} + && \
    find /usr/local -type f -name '*.py[co]' -exec rm -f {} + && \
    find /app -name '__pycache__' -exec rm -rf {} + && \
    find /app -name '*.pyc' -delete && \
    rm -rf /var/cache/apk/* /tmp/*

ENV PATH=/root/.local/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPYCACHEPREFIX=/tmp/pycache

EXPOSE 8000
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]