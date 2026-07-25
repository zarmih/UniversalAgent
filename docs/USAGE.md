# Руководство по использованию UniversalAgent

UniversalAgent позволяет безопасно выполнять задачи, используя локальные AI-модели или скрипты в изолированном окружении.

## Первый запуск

После настройки (см. README), запустите сервис:
```bash
systemctl --user start universal-agent.service
# Или локально: python -m universal_agent.main
```

Проверка состояния (Health):
```bash
curl -s http://127.0.0.1:8765/health
# Ожидаемый ответ: {"status":"ok","version":"1.0.0"}
```

## Жизненный цикл задачи (End-to-End)

1. **Создание задачи:**
```bash
curl -X POST http://localhost:8765/tasks \
     -H "Content-Type: application/json" \
     -d '{"type":"filesystem", "parameters":{"path":"/tmp/test", "action":"read"}}'
```
*Ответ вернёт `task_id`.*

2. **Просмотр статуса (show / events):**
```bash
curl http://localhost:8765/tasks/{task_id}
curl http://localhost:8765/tasks/{task_id}/events
```

3. **Задача, требующая подтверждения (Approval):**
Если задача включает опасное действие (запись файлов, запуск submit), она перейдёт в статус `waiting_for_approval`.
Для подтверждения или отклонения:
```bash
curl -X POST http://localhost:8765/tasks/{task_id}/approve
# или
curl -X POST http://localhost:8765/tasks/{task_id}/deny
```

4. **Отмена задачи (Cancel):**
Вы можете отменить любую выполняющуюся задачу:
```bash
curl -X POST http://localhost:8765/tasks/{task_id}/cancel
```

5. **Просмотр результатов (Evidence):**
После успешного (или неудачного) завершения можно посмотреть собранные артефакты:
```bash
curl http://localhost:8765/tasks/{task_id}/evidence
```

## Взаимодействие с AGY Worker (Агентом)

Вторичный воркер (AGY) используется для глубоких задач. 
**Важно:** Использование submit требует включения feature flag и может завершиться ошибкой `provider eligibility/auth error` в зависимости от вашего локального LLM-провайдера. Это нормально и означает, что воркер работает, но API отклонил запрос.

Проверка состояния AGY Worker:
```bash
curl http://localhost:8765/agy/status
```

Если AGY Worker сталкивается с проблемой (например, `eligibility_error`), его статус можно продиагностировать через лог последней попытки.
