# Security

## Principles
1. **Never `shell=True`**: All commands are executed as lists using `subprocess.run(shell=False)`.
2. **Path Traversal Protection**: Any file operation uses `os.path.abspath` and verifies the prefix matches the `workspace_id`.
3. **Allowlist Commands**: Shell commands are strictly filtered (e.g., `ls`, `pwd`, `cat`, `grep`, `git`, `python`, `pytest`).
4. **Dangerous Character Blocking**: Commands cannot contain `;`, `|`, `<`, `>`, `$()`, `` ` ``, or `&`.
5. **Approval Gates**: The `policy` node analyzes the plan and assigns a `permission_tier`. If it requires `host_write` or `dangerous`, the graph halts and sets the status to `waiting_for_approval` until `ua approve <id>` is called.
6. **No Auto-Network Access**: The browser worker rejects external URLs unless explicitly enabled in the configuration (`allow_external_network=True`).
