import pytest
from universal_agent.core.graph import create_graph

def test_smoke():
    graph = create_graph()
    initial_state = {
        "task_id": "t1",
        "goal": "smoke test",
        "status": "queued",
        "plan": [],
        "current_step": 0,
        "evidence": [],
        "errors": [],
        "messages": []
    }
    
    result = graph.invoke(initial_state)
    assert result["status"] == "succeeded"
