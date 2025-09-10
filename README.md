


````markdown
# Stack-1 FastAPI

FastAPI → Docker → Postgres → Vault (dev) with a hot-reload dev loop.  
This repo is a learning scaffold that follows 12-Factor config (env-driven) and sets you up for the next steps (LLM/MCP, Kubernetes).

---

## 🧱 What’s inside

- **FastAPI** app (`app/`)
  - `main.py` – app factory & `/health`
  - `routers/tasks.py` – CRUD + `toggle`
  - `schemas.py` – Pydantic v2 models
  - `models.py` – SQLAlchemy 2.0 (`Mapped`, `mapped_column`)
  - `db.py` – SQLAlchemy engine/session. **Reads DB password from Vault** (falls back to `DB_PASSWORD` if needed).
  - `config.py` – `pydantic-settings` reads env vars (`.env` optional)
- **Docker / Compose**
  - `Dockerfile` – slim Python image
  - `docker-compose.yml` – runs **api**, **db (Postgres 16)**, **vault**
  - Named volume `pgdata` for DB persistence
  - Dev bind-mount `./app` with `uvicorn --reload` (instant reload)
- **Env**
  - `.env.example` (safe template)
  - `.gitignore` excludes `.env`, `venv/`, caches, etc.

---

## 🚀 Quick start (dev)

> Prereqs: Docker Desktop (WSL2 backend on Windows recommended), PowerShell.

```powershell
# from the project root
docker compose up --build
# open http://localhost:8000/docs
````

**Hot reload:** The API watches `./app` and restarts when you save files (no rebuild needed).
**Persistence:** Postgres data persists across restarts via the `pgdata` volume.

Stop:

```powershell
# Ctrl+C if attached
docker compose down     # removes containers (keeps volume/data)
# docker compose down -v   # ⚠️ also deletes the DB data volume
```

---

## 🔐 Vault (dev) – secrets for DB password

We run Vault **in dev mode** (in-memory). Secrets are lost when the container restarts.
The API fetches `POSTGRES_PASSWORD` from KV v2 at `secret/db-creds`.

### 1) Seed the secret (needed after Vault restarts)

**Option A – inside the container (recommended):**

```powershell
docker compose exec vault sh -lc ^
  "export VAULT_ADDR=http://127.0.0.1:8200 VAULT_TOKEN=dev-root-token; \
   vault kv put secret/db-creds POSTGRES_PASSWORD=changeme; \
   vault kv get secret/db-creds"
```

**Option B – from PowerShell:**

```powershell
$Headers = @{ "X-Vault-Token" = "dev-root-token" }
$Body = '{"data":{"POSTGRES_PASSWORD":"changeme"}}'
Invoke-RestMethod -Uri http://localhost:8200/v1/secret/data/db-creds `
  -Method Post -Headers $Headers -Body $Body -ContentType 'application/json'
```

Verify:

```powershell
(Invoke-RestMethod -Uri http://localhost:8200/v1/secret/data/db-creds -Headers $Headers -Method Get).data.data
# -> should show POSTGRES_PASSWORD = changeme
```

> If the API started before the secret existed, restart it so the engine picks up the password:
>
> ```powershell
> docker compose restart api
> ```

### (Optional) Auto-seed Vault on every `up`

Add a helper service to your `docker-compose.yml`:

```yaml
  vault-seed:
    image: curlimages/curl:8.7.1
    depends_on: [vault]
    command: >
      sh -c "
      until curl -sf http://vault:8200/v1/sys/health >/dev/null; do sleep 1; done;
      curl -s -H 'X-Vault-Token: dev-root-token' -H 'Content-Type: application/json'
           -d '{\"data\":{\"POSTGRES_PASSWORD\":\"changeme\"}}'
           http://vault:8200/v1/secret/data/db-creds && echo 'Seeded Vault';
      "
    restart: "no"
```

---

## ⚙️ Configuration (12-Factor)

All config via **environment variables** (no hard-coded settings).
`app/config.py` reads these (and more):

* `APP_NAME` (e.g., `Stack Task API`)
* `ENV`, `LOG_LEVEL`
* `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` *(API **prefers Vault** over this)*
* `VAULT_ADDR`, `VAULT_TOKEN`, `VAULT_DB_SECRET_PATH`

See `.env.example`. Keep real `.env` out of git.

---

## 🗄️ Database

* Image: `postgres:16`
* Compose sets:

  * `POSTGRES_DB=appdb`
  * `POSTGRES_USER=appuser`
  * `POSTGRES_PASSWORD=changeme` *(for the DB container itself)*
* API resolves the password from Vault (KV v2 `secret/db-creds`).

Inspect data:

```powershell
docker compose exec -e PGPASSWORD=changeme db `
  psql -U appuser -d appdb -c "SELECT id, title, done FROM tasks ORDER BY id DESC LIMIT 10;"
```

---

## 📡 API endpoints

Open Swagger: **[http://localhost:8000/docs](http://localhost:8000/docs)**

* `GET /health` → `{"status":"ok"}`
* `POST /tasks` – body: `{ "title": "...", "description": "..." }`
* `GET /tasks`
* `GET /tasks/{id}`
* `POST /tasks/{id}/toggle`
* `DELETE /tasks/{id}`

### PowerShell examples

```powershell
# create
$payload = @{ title = "vault test"; description = "hello" } | ConvertTo-Json
$new = Invoke-RestMethod -Uri http://localhost:8000/tasks -Method Post -ContentType 'application/json' -Body $payload

# list
Invoke-RestMethod -Uri http://localhost:8000/tasks

# toggle
Invoke-RestMethod -Uri ("http://localhost:8000/tasks/{0}/toggle" -f $new.id) -Method Post
```

### Use real curl on Windows (not the PowerShell alias)

```powershell
curl.exe -s -X POST http://localhost:8000/tasks `
  -H "Content-Type: application/json" `
  -d "{\"title\":\"vault test\",\"description\":\"hello\"}"
```

---

## 🧪 Dev loop

* Run detached, then tail logs:

  ```powershell
  docker compose up -d
  docker compose logs -f api
  ```
* Edit code in `app/` → **hot reload** restarts Uvicorn.
* Rebuild only when `requirements.txt` or `Dockerfile` changes:

  ```powershell
  docker compose up --build
  ```

---

## 🔍 Troubleshooting

* **`{"errors":[]}` when reading Vault secret**
  Dev Vault wipes on restart. Re-seed, then `docker compose restart api`.

* **API can’t connect to DB at boot**
  First run: Postgres needs a few seconds. Retry request or restart API.

* **Not sure which envs the API has**

  ```powershell
  docker compose exec api env | findstr /R "VAULT_ DB_"
  ```

* **Accidentally deleted the volume**
  If `GET /tasks` is empty after `down -v`, your DB was reset. Create tasks again.

---

## 🧭 Useful commands

```powershell
# services
docker compose ps
docker compose logs -f api
docker compose logs -f db
docker compose restart api

# DB shell
docker compose exec -e PGPASSWORD=changeme db psql -U appuser -d appdb

# clean up
docker compose down
# docker compose down -v   # ⚠️ nukes data volume

# image housekeeping
docker image ls
docker image rm <image-id>
```

---

## 📦 Project structure

```
stack-1-fastapi/
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ config.py
│  ├─ db.py
│  ├─ models.py
│  ├─ schemas.py
│  └─ routers/
│     ├─ __init__.py
│     └─ tasks.py
├─ requirements.txt
├─ .env.example
├─ .gitignore
├─ Dockerfile
├─ .dockerignore
└─ docker-compose.yml
```

---

## Run on Kubernetes (kind) with Vault

```powershell
# 1) Create kind cluster with host port mapping (30080 -> 8000)
kind create cluster --config k8s/kind.yaml --name stack1

# 2) Build and load API image into kind
docker build -t stack-1-fastapi:dev .
kind load docker-image stack-1-fastapi:dev --name stack1

# 3) Apply base manifests
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/config.yaml

# 4) Apply local secrets (NOT committed)
kubectl apply -f k8s/app-secrets.yaml

# 5) Vault + seed
kubectl apply -f k8s/vault.yaml
kubectl apply -f k8s/vault-seed.yaml
kubectl -n stack1 wait --for=condition=complete job/vault-seed --timeout=120s

# 6) Postgres + API
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/api.yaml
kubectl -n stack1 get pods -w
