#!/bin/bash
SESSION_NAME="universal-agent-agy"
SOCKET_NAME="universal-agent"
AGY_BIN="/home/mikhail/.local/bin/agy"

if tmux -L "$SOCKET_NAME" has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "AGY worker session already running."
else
    echo "Starting AGY worker session..."
    tmux -L "$SOCKET_NAME" new-session -d -s "$SESSION_NAME" "cd /tmp && $AGY_BIN --dangerously-skip-permissions"
    echo "AGY worker started."
fi
