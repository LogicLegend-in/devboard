"""
Main FastAPI application for DevBoard.
Initializes database, seeds monitored repositories with commit/PR/CI histories,
and exposes engineering observability metrics.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from shared.python.database import get_db_engine, create_session_factory, Base
from shared.python.logging_config import configure_logger
from .models.schemas import Repository
from .api.routes import router as devboard_router
from .services.github_client import github_client

logger = configure_logger("devboard-service")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./devboard.db")
engine = get_db_engine(DATABASE_URL, service_name="devboard")
SessionLocal = create_session_factory(engine)


def seed_database(db: Session):
    if db.query(Repository).count() > 0:
        return

    logger.info("Seeding DevBoard with tracked repositories, CI/CD pipelines, and engineering commits...")

    sample_repos = [
        ("repo-iot-sentinel", "logiclegend/iot-sentinel", "iot-sentinel", "Real-time IoT device monitoring & anomaly detection"),
        ("repo-campusml", "logiclegend/campusml", "campusml", "Institutional machine learning & timetable operations"),
        ("repo-openapi-hub", "logiclegend/openapi-hub", "openapi-hub", "Developer API testing sandbox & OpenAPI spec repository"),
        ("repo-core-platform", "logiclegend/production-platform", "production-platform", "Ecosystem microservices, shared auth, and k8s infrastructure"),
    ]

    for r_id, full_name, name, desc in sample_repos:
        repo = Repository(
            id=r_id,
            full_name=full_name,
            name=name,
            description=desc,
            default_branch="main",
            open_issues_count=4,
            stars_count=142,
            forks_count=28,
        )
        db.add(repo)
        db.flush()

        activity = github_client.generate_simulated_activity(repo)
        db.add_all(activity["commits"])
        db.add_all(activity["pull_requests"])
        db.add_all(activity["workflow_runs"])
        db.add_all(activity["deployments"])

    db.commit()
    logger.info("DevBoard seeded successfully.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="DevBoard Engineering Observability API",
    version="1.0.0",
    description="Unified developer productivity, GitHub activity, CI/CD observability, and DORA metrics platform.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(devboard_router)


@app.get("/health")
def health():
    return {"status": "healthy", "service": "devboard", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/ready")
def ready():
    return {"status": "ready", "service": "devboard"}


@app.get("/metrics")
def metrics():
    return (
        "# HELP devboard_repositories_tracked Tracked software engineering repositories\n"
        "# TYPE devboard_repositories_tracked gauge\n"
        "devboard_repositories_tracked 4\n"
        "# HELP devboard_workflow_runs_total Monitored CI/CD pipeline runs\n"
        "# TYPE devboard_workflow_runs_total counter\n"
        "devboard_workflow_runs_total 72\n"
    )
