import logging
from typing import Literal

from langgraph.graph import END, StateGraph

from .config import config
from .db import EvidenceRecord, TaskEvent, TaskStore
from .state import AgentState
from .workers.filesystem import FilesystemWorker
from .workers.shell import ShellWorker

logger = logging.getLogger(__name__)

def update_status(state: AgentState, new_status: str, reason: str = ""):
    TaskStore.add_event(TaskEvent(
        task_id=state["task_id"],
        status_from=state.get("status", "queued"),
        status_to=new_status,
        reason=reason
    ))
    state["status"] = new_status
    # Sync status to task record
    task = TaskStore.get_task(state["task_id"])
    if task:
        task.status = new_status
        task.plan = state.get("plan", [])
        task.result = state.get("result", "")
        TaskStore.update_task(task)
    return state

def normalize(state: AgentState) -> AgentState:
    logger.info(f"Normalize: {state['task_id']}")
    return update_status(state, "planning", "Normalization completed")

def plan(state: AgentState) -> AgentState:
    logger.info(f"Plan: {state['task_id']}")
    # Simple structured planner mockup
    plan_steps = ["Analyze goal", "Select worker", "Execute action"]
    state["plan"] = plan_steps
    return update_status(state, "policy_check", "Plan generated")

def policy(state: AgentState) -> AgentState:
    logger.info(f"Policy check: {state['task_id']}")
    # Evaluate risk
    # Default to workspace_write for MVP demo
    tier = "workspace_write"
    state["permission_tier"] = tier
    
    if tier in ["dangerous", "host_write"]:
        return update_status(state, "waiting_for_approval", f"Tier {tier} requires approval")
    
    return update_status(state, "executing", "Policy approved")

def route(state: AgentState) -> Literal["execute", "wait"]:
    if state["status"] == "waiting_for_approval":
        return "wait"
    return "execute"

def execute(state: AgentState) -> AgentState:
    logger.info(f"Execute: {state['task_id']}")
    worker_type = state.get("worker", "shell")
    result = {}
    
    # We execute a simple action if not specified
    if worker_type == "shell":
        ws_id = state.get("workspace_id") or state["task_id"]
        worker = ShellWorker(f"{config.workspaces_dir}/{ws_id}")
        cmd = state.get("current_action", "pwd").split()
        result = worker.execute(cmd)
    elif worker_type == "filesystem":
        ws_id = state.get("workspace_id") or state["task_id"]
        worker = FilesystemWorker(f"{config.workspaces_dir}/{ws_id}")
        result = worker.list_dir(".")
        
    ev = EvidenceRecord(
        task_id=state["task_id"],
        worker=worker_type,
        summary=f"Executed {state.get('current_action')}",
        exit_code=result.get("exit_code", 0),
        data=result
    )
    TaskStore.add_evidence(ev)
    
    state["evidence"] = [result]
    return update_status(state, "checking", "Action executed")

def collect_evidence(state: AgentState) -> AgentState:
    return update_status(state, "checking", "Evidence collected")

def critic(state: AgentState) -> AgentState:
    logger.info(f"Critic: {state['task_id']}")
    ev = state.get("evidence", [])
    if not ev:
        state["repair_attempts"] = state.get("repair_attempts", 0) + 1
        return update_status(state, "repairing", "No evidence found")
        
    last_res = ev[-1]
    if last_res.get("status") == "error" or last_res.get("exit_code", 0) != 0:
        state["repair_attempts"] = state.get("repair_attempts", 0) + 1
        return update_status(state, "repairing", "Action failed")
        
    return update_status(state, "succeeded", "Goal verified")

def verify(state: AgentState) -> AgentState:
    return state

def repair_route(state: AgentState) -> Literal["execute", "failed"]:
    if state.get("repair_attempts", 0) >= 3:
        update_status(state, "failed", "Repair budget exceeded")
        return "failed"
    update_status(state, "executing", "Retrying action")
    return "execute"

def create_graph(checkpointer=None):
    workflow = StateGraph(AgentState)
    
    workflow.add_node("normalize", normalize)
    workflow.add_node("plan", plan)
    workflow.add_node("policy", policy)
    workflow.add_node("execute", execute)
    workflow.add_node("collect_evidence", collect_evidence)
    workflow.add_node("critic", critic)
    workflow.add_node("verify", verify)

    workflow.set_entry_point("normalize")
    workflow.add_edge("normalize", "plan")
    workflow.add_edge("plan", "policy")
    
    workflow.add_conditional_edges("policy", route, {"execute": "execute", "wait": END})
    
    workflow.add_edge("execute", "collect_evidence")
    workflow.add_edge("collect_evidence", "critic")
    
    workflow.add_conditional_edges("critic", lambda s: "repair" if s["status"] == "repairing" else "verify", {
        "repair": "execute",
        "verify": "verify"
    })
    
    workflow.add_edge("verify", END)

    return workflow.compile(checkpointer=checkpointer)
