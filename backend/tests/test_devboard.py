"""
Automated unit and integration test suite for DevBoard.
Tests GitHub sync worker, commit/PR tracking, CI/CD run aggregation, and DORA metrics calculations.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Setup sys.path for standalone backend execution
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from shared.python.database import Base
from app.main import app
from app.api.routes import get_db
from app.models.schemas import (
    CommitRecord,
    DeploymentRecord,
    PullRequestRecord,
    Repository,
    WorkflowRunRecord,
)
from app.services.metrics_engine import metrics_engine

TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    now = datetime.now(timezone.utc)

    repo = Repository(
        id="repo-test",
        full_name="logiclegend/test-service",
        name="test-service",
        default_branch="main",
    )
    db.add(repo)

    # Add test commits
    for i in range(10):
        db.add(CommitRecord(
            id=f"c-{i}",
            repo_id=repo.id,
            sha=f"sha{i:05d}",
            author_name="Alice Dev",
            author_email="alice@campus.edu",
            message=f"commit {i}",
            committed_at=now - timedelta(days=i),
        ))

    # Add test PRs
    for i in range(4):
        db.add(PullRequestRecord(
            id=f"pr-{i}",
            repo_id=repo.id,
            number=i + 1,
            title=f"PR {i}",
            author="Alice Dev",
            state="merged",
            opened_at=now - timedelta(days=i + 2),
            merged_at=now - timedelta(days=i + 1),
            review_time_hours=12.0 + (i * 2),
        ))

    # Add workflow runs (8 success, 2 failure = 80%)
    for i in range(10):
        db.add(WorkflowRunRecord(
            id=f"wf-{i}",
            repo_id=repo.id,
            workflow_name="CI Test",
            run_number=i + 1,
            branch="main",
            status="completed",
            conclusion="success" if i < 8 else "failure",
            duration_seconds=120,
            run_started_at=now - timedelta(hours=i * 6),
        ))

    # Add deployment
    db.add(DeploymentRecord(
        id="dep-1",
        repo_id=repo.id,
        environment="production",
        status="SUCCESS",
        deployed_by="Actions CD",
        deployed_at=now - timedelta(days=1),
    ))

    db.commit()
    yield
    db.close()
    Base.metadata.drop_all(bind=test_engine)


def test_health_endpoint():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
    assert resp.json()["service"] == "devboard"


def test_root_serves_frontend():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    # Returns HTML containing DevBoard title or fallback status
    assert "DevBoard" in resp.text or resp.json().get("service") == "devboard"



def test_connect_repository():
    client = TestClient(app)
    resp = client.post("/api/v1/devboard/repositories", json={"full_name": "org/new-repo"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["full_name"] == "org/new-repo"
    assert data["name"] == "new-repo"


def test_query_commits_and_prs():
    client = TestClient(app)
    commits_resp = client.get("/api/v1/devboard/commits?repo_id=repo-test")
    assert commits_resp.status_code == 200
    assert len(commits_resp.json()) >= 10

    prs_resp = client.get("/api/v1/devboard/pull-requests?repo_id=repo-test")
    assert prs_resp.status_code == 200
    assert len(prs_resp.json()) == 4


def test_engineering_metrics_calculation():
    db = TestingSessionLocal()
    metrics = metrics_engine.compute_metrics(db, repo_id="repo-test")
    db.close()

    assert metrics.build_success_rate_percent == 80.0
    assert metrics.average_pr_cycle_time_hours > 10.0
    assert "lead_time_for_changes" in metrics.metric_definitions
    assert "commit_frequency_weekly" in metrics.metric_definitions
    assert metrics.dora.change_failure_rate_percent == 3.8


def test_record_details_and_health_status():
    client = TestClient(app)
    # Test single repo detail
    repo_resp = client.get("/api/v1/devboard/repositories/repo-test")
    assert repo_resp.status_code == 200
    assert repo_resp.json()["name"] == "test-service"

    # Test single PR detail
    pr_resp = client.get("/api/v1/devboard/pull-requests/pr-0")
    assert pr_resp.status_code == 200
    assert pr_resp.json()["number"] == 1

    # Test single workflow run detail
    wf_resp = client.get("/api/v1/devboard/workflows/wf-0")
    assert wf_resp.status_code == 200
    assert wf_resp.json()["workflow_name"] == "CI Test"

    # Test single deployment detail
    dep_resp = client.get("/api/v1/devboard/deployments/dep-1")
    assert dep_resp.status_code == 200
    assert dep_resp.json()["environment"] == "production"

    # Test diagnostic health endpoint
    health_resp = client.get("/api/v1/devboard/health/status")
    assert health_resp.status_code == 200
    assert health_resp.json()["status"] == "healthy"
    assert "services" in health_resp.json()
    assert health_resp.json()["services"]["database"]["status"] == "healthy"

