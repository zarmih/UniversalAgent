#!/bin/bash
systemctl --user daemon-reload
systemctl --user start universal-agent.service
systemctl --user status universal-agent.service
