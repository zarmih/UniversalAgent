# Описание API UniversalAgent

- `POST /tasks` — Создать новую задачу. Требует JSON `{type, parameters}`. Возвращает `{"task_id": "uuid"}`.
- `GET /tasks/{task_id}` — Получить текущий статус задачи.
- `GET /tasks/{task_id}/events` — Получить массив событий жизненного цикла задачи.
- `POST /tasks/{task_id}/approve` — Подтвердить задачу (выполняется если статус `waiting_for_approval`).
- `POST /tasks/{task_id}/deny` — Отклонить задачу (отменит выполнение).
- `POST /tasks/{task_id}/cancel` — Отменить задачу в любой момент.
- `GET /tasks/{task_id}/evidence` — Получить список собранных артефактов и логов.
- `GET /health` — Проверка жизнеспособности главного сервера.
- `GET /agy/status` — Проверка статуса AGY worker'а.
- `GET /agy/doctor` — Диагностика конфигурации worker'а.
