# UniversalAgent Usage Guide

UniversalAgent allows you to safely execute tasks using local AI models or scripts within an isolated environment.

## First Run

After setup (see README), start the service:
```bash
systemctl --user start universal-agent.service
# Or locally: python -m universal_agent.main
```

Check health:
```bash
curl -s http://127.0.0.1:8765/health
# Expected: {"status":"ok","version":"1.0.0"}
```

## Task Lifecycle (End-to-End)

1. **Create a task:**
```bash
curl -X POST http://localhost:8765/tasks \
     -H "Content-Type: application/json" \
     -d '{"type":"filesystem", "parameters":{"path":"/tmp/test", "action":"read"}}'
```
*Returns a `task_id`.*

2. **Check Status (show / events):**
```bash
curl http://localhost:8765/tasks/{task_id}
curl http://localhost:8765/tasks/{task_id}/events
```

3. **Approval-requiring Tasks:**
If a task involves dangerous actions (e.g. file writing, submitting), it transitions to `waiting_for_approval`.
To approve or deny:
```bash
curl -X POST http://localhost:8765/tasks/{task_id}/approve
# or
curl -X POST http://localhost:8765/tasks/{task_id}/deny
```

4. **Cancel a Task:**
```bash
curl -X POST http://localhost:8765/tasks/{task_id}/cancel
```

5. **View Results (Evidence):**
```bash
curl http://localhost:8765/tasks/{task_id}/evidence
```

## Interacting with AGY Worker

The secondary worker (AGY) is used for deep reasoning tasks.
**Note:** Submitting requires a feature flag and may fail with a `provider eligibility/auth error` depending on your local LLM provider. This is normal and means the worker is active but the upstream API rejected the request.

Check AGY status:
```bash
curl http://localhost:8765/agy/status
```
