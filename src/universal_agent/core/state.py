import sqlite3
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
import operator

class AgentState(TypedDict):
    task_id: str
    goal: str
    status: str # queued, planning, waiting_for_approval, executing, checking, repairing, blocked, succeeded, failed, cancelled
    plan: List[str]
    current_step: int
    evidence: List[Dict[str, Any]]
    errors: List[str]
    # Reducers for parallel modifications
    messages: Annotated[List[Dict[str, Any]], operator.add]
