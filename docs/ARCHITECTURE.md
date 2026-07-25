# Architecture

## Components
- **API (FastAPI)**: Serves REST endpoints for task creation, inspection, and lifecycle management.
- **Task Store (SQLite)**: Persists `tasks`, `task_events` (status transitions), and `evidence`.
- **LangGraph Orchestrator**: Manages state transitions using `AgentState`.
  - Nodes: `normalize` -> `plan` -> `policy` -> `execute` -> `collect_evidence` -> `critic` -> `verify`.
  - Conditional Edges: Interrupts at `policy` for human approval if `permission_tier` is high. Handles `critic` repair loops (retries up to 3 times on failed execution).
- **Workers**: Interfaces for acting on the system.
  - `ShellWorker`: Secure subprocess execution with allowlists.
  - `FilesystemWorker`: Path-traversal proofed CRUD on files.
  - `BrowserWorker`: Safe headless chromium automation (dumps DOM, takes screenshots).
  - `LLMWorker`: Mocked LLM completion endpoint for critical decision making.
  - `AgyAdapter` & `OpenHandsAdapter`: Plugin stubs.

## State Management
We use both LangGraph's `SqliteSaver` checkpointer for graph iteration state (thread level), and our custom `TaskStore` for API-level status querying and persistence of evidence without requiring full graph resumption.
