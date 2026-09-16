# DevBoard — Unified Engineering Productivity & Observability Dashboard

[![LogicLegend](https://img.shields.io/badge/LogicLegend-Ecosystem-6366f1.svg)](https://github.com/LogicLegend-in)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](Dockerfile)
[![Deploy on Render](https://img.shields.io/badge/Deploy-Render-46E3B7.svg)](render.yaml)
[![Deploy on Railway](https://img.shields.io/badge/Deploy-Railway-0B0D0E.svg)](railway.json)
[![Tests](https://img.shields.io/badge/Tests-Passing%20(5%2F5)-success.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**DevBoard** is a unified developer productivity and engineering observability platform that aggregates Git repository activities, commit velocity, pull request cycles, and CI/CD build health into a single elegant interface.

Part of the [**LogicLegend.in**](https://github.com/LogicLegend-in) open-source technology ecosystem.

---

## Key Features

- **Self-Contained Fullstack Deployment**: FastAPI serves both the high-performance REST API and the interactive dashboard at root `/` on a single port.
- **Engineering Velocity & KPIs**: Real-time aggregation of commit counts, active contributors, pull request cycle times, and deployment success frequencies.
- **CI/CD Pipeline Observability**: Live monitoring of automated builds, pipeline durations, failure triage, and branch status across multiple repositories.
- **Repository Health Scorecard**: Tracks codebase momentum, stale pull requests, review bottlenecks, and test coverage metrics.
- **Production Database Ready**: Seamless zero-configuration SQLite for development/containers and automated connection pooling for production PostgreSQL (Supabase, Neon, AWS RDS, Render).
- **Cloud-Ready Infrastructure**: Includes native manifests for Render, Railway, Fly.io, and Docker Compose.

---

## Architecture

```
devboard/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI route handlers
│   │   ├── core/         # Settings & database configuration
│   │   ├── models/       # Schemas for repos, commits, PRs, and pipelines
│   │   ├── services/     # Observability aggregation & analytics services
│   │   └── main.py       # FastAPI application entrypoint (serves API + Frontend)
│   ├── tests/            # Automated test suite (5 tests passing)
│   ├── Dockerfile        # Container specification
│   └── requirements.txt  # Python dependencies with PostgreSQL support
├── frontend/
│   └── index.html        # Interactive engineering dashboard (dynamic API_BASE)
├── shared/               # Shared database, logging, auth & security handlers
├── .env.example          # Environment variables template
├── docker-compose.yml    # Single-container deployment with data volume
├── docker-compose.prod.yml # Production stack with PostgreSQL 16
├── render.yaml           # 1-Click Render Blueprint
├── railway.json          # Railway deployment config
├── fly.toml              # Fly.io edge deployment config
├── Procfile              # Heroku / Dokku / generic buildpack runner
├── DEPLOYMENT.md         # Comprehensive cloud deployment guide
└── README.md
```

---

## 🚀 Instant Cloud Deployment

Detailed step-by-step instructions for all platforms are available in [**DEPLOYMENT.md**](./DEPLOYMENT.md).

### 1. Deploy on Render
Connect this repository to [Render](https://render.com) using the included [`render.yaml`](./render.yaml) blueprint for a 1-click free-tier deployment.

### 2. Deploy on Railway
Click **Deploy from GitHub repo** on [Railway](https://railway.app). Railway will automatically detect the [`railway.json`](./railway.json) and [`Dockerfile`](./Dockerfile).

### 3. Deploy on Fly.io
```bash
fly launch
fly deploy
```

### 4. Deploy with Docker
```bash
# Standalone (SQLite)
docker compose up -d --build

# Production Stack (with PostgreSQL 16)
docker compose -f docker-compose.prod.yml up -d --build
```

---

## Quick Start (Local Development)

### 1. Local Setup

```bash
# Clone repository
git clone https://github.com/LogicLegend-in/devboard.git
cd devboard

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run server (default: http://localhost:8004)
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8004 --reload
```

Visit `http://localhost:8004` to view the DevBoard dashboard and `http://localhost:8004/docs` for the interactive Swagger API documentation.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | DevBoard interactive single-page dashboard |
| `GET` | `/health` | Healthcheck probe (`status: healthy`) |
| `GET` | `/ready` | Kubernetes/orchestrator readiness probe |
| `GET` | `/metrics` | Prometheus metrics exposition |
| `GET` | `/api/v1/devboard/metrics/summary` | Engineering velocity & throughput KPIs |
| `GET` | `/api/v1/devboard/repositories` | Monitored repositories and commit statistics |
| `GET` | `/api/v1/devboard/pipelines` | CI/CD pipeline history, statuses, and run times |
| `GET` | `/api/v1/devboard/pull-requests` | PR review velocity, lead times, and open review counts |
| `GET` | `/docs` | OpenAPI / Swagger interactive documentation |

---

## Running Tests

```bash
python -m pytest backend/tests -v
```

---

## License

Distributed under the MIT License. Built with ❤️ by [LogicLegend](https://github.com/LogicLegend-in).
