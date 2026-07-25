# Roadmap

## Phase 1: Core MVP (Done)
- [x] Basic project layout, dependency management (`uv`).
- [x] FastAPI skeleton, CLI interface (`ua`).
- [x] LangGraph implementation with SQLite checkpointing.
- [x] Secure Workers (`shell`, `filesystem`, `browser`).
- [x] Basic task execution flow, evidence tracking, and policy approval logic.
- [x] 20+ unit tests with 100% pass rate.
- [x] Systemd service integration for background execution.

## Phase 2: Intelligence & Integration
- [ ] Connect real LLM adapters (via LangChain or explicit provider APIs).
- [ ] Implement OpenHands environment integration.
- [ ] Implement Domovoi task offloading capabilities.
- [ ] Extend UI (e.g. basic web frontend) for better task monitoring than CLI.

## Phase 3: Advanced Reasoning
- [ ] Multi-agent negotiation (Critic / Planner / Executor split into sub-graphs).
- [ ] Dynamic tool use based on context.
- [ ] Auto-repair code directly within the graph instead of just basic retry loops.
