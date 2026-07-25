# UniversalAgent

UniversalAgent is a highly autonomous background task orchestrator and task execution framework.

## Features
- **LangGraph Checkpointer**: Uses SQLite checkpointer for persisting states.
- **Workers**:
  - `AgyAdapter`: Proxy-aware adapter to safely run AGY tasks in a separate isolated `tmux` session.
  - `LLMWorker`: OpenAI-compatible wrapper to use local LLM instances (e.g. Ollama).
  - `OpenHands`: Future integration for sandbox task execution.

### Worker Lifecycle
The AGY Worker runs in a standalone systemd session (`universal-agent-agy.service`). When a task is submitted, the session is created. If the task fails due to timeout, eligibility block, or internal error, a strict cleanup phase stops the service and destroys the session, preventing stale or stuck workers. If the task succeeds, the service remains active. The lifecycle state (including cleanup status) is securely recorded in the artifact logs.

## Deployment
UniversalAgent runs as a `systemd` user service.
AGY Worker runs as `universal-agent-agy.service` but requires proxy configuration (`~/.local/share/universal-agent/agy-worker.env`).

**NOTE:** The AGY worker proxy has been fixed and successfully routes traffic. However, secondary AGY workers may fail with "Eligibility check failed". This is an auth/account-level block, not a network error. If this happens, leave the worker disabled. The real status of attempts can be checked using the CLI command `ua agy-doctor` or `ua agy-last-attempt` which reads the sanitized attempt artifact.
