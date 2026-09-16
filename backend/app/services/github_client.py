"""
GitHub Sync Worker and High-Fidelity Activity Simulator for DevBoard.
Syncs real GitHub repository activity or generates realistic developer workflow events.
"""

from datetime import datetime, timedelta, timezone
import os
import random
import uuid
from typing import Dict, List, Optional
import httpx

from ..models.schemas import (
    CommitRecord,
    DeploymentRecord,
    PullRequestRecord,
    Repository,
    WorkflowRunRecord,
)


class GitHubSyncClient:
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.api_base = "https://api.github.com"

    async def fetch_real_repo(self, full_name: str) -> Optional[Dict]:
        """Queries live GitHub REST API if credentials are configured."""
        if not self.github_token:
            return None
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.get(f"{self.api_base}/repos/{full_name}", headers=headers)
                if res.status_code == 200:
                    return res.json()
            except Exception:
                pass
        return None

    def generate_simulated_activity(self, repo: Repository) -> Dict[str, List]:
        """
        Generates realistic commit history, pull request lifecycle, and CI/CD workflow runs.
        Used for development and when external GitHub credentials are not supplied.
        """
        now = datetime.now(timezone.utc)
        random.seed(hash(repo.id) % 100000)

        # 1. Commits
        authors = [
            ("Alex Rivera", "alex.rivera@campus.edu"),
            ("Maya Patel", "maya.patel@campus.edu"),
            ("Liam Chen", "liam.chen@campus.edu"),
            ("Sophia Taylor", "sophia.t@campus.edu"),
        ]
        commit_msgs = [
            "feat: add distributed stream ingestion pipeline",
            "fix: resolve race condition in websocket hub",
            "perf: optimize room allocation constraint solver",
            "refactor: extract shared security authentication middleware",
            "test: add isolation forest anomaly unit tests",
            "docs: update API documentation and deployment guides",
            "ci: add security SAST scanning workflow",
            "feat: implement SSRF private IP validation",
        ]

        commits = []
        for i in range(25):
            author_name, author_email = authors[i % len(authors)]
            c_time = now - timedelta(hours=(25 - i) * 6 + random.randint(0, 180))
            sha = f"c{uuid.uuid4().hex[:7]}"
            commits.append(CommitRecord(
                id=f"commit-{sha}",
                repo_id=repo.id,
                sha=sha,
                author_name=author_name,
                author_email=author_email,
                message=commit_msgs[i % len(commit_msgs)],
                committed_at=c_time,
            ))

        # 2. Pull Requests
        pr_titles = [
            "feat: MQTT telemetry batch ingestion",
            "fix: correct rolling z-score floor calculation",
            "refactor: improve timetable constraint optimization",
            "security: enforce SSRF IP range filtering on proxy",
            "feat: add DORA metrics tracking to DevBoard",
        ]
        pull_requests = []
        for i, title in enumerate(pr_titles):
            author_name, _ = authors[i % len(authors)]
            open_time = now - timedelta(days=(5 - i) * 2 + 1)
            merged_time = open_time + timedelta(hours=random.randint(4, 36))
            review_hours = round((merged_time - open_time).total_seconds() / 3600.0, 1)

            state = "merged" if i < 4 else "open"
            pull_requests.append(PullRequestRecord(
                id=f"pr-{repo.id}-{i+101}",
                repo_id=repo.id,
                number=i + 101,
                title=title,
                author=author_name,
                state=state,
                opened_at=open_time,
                merged_at=merged_time if state == "merged" else None,
                review_time_hours=review_hours if state == "merged" else None,
                additions=random.randint(40, 600),
                deletions=random.randint(10, 150),
            ))

        # 3. CI/CD Workflow Runs
        workflows = ["CI Test Suite", "Docker Container Build", "Security Audit Scan"]
        workflow_runs = []
        run_num = 100
        for i in range(18):
            run_num += 1
            wf_name = workflows[i % len(workflows)]
            run_time = now - timedelta(hours=(18 - i) * 8)
            # 90% build success rate
            conclusion = "success" if random.random() > 0.10 else "failure"
            duration = random.randint(65, 240)
            workflow_runs.append(WorkflowRunRecord(
                id=f"run-{repo.id}-{run_num}",
                repo_id=repo.id,
                workflow_name=wf_name,
                run_number=run_num,
                branch="main",
                status="completed",
                conclusion=conclusion,
                duration_seconds=duration,
                run_started_at=run_time,
            ))

        # 4. Deployments
        deployments = []
        for i in range(6):
            dep_time = now - timedelta(days=(6 - i) * 2)
            deployments.append(DeploymentRecord(
                id=f"dep-{repo.id}-{i+1}",
                repo_id=repo.id,
                environment="production" if i % 2 == 0 else "staging",
                status="SUCCESS",
                deployed_by="GitHub Actions CD",
                commit_sha=commits[i].sha if i < len(commits) else "a1b2c3d",
                deployed_at=dep_time,
            ))

        return {
            "commits": commits,
            "pull_requests": pull_requests,
            "workflow_runs": workflow_runs,
            "deployments": deployments,
        }


github_client = GitHubSyncClient()
