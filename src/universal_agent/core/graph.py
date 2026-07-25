import logging
from .state import AgentState, StateGraph, END

logger = logging.getLogger(__name__)

def normalize(state: AgentState):
    logger.info(f"Normalizing task: {state.get('task_id')}")
    return {"status": "planning"}

def plan(state: AgentState):
    logger.info("Planning execution")
    return {"plan": ["step1", "step2"]}

def policy(state: AgentState):
    logger.info("Checking policy and risk gates")
    return {"status": "executing"}

def execute(state: AgentState):
    logger.info("Executing plan")
    return {"evidence": [{"step": "step1", "result": "ok"}]}

def collect_evidence(state: AgentState):
    logger.info("Collecting evidence")
    return {}

def critic(state: AgentState):
    logger.info("Critic reviewing evidence")
    return {}

def verify(state: AgentState):
    logger.info("Verifying goal")
    return {"status": "succeeded"}

def create_graph():
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
    workflow.add_edge("policy", "execute")
    workflow.add_edge("execute", "collect_evidence")
    workflow.add_edge("collect_evidence", "critic")
    workflow.add_edge("critic", "verify")
    workflow.add_edge("verify", END)

    return workflow.compile()
