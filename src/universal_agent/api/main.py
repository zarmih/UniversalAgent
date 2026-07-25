import os
import sqlite3
import uuid

from fastapi import BackgroundTasks, FastAPI, HTTPException
from langgraph.checkpoint.sqlite import SqliteSaver
from pydantic import BaseModel

from ..core.config import config
from ..core.db import TaskStore, get_db
from ..core.graph import create_graph
from ..core.models import (
    ApprovalRequest,
    EvidenceRecord,
    TaskCreate,
    TaskEvent,
    TaskRecord,
)

app = FastAPI(title="Universal Agent API")

def get_graph():
    conn = sqlite3.connect(config.db_path, check_same_thread=False)
    return create_graph(SqliteSaver(conn))

@app.get("/health")
def health():
    # Check sqlite
    try:
        with get_db() as conn:
            conn.execute("SELECT 1")
    except Exception:
        raise HTTPException(status_code=500, detail="DB Error")
    return {"status": "ok", "version": "1.0.0"}

@app.post("/tasks", response_model=TaskRecord)
@app.post("/task", response_model=TaskRecord) # legacy
def create_task(req: TaskCreate):
    task = TaskRecord(
        id=str(uuid.uuid4()),
        goal=req.goal
    )
    TaskStore.create_task(task)
    TaskStore.add_event(TaskEvent(task_id=task.id, status_to="queued", reason="Task created"))
    return task

@app.get("/tasks", response_model=list[TaskRecord])
def list_tasks():
    return TaskStore.list_tasks()

@app.get("/tasks/{task_id}", response_model=TaskRecord)
def get_task(task_id: str):
    task = TaskStore.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/tasks/{task_id}/events", response_model=list[TaskEvent])
def get_task_events(task_id: str):
    return TaskStore.get_events(task_id)

@app.get("/tasks/{task_id}/evidence", response_model=list[EvidenceRecord])
def get_task_evidence(task_id: str):
    return TaskStore.get_evidence(task_id)

def run_task_background(task_id: str, workspace_id: str, goal: str):
    graph = get_graph()
    conf = {"configurable": {"thread_id": task_id}}
    state = {
        "task_id": task_id,
        "goal": goal,
        "workspace_id": workspace_id,
        "status": "queued",
        "permission_tier": "read_only",
        "repair_attempts": 0,
        "evidence": []
    }
    graph.invoke(state, config=conf)

@app.post("/tasks/{task_id}/run")
def run_task(task_id: str, background_tasks: BackgroundTasks):
    task = TaskStore.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status not in ["queued", "failed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Task not in runnable state")
    
    workspace_id = task.id
    os.makedirs(f"{config.workspaces_dir}/{workspace_id}", exist_ok=True)
    background_tasks.add_task(run_task_background, task.id, workspace_id, task.goal)
    return {"status": "started"}

@app.post("/tasks/{task_id}/approve")
def approve_task(task_id: str, background_tasks: BackgroundTasks):
    task = TaskStore.get_task(task_id)
    if not task or task.status != "waiting_for_approval":
        raise HTTPException(status_code=400, detail="Task not waiting for approval")
    
    TaskStore.add_event(TaskEvent(task_id=task_id, status_from=task.status, status_to="executing", reason="Approved by user"))
    task.status = "executing"
    TaskStore.update_task(task)
    
    # Resume graph
    def resume_graph(t_id):
        graph = get_graph()
        conf = {"configurable": {"thread_id": t_id}}
        graph.invoke({"status": "executing", "task_id": t_id}, config=conf)

    background_tasks.add_task(resume_graph, task.id)
    return {"status": "approved"}

@app.post("/tasks/{task_id}/deny")
def deny_task(task_id: str, req: ApprovalRequest):
    task = TaskStore.get_task(task_id)
    if not task or task.status != "waiting_for_approval":
        raise HTTPException(status_code=400, detail="Task not waiting for approval")
    
    TaskStore.add_event(TaskEvent(task_id=task_id, status_from=task.status, status_to="blocked", reason=req.reason or "Denied by user"))
    task.status = "blocked"
    TaskStore.update_task(task)
    return {"status": "denied"}

@app.post("/tasks/{task_id}/cancel")
def cancel_task(task_id: str):
    task = TaskStore.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    TaskStore.add_event(TaskEvent(task_id=task_id, status_from=task.status, status_to="cancelled", reason="Cancelled by user"))
    task.status = "cancelled"
    TaskStore.update_task(task)
    return {"status": "cancelled"}

@app.get("/agy/status")
def agy_status():
    adapter = AgyAdapter()
    return {"status": adapter.status()}

@app.post("/agy/start")
def agy_start():
    import subprocess
    subprocess.run(["systemctl", "--user", "start", "universal-agent-agy.service"])
    return {"status": "started"}

@app.post("/agy/stop")
def agy_stop():
    import subprocess
    subprocess.run(["systemctl", "--user", "stop", "universal-agent-agy.service"])
    return {"status": "stopped"}

class AgySubmitReq(BaseModel):
    goal: str

@app.post("/agy/submit")
def agy_submit(req: AgySubmitReq):
    adapter = AgyAdapter()
    # Mocking task approval by skipping it in this direct endpoint
    res = adapter.submit(req.goal, require_approval=False)
    if res["status"] == "error":
        raise HTTPException(status_code=400, detail=res["error"])
    return res
