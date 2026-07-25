#!/bin/bash
SESSION_NAME="universal-agent-agy"
SOCKET_NAME="universal-agent"
AGY_BIN="/home/mikhail/.local/bin/agy"

if tmux -L "$SOCKET_NAME" has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "AGY worker session already running."
else
    echo "Starting AGY worker session..."
    if [ -f "/home/mikhail/.local/share/universal-agent/agy-worker.env" ]; then
        set -a
        source /home/mikhail/.local/share/universal-agent/agy-worker.env
        set +a
    fi
    # Use env to explicitly pass to tmux
    tmux -L "$SOCKET_NAME" new-session -d -s "$SESSION_NAME" "cd /tmp && env HTTP_PROXY=$HTTP_PROXY HTTPS_PROXY=$HTTPS_PROXY ALL_PROXY=$ALL_PROXY NO_PROXY=$NO_PROXY http_proxy=$http_proxy https_proxy=$https_proxy all_proxy=$all_proxy no_proxy=$no_proxy NODE_USE_ENV_PROXY=$NODE_USE_ENV_PROXY $AGY_BIN --dangerously-skip-permissions"
    echo "AGY worker started."
fi
