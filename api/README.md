# CreatorOS API Stack

This folder contains the backend runtime and orchestration files:

- `app/`: FastAPI application
- `worker/`: Celery worker
- `docker-compose.yml`: local MySQL + Redis + api + worker + web
- `.env` / `.env.example`: environment config for backend stack
- `Makefile`: local backend compose shortcuts

## Run backend stack

```bash
cd api
cp .env.example .env
docker compose up --build
```
