#!/bin/bash
SESSION_NAME="universal-agent-agy"
SOCKET_NAME="universal-agent"

if tmux -L "$SOCKET_NAME" has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "active"
else
    echo "inactive"
fi
