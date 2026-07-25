# UniversalAgent

UniversalAgent is a highly autonomous background task orchestrator and task execution framework.

## Features
- **LangGraph Checkpointer**: Uses SQLite checkpointer for persisting states.
- **Workers**:
  - `AgyAdapter`: Proxy-aware adapter to safely run AGY tasks in a separate isolated `tmux` session.
  - `LLMWorker`: OpenAI-compatible wrapper to use local LLM instances (e.g. Ollama).
  - `OpenHands`: Future integration for sandbox task execution.

## Deployment
UniversalAgent runs as a `systemd` user service.
AGY Worker runs as `universal-agent-agy.service` but requires proxy configuration (`~/.local/share/universal-agent/agy-worker.env`).

**NOTE:** Secondary AGY worker might fail with "Eligibility check failed: Your current account is not eligible for Antigravity" based on region or auth constraints. If so, leave the worker disabled.
