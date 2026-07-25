# Universal Agent

Universal local agent framework based on LangGraph, SQLite, FastAPI, and robust worker isolations.

## Overview

UniversalAgent orchestrates local and containerized tasks using LangGraph. Features:
- **Persistent State**: SQLite task and graph checkpointing (`SqliteSaver`).
- **Security Checkpoints**: Built-in permission tiers with approval gates (`waiting_for_approval`).
- **Safe Workers**: Pre-configured strict workers (`shell` without `shell=True`, path-traversal protected `filesystem`, etc.)
- **Evidence Loop**: Collects task evidence (stdout, status codes, screenshots) for LLM critique.

## Setup

```bash
# Initialize uv venv and deps
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Start system service
systemctl --user start universal-agent.service
```

## CLI Usage

```bash
# Check health
ua health

# Create a task
ua create "Find files in src/"

# Run the task
ua run <task_id>

# Approve a policy gate
ua approve <task_id>

# Check status and evidence
ua show <task_id>
ua events <task_id>
ua evidence <task_id>
```
