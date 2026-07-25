# Диагностика и устранение неполадок (Troubleshooting)

- **Worker не запускается или `no server running on /tmp/tmux-xxx`:** 
  Проверьте `systemctl --user status universal-agent-agy.service`. Если сервис упал, логи можно посмотреть через `journalctl --user -u universal-agent-agy.service`.
- **API возвращает `eligibility_error` при запуске submit-задач:**
  Это ограничение провайдера LLM. Убедитесь, что прокси или VPN настроен корректно (если это актуально для вашего региона). Локальный worker фиксирует это как `eligibility_error` в файле `last_attempt.json`.
- **SQLite Locked:**
  LangGraph использует SQLite. Избегайте множественного параллельного доступа скриптами извне во время работы оркестратора.
- **Port 8765 in use:**
  Проверьте, не запущен ли процесс на этом порту: `lsof -i :8765`.
