# DevBoard Deployment Guide

This guide covers deploying **DevBoard** to cloud platforms and production servers. DevBoard is a self-contained fullstack application: FastAPI serves the REST API, DORA metrics engine, and the interactive frontend directly on a single port.

---

## Deployment Options at a Glance

| Platform | Difficulty | Database | Recommended For |
|---|:---:|---|---|
| [**Render**](#1-deploy-to-render-recommended) | Easy | SQLite / PostgreSQL | Free tier, 1-click Git deploy |
| [**Railway**](#2-deploy-to-railway) | Easy | SQLite / PostgreSQL | Automated branch previews |
| [**Fly.io**](#3-deploy-to-flyio) | Moderate | SQLite / PostgreSQL | Global edge deployment |
| [**Docker / VPS**](#4-deploy-with-docker--vps) | Moderate | SQLite / PostgreSQL | DigitalOcean, Hetzner, AWS EC2 |

---

## 1. Deploy to Render (Recommended)

Render offers a free tier for web services and natively supports Docker or Python runtimes.

### Option A: 1-Click Blueprint (`render.yaml`)
1. Fork or push this repository to GitHub.
2. Sign in to [Render](https://render.com).
3. Navigate to **Blueprints** → **New Blueprint Instance**.
4. Select `LogicLegend-in/devboard` (or your fork).
5. Render will automatically read [`render.yaml`](./render.yaml), provision the service, and deploy!

### Option B: Manual Web Service
1. In Render, click **New +** → **Web Service**.
2. Connect your GitHub repository: `LogicLegend-in/devboard`.
3. Choose **Docker** as the Runtime (or **Python 3** with build command `pip install -r backend/requirements.txt` and start command `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`).
4. Set the following environment variables:
   - `PORT`: `8004` (or let Render set `$PORT` automatically)
   - `ENVIRONMENT`: `production`
   - `CORS_ORIGINS`: `*`
   - *(Optional)* `GITHUB_TOKEN`: Your GitHub personal access token
5. Click **Create Web Service**. Once built, your DevBoard dashboard is live at `https://your-service.onrender.com/`.

---

## 2. Deploy to Railway

Railway detects the Dockerfile automatically and provisions SSL.

1. Go to [Railway.app](https://railway.app) and click **New Project**.
2. Select **Deploy from GitHub repo** → pick `devboard`.
3. Under **Variables**, configure:
   - `PORT`: `8004`
   - `ENVIRONMENT`: `production`
   - `CORS_ORIGINS`: `*`
   - *(Optional)* Add a Railway PostgreSQL plugin and reference `${{Postgres.DATABASE_URL}}` in `DATABASE_URL`.
4. Click **Deploy**. Under **Settings** → **Networking**, click **Generate Domain** to get your public HTTPS URL.

---

## 3. Deploy to Fly.io

Fly.io runs Docker containers near your users on global edge machines.

1. Install the Fly CLI:
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```
2. Log in:
   ```bash
   fly auth login
   ```
3. Initialize and deploy:
   ```bash
   fly launch --no-deploy
   fly deploy
   ```
4. Open the deployed application:
   ```bash
   fly open
   ```

---

## 4. Deploy with Docker & VPS (Self-Hosted)

For DigitalOcean Droplets, AWS EC2, Hetzner, or any Linux server:

### A. Single-Container (SQLite Storage)
```bash
# Clone repository
git clone https://github.com/LogicLegend-in/devboard.git
cd devboard

# Start container with volume persistence
docker compose up -d --build
```
DevBoard is now running at `http://YOUR_SERVER_IP:8004`.

### B. Production Multi-Container with PostgreSQL 16
```bash
docker compose -f docker-compose.prod.yml up -d --build
```
This runs PostgreSQL 16 in a private network alongside DevBoard with automated schema generation, healthchecks, and data persistence.

---

## 5. Connecting a Production Database

DevBoard is built with SQLAlchemy 2.0 and supports:
- **SQLite** (default, requires zero setup, ideal for testing and single-instance deployments):
  ```env
  DATABASE_URL=sqlite:///./data/devboard.db
  ```
- **PostgreSQL / Supabase / Neon / AWS RDS / Render Postgres**:
  ```env
  DATABASE_URL=postgresql://user:password@hostname:5432/dbname
  ```

> [!NOTE]
> DevBoard automatically converts legacy `postgres://` URLs (used by Render and Heroku) to modern `postgresql://` connection strings for SQLAlchemy 2.0.

---

## 6. Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8004` | Listening HTTP port (automatically injected by cloud platforms) |
| `HOST` | `0.0.0.0` | Binding interface IP |
| `ENVIRONMENT` | `production` | Environment mode (`development` or `production`) |
| `DATABASE_URL` | `sqlite:///./devboard.db` | SQLAlchemy connection string |
| `CORS_ORIGINS` | `*` | Allowed CORS origins (e.g. `https://devboard.logiclegend.in`) |
| `GITHUB_TOKEN` | *(empty)* | Optional GitHub Personal Access Token for live repository data sync |
| `WORKERS` | `2` | Number of Uvicorn worker processes |
| `DB_POOL_SIZE` | `10` | SQLAlchemy connection pool size (PostgreSQL) |
| `DB_MAX_OVERFLOW`| `20` | SQLAlchemy connection pool max overflow (PostgreSQL) |

---

## 7. Health & Monitoring Endpoints

- **Live Application**: `GET /` (Interactive Dark-Mode Dashboard)
- **Health Probe**: `GET /health` (Returns HTTP 200 `{"status": "healthy", "service": "devboard"}`)
- **Readiness Probe**: `GET /ready` (Returns HTTP 200 `{"status": "ready"}`)
- **Prometheus Metrics**: `GET /metrics` (Prometheus-compatible gauge & counter exposition)
- **Interactive Swagger Docs**: `GET /docs`
