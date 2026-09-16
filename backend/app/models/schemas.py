"""
Database models and Pydantic schemas for DevBoard.
Handles Repositories, Commits, Pull Requests, CI/CD Workflows, Deployments, and DORA Engineering Metrics.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict, Field

from shared.python.database import Base, TimestampMixin


class PrState(str, Enum):
    OPEN = "open"
    MERGED = "merged"
    CLOSED = "closed"


class WorkflowConclusion(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


# -------------------------------------------------------------
# SQLAlchemy Models
# -------------------------------------------------------------
class Repository(Base, TimestampMixin):
    __tablename__ = "devboard_repositories"

    id = Column(String(64), primary_key=True)
    full_name = Column(String(120), unique=True, nullable=False, index=True)
    name = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    default_branch = Column(String(32), default="main")
    open_issues_count = Column(Integer, default=0)
    stars_count = Column(Integer, default=0)
    forks_count = Column(Integer, default=0)
    last_synced_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    commits = relationship("CommitRecord", back_populates="repository", cascade="all, delete-orphan")
    pull_requests = relationship("PullRequestRecord", back_populates="repository", cascade="all, delete-orphan")
    workflow_runs = relationship("WorkflowRunRecord", back_populates="repository", cascade="all, delete-orphan")
    deployments = relationship("DeploymentRecord", back_populates="repository", cascade="all, delete-orphan")


class CommitRecord(Base):
    __tablename__ = "devboard_commits"

    id = Column(String(64), primary_key=True)
    repo_id = Column(String(64), ForeignKey("devboard_repositories.id"), nullable=False, index=True)
    sha = Column(String(40), nullable=False, index=True)
    author_name = Column(String(100), nullable=False)
    author_email = Column(String(120), nullable=False)
    message = Column(Text, nullable=False)
    committed_at = Column(DateTime, nullable=False, index=True)

    repository = relationship("Repository", back_populates="commits")


class PullRequestRecord(Base, TimestampMixin):
    __tablename__ = "devboard_pull_requests"

    id = Column(String(64), primary_key=True)
    repo_id = Column(String(64), ForeignKey("devboard_repositories.id"), nullable=False, index=True)
    number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    state = Column(String(16), default=PrState.OPEN.value, index=True)
    opened_at = Column(DateTime, nullable=False)
    merged_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    review_time_hours = Column(Float, nullable=True)
    additions = Column(Integer, default=0)
    deletions = Column(Integer, default=0)

    repository = relationship("Repository", back_populates="pull_requests")


class WorkflowRunRecord(Base):
    __tablename__ = "devboard_workflow_runs"

    id = Column(String(64), primary_key=True)
    repo_id = Column(String(64), ForeignKey("devboard_repositories.id"), nullable=False, index=True)
    workflow_name = Column(String(100), nullable=False)
    run_number = Column(Integer, nullable=False)
    branch = Column(String(64), default="main")
    status = Column(String(32), default="completed")
    conclusion = Column(String(32), default=WorkflowConclusion.SUCCESS.value)
    duration_seconds = Column(Integer, default=120)
    run_started_at = Column(DateTime, nullable=False, index=True)

    repository = relationship("Repository", back_populates="workflow_runs")


class DeploymentRecord(Base, TimestampMixin):
    __tablename__ = "devboard_deployments"

    id = Column(String(64), primary_key=True)
    repo_id = Column(String(64), ForeignKey("devboard_repositories.id"), nullable=False, index=True)
    environment = Column(String(32), default="production", index=True)
    status = Column(String(32), default="SUCCESS")
    deployed_by = Column(String(100), default="GitHub Actions CD")
    commit_sha = Column(String(40), nullable=True)
    deployed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    repository = relationship("Repository", back_populates="deployments")


# -------------------------------------------------------------
# Pydantic Schemas
# -------------------------------------------------------------
class RepositoryConnectRequest(BaseModel):
    full_name: str
    github_token: Optional[str] = None


class DoraMetrics(BaseModel):
    deployment_frequency: str  # e.g. "3.2 / week"
    lead_time_for_changes_hours: float  # e.g. 14.5 hours
    change_failure_rate_percent: float  # e.g. 3.2%
    time_to_restore_service_hours: float  # e.g. 1.2 hours


class EngineeringMetricsSummary(BaseModel):
    commit_frequency_weekly: int
    pr_throughput_weekly: int
    average_pr_cycle_time_hours: float
    build_success_rate_percent: float
    deployments_total: int
    dora: DoraMetrics
    metric_definitions: Dict[str, str]
