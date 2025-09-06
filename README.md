# Stack-1 FastAPI

FastAPI + Docker + Postgres (dev-compose with auto-reload).  
Learning path: API → Docker → DB → Vault → 12-Factor → Kubernetes.

## Run (dev)
```bash
docker compose up --build
# open http://localhost:8000/docs

Endpoints

GET /health

POST /tasks (title, description)

GET /tasks

GET /tasks/{id}

POST /tasks/{id}/toggle

DELETE /tasks/{id}