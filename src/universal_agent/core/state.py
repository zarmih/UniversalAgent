import operator
from typing import Annotated, Any, TypedDict


class AgentState(TypedDict):
    task_id: str
    goal: str
    status: str # queued, planning, waiting_for_approval, executing, checking, repairing, blocked, succeeded, failed, cancelled
    plan: list[str]
    current_step: int
    evidence: list[dict[str, Any]]
    errors: list[str]
    # Reducers for parallel modifications
    messages: Annotated[list[dict[str, Any]], operator.add]
