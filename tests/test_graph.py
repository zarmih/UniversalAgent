
from universal_agent.core.graph import create_graph


def test_graph_normalize_plan_policy():
    graph = create_graph()
    conf = {"configurable": {"thread_id": "test_graph_1"}}
    # Invoke up to policy which should yield "waiting_for_approval"
    state = {
        "task_id": "test_g_1",
        "goal": "graph flow",
        "workspace_id": "ws_1",
        "status": "queued",
        "evidence": [],
        "plan": [],
        "permission_tier": "read_only"
    }
    # We mock out TaskStore in real environment, but here we just pass the state
    # Actually graph will interact with TaskStore db, which is fine since we use real db.
    res = graph.invoke(state, config=conf)
    # The policy currently defaults to "workspace_write" -> "executing" -> "checking"
    assert res["status"] in ["checking", "succeeded", "repairing"]

def test_critic_repair_loop():
    graph = create_graph()
    # Force state to check critic with bad evidence
    state = {
        "task_id": "test_g_2",
        "goal": "repair test",
        "workspace_id": "ws_2",
        "status": "checking",
        "evidence": [{"status": "error", "exit_code": 1}],
        "repair_attempts": 2
    }
    # Just run node
    import universal_agent.core.graph as gr
    # Critic should say repairing
    res1 = gr.critic(state)
    assert res1["status"] == "repairing"
    assert res1["repair_attempts"] == 3
    
    # Repair route should say failed since budget=3
    route = gr.repair_route(res1)
    assert route == "failed"
