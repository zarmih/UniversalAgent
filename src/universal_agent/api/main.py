
from fastapi import FastAPI
from pydantic import BaseModel

from universal_agent.core.graph import create_graph

app = FastAPI(title="Universal Local Agent API")
graph = create_graph()

class TaskRequest(BaseModel):
    goal: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/task")
def submit_task(request: TaskRequest):
    # Dummy synchronous execution for MVP
    initial_state = {
        "task_id": "t1",
        "goal": request.goal,
        "status": "queued",
        "plan": [],
        "current_step": 0,
        "evidence": [],
        "errors": [],
        "messages": []
    }
    
    result = graph.invoke(initial_state)
    return {"status": result.get("status")}
