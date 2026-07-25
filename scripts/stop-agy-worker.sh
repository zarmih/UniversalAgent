#!/bin/bash
SESSION_NAME="universal-agent-agy"
SOCKET_NAME="universal-agent"

if tmux -L "$SOCKET_NAME" has-session -t "$SESSION_NAME" 2>/dev/null; then
    tmux -L "$SOCKET_NAME" kill-session -t "$SESSION_NAME"
    echo "AGY worker stopped."
else
    echo "AGY worker not running."
fi
