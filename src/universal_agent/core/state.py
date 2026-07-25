import operator
from typing import Annotated, Any, TypedDict


class AgentState(TypedDict):
    task_id: str
    goal: str
    workspace_id: str
    
    # Track status transitions
    status: str
    permission_tier: str
    
    plan: list[str]
    evidence: Annotated[list[dict[str, Any]], operator.add]
    
    # Used for loops
    repair_attempts: int
    worker: str | None
    current_action: str | None
    result: str | None
