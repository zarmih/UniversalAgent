import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver

from universal_agent.core.graph import create_graph


def test_sqlite_persistence(tmp_path):
    db_path = str(tmp_path / "test_state.db")
    with sqlite3.connect(db_path, check_same_thread=False) as conn:
        checkpointer = SqliteSaver(conn)
        graph = create_graph(checkpointer=checkpointer)
        
        config = {"configurable": {"thread_id": "test_thread_1"}}
        result1 = graph.invoke({"task_id": "t1", "goal": "test"}, config=config)
        assert result1["status"] == "succeeded"
        
        state = graph.get_state(config)
        assert state.values["task_id"] == "t1"

def test_policy_gate():
    graph = create_graph()
    result = graph.invoke({"task_id": "t2", "goal": "test policy"})
    assert result["status"] == "succeeded"
