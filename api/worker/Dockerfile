FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace/api/worker

COPY shared /workspace/shared
COPY api/worker /workspace/api/worker

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD ["celery", "-A", "worker_app.celery_app", "worker", "--loglevel=INFO"]
