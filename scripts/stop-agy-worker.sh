#!/bin/bash
SOCKET_NAME="universal-agent"
SESSION_NAME="universal-agent-agy"
timeout 5s tmux -L "$SOCKET_NAME" kill-session -t "$SESSION_NAME" 2>/dev/null || true
rm -f /tmp/agy_worker.lock
