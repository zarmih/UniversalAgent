#!/bin/bash
echo "=== Doctor Check ==="
echo "Python env:"
ls -ld /home/mikhail/.local/share/universal-agent/venv
/home/mikhail/.local/share/universal-agent/venv/bin/python --version
echo "Playwright browsers:"
ls -ld /mnt/SDD_1.7_TB/UniversalAgent/runtime/playwright-browsers
echo "Service status:"
systemctl --user status universal-agent.service --no-pager
echo "API Check:"
curl -s http://127.0.0.1:8765/health
echo ""
