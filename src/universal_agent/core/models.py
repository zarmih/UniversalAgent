import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


def utcnow_iso():
    return datetime.now(UTC).isoformat()

class TaskCreate(BaseModel):
    goal: str
    workspace_id: str | None = None

class TaskStatus:
    QUEUED = "queued"
    PLANNING = "planning"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    EXECUTING = "executing"
    CHECKING = "checking"
    REPAIRING = "repairing"
    BLOCKED = "blocked"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PermissionTier:
    READ_ONLY = "read_only"
    WORKSPACE_WRITE = "workspace_write"
    HOST_WRITE = "host_write"
    DANGEROUS = "dangerous"

class TaskRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal: str
    status: str = TaskStatus.QUEUED
    permission_tier: str = PermissionTier.READ_ONLY
    created_at: str = Field(default_factory=utcnow_iso)
    updated_at: str = Field(default_factory=utcnow_iso)
    plan: list[str] = Field(default_factory=list)
    result: str | None = None

class TaskEvent(BaseModel):
    task_id: str
    status_from: str | None = None
    status_to: str
    reason: str | None = None
    timestamp: str = Field(default_factory=utcnow_iso)

class EvidenceRecord(BaseModel):
    task_id: str
    worker: str
    summary: str
    timestamp: str = Field(default_factory=utcnow_iso)
    exit_code: int | None = None
    data: dict[str, Any] = Field(default_factory=dict)

class ApprovalRequest(BaseModel):
    action: str # approve or deny
    reason: str | None = None
