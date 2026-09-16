"""
REST API routes for DevBoard.
Endpoints for repositories, commits, pull requests, CI/CD runs, deployments, and DORA metrics.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..models.schemas import (
    CommitRecord,
    DeploymentRecord,
    EngineeringMetricsSummary,
    PullRequestRecord,
    Repository,
    RepositoryConnectRequest,
    WorkflowRunRecord,
)
from ..services.github_client import github_client
from ..services.metrics_engine import metrics_engine

router = APIRouter(prefix="/api/v1/devboard", tags=["DevBoard"])


def get_db():
    from ..main import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------------------------------------------
# Repositories & Sync
# -------------------------------------------------------------
@router.get("/repositories")
def list_repositories(db: Session = Depends(get_db)):
    return db.query(Repository).order_by(Repository.full_name).all()


@router.post("/repositories", status_code=status.HTTP_201_CREATED)
def connect_repository(payload: RepositoryConnectRequest, db: Session = Depends(get_db)):
    existing = db.query(Repository).filter(Repository.full_name == payload.full_name).first()
    if existing:
        return existing

    repo_name = payload.full_name.split("/")[-1]
    repo_id = f"repo-{repo_name.lower().replace('.', '-')}"
    new_repo = Repository(
        id=repo_id,
        full_name=payload.full_name,
        name=repo_name,
        description=f"Tracked engineering codebase {payload.full_name}",
        default_branch="main",
    )
    db.add(new_repo)
    db.flush()

    # Trigger initial simulated sync
    activity = github_client.generate_simulated_activity(new_repo)
    db.add_all(activity["commits"])
    db.add_all(activity["pull_requests"])
    db.add_all(activity["workflow_runs"])
    db.add_all(activity["deployments"])

    db.commit()
    db.refresh(new_repo)
    return new_repo


@router.post("/repositories/{repo_id}/sync")
def sync_repository(repo_id: str, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    activity = github_client.generate_simulated_activity(repo)
    # Add new commits / runs
    for c in activity["commits"][:3]:
        db.merge(c)
    for r in activity["workflow_runs"][:2]:
        db.merge(r)

    db.commit()
    return {"status": "synced", "repository": repo.full_name}


# -------------------------------------------------------------
# Commits & Pull Requests
# -------------------------------------------------------------
@router.get("/commits")
def list_commits(repo_id: Optional[str] = None, limit: int = Query(30, le=100), db: Session = Depends(get_db)):
    query = db.query(CommitRecord)
    if repo_id:
        query = query.filter(CommitRecord.repo_id == repo_id)
    return query.order_by(CommitRecord.committed_at.desc()).limit(limit).all()


@router.get("/pull-requests")
def list_pull_requests(repo_id: Optional[str] = None, state: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(PullRequestRecord)
    if repo_id:
        query = query.filter(PullRequestRecord.repo_id == repo_id)
    if state:
        query = query.filter(PullRequestRecord.state == state)
    return query.order_by(PullRequestRecord.opened_at.desc()).all()


# -------------------------------------------------------------
# CI/CD Workflows & Deployments
# -------------------------------------------------------------
@router.get("/workflows")
def list_workflows(repo_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(WorkflowRunRecord)
    if repo_id:
        query = query.filter(WorkflowRunRecord.repo_id == repo_id)
    return query.order_by(WorkflowRunRecord.run_started_at.desc()).limit(25).all()


@router.get("/deployments")
def list_deployments(repo_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(DeploymentRecord)
    if repo_id:
        query = query.filter(DeploymentRecord.repo_id == repo_id)
    return query.order_by(DeploymentRecord.deployed_at.desc()).all()


# -------------------------------------------------------------
# Engineering & DORA Metrics
# -------------------------------------------------------------
@router.get("/metrics", response_model=EngineeringMetricsSummary)
def get_engineering_metrics(repo_id: Optional[str] = None, db: Session = Depends(get_db)):
    return metrics_engine.compute_metrics(db, repo_id=repo_id)
