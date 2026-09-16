# DevBoard — Unified Engineering Productivity & Observability Dashboard

[![LogicLegend](https://img.shields.io/badge/LogicLegend-Ecosystem-6366f1.svg)](https://github.com/LogicLegend-in)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/Tests-Passing%20(4%2F4)-success.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**DevBoard** is a unified developer productivity and engineering observability platform that aggregates Git repository activities, commit velocity, pull request cycles, and CI/CD build health into a single elegant interface.

Part of the [**LogicLegend.in**](https://github.com/LogicLegend-in) open-source technology ecosystem.

---

## Key Features

- **Engineering Velocity & KPIs**: Real-time aggregation of commit counts, active contributors, pull request cycle times, and deployment success frequencies.
- **CI/CD Pipeline Observability**: Live monitoring of automated builds, pipeline durations, failure triage, and branch status across multiple repositories.
- **Repository Health Scorecard**: Tracks codebase momentum, stale pull requests, review bottlenecks, and test coverage metrics.
- **Developer Experience First**: Glassmorphism dark UI with live data polling, SVG activity charts, and instant branch drill-downs.

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
│   │   └── main.py       # FastAPI application entrypoint
│   ├── tests/            # Automated test suite (4 tests passing)
│   ├── Dockerfile        # Container specification
│   └── requirements.txt  # Python dependencies
├── frontend/
│   └── index.html        # Interactive engineering dashboard
├── shared/               # Shared database, logging, auth & security handlers
├── docker-compose.yml    # Docker Compose deployment
└── README.md
```

---

## Quick Start

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

# Run backend (default: http://localhost:8004)
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8004 --reload
```

Open `frontend/index.html` in your browser to explore the dashboard.

### 2. Docker Setup

```bash
# Build and run with Docker Compose
docker compose up --build
```

Access Swagger API docs at `http://localhost:8004/docs`.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Healthcheck and readiness probe |
| `GET` | `/api/v1/devboard/metrics/summary` | High-level engineering KPIs & throughput stats |
| `GET` | `/api/v1/devboard/repos` | Monitored repositories and commit statistics |
| `GET` | `/api/v1/devboard/pipelines` | CI/CD pipeline history, statuses, and run times |
| `GET` | `/api/v1/devboard/pull-requests` | PR review velocity, lead times, and open review counts |

---

## Running Tests

```bash
python -m pytest backend/tests -v
```

---

## License

Distributed under the MIT License. Built with ❤️ by [LogicLegend](https://github.com/LogicLegend-in).
