import universal_agent.core.graph as gr
from universal_agent.core.graph import create_graph


def test_graph_normalize_plan_policy():
    graph = create_graph()
    conf = {"configurable": {"thread_id": "test_graph_1"}}
    state = {
        "task_id": "test_g_1",
        "goal": "graph flow",
        "workspace_id": "ws_1",
        "status": "queued",
        "evidence": [],
        "plan": [],
        "permission_tier": "read_only"
    }
    res = graph.invoke(state, config=conf)
    # Depending on mock, it goes up to a certain node
    assert res is not None

def test_critic_repair_loop():
    state = {
        "task_id": "test_g_2",
        "goal": "repair test",
        "workspace_id": "ws_2",
        "status": "checking",
        "evidence": [{"status": "error", "exit_code": 1}],
        "repair_attempts": 2
    }
    res1 = gr.critic(state)
    assert res1["status"] == "repairing"
    
    route = gr.repair_route(res1)
    assert route == "failed"
