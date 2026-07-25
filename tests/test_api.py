from fastapi.testclient import TestClient

from universal_agent.api.main import app
from universal_agent.core.db import TaskStore, get_db

client = TestClient(app)

def setup_module(module):
    # Ensure fresh DB for tests by cleaning up tables
    with get_db() as conn:
        conn.execute("DELETE FROM evidence")
        conn.execute("DELETE FROM task_events")
        conn.execute("DELETE FROM tasks")
        conn.commit()

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_create_and_get_task():
    resp = client.post("/tasks", json={"goal": "test API"})
    assert resp.status_code == 200
    task_id = resp.json()["id"]
    assert resp.json()["status"] == "queued"
    
    resp2 = client.get(f"/tasks/{task_id}")
    assert resp2.status_code == 200
    assert resp2.json()["id"] == task_id

def test_task_events():
    resp = client.post("/tasks", json={"goal": "events test"})
    task_id = resp.json()["id"]
    
    ev_resp = client.get(f"/tasks/{task_id}/events")
    assert ev_resp.status_code == 200
    assert len(ev_resp.json()) == 1
    assert ev_resp.json()[0]["status_to"] == "queued"

def test_task_cancel():
    resp = client.post("/tasks", json={"goal": "cancel test"})
    task_id = resp.json()["id"]
    
    client.post(f"/tasks/{task_id}/cancel")
    resp2 = client.get(f"/tasks/{task_id}")
    assert resp2.json()["status"] == "cancelled"

def test_task_approval_flow():
    resp = client.post("/tasks", json={"goal": "approval test"})
    task_id = resp.json()["id"]
    
    # Mock status to waiting_for_approval
    task = TaskStore.get_task(task_id)
    task.status = "waiting_for_approval"
    TaskStore.update_task(task)
    
    # Approve
    client.post(f"/tasks/{task_id}/approve")
    task = TaskStore.get_task(task_id)
    # In TestClient, background tasks run synchronously, so it goes to 'succeeded'
    assert task.status in ["executing", "succeeded", "checking"]

def test_task_deny_flow():
    resp = client.post("/tasks", json={"goal": "deny test"})
    task_id = resp.json()["id"]
    
    # Mock status to waiting_for_approval
    task = TaskStore.get_task(task_id)
    task.status = "waiting_for_approval"
    TaskStore.update_task(task)
    
    # Deny
    client.post(f"/tasks/{task_id}/deny", json={"action": "deny", "reason": "unsafe"})
    task = TaskStore.get_task(task_id)
    assert task.status == "blocked"

def test_evidence_endpoint():
    resp = client.post("/tasks", json={"goal": "evidence test"})
    task_id = resp.json()["id"]
    # Evidence is empty initially
    ev = client.get(f"/tasks/{task_id}/evidence")
    assert len(ev.json()) == 0
