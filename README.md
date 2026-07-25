# UniversalAgent 🚀

UniversalAgent — это локальный оркестратор задач (MVP), построенный на базе **LangGraph**, **FastAPI** и **SQLite**. Он обеспечивает надёжное выполнение сложных и потенциально опасных задач в изолированных средах (workers) с механизмом ручного подтверждения (Approval Policy) и сбором доказательств (Evidence).

⚠️ **Статус:** Working Local Orchestrator / MVP. Проект активно развивается.

## Ключевые возможности

- 🛡️ **Изолированное выполнение (Workers):** Задачи выполняются в отдельных `tmux` сессиях с изоляцией окружения. 
- 🚦 **Политика подтверждения (Approval Policy):** Опасные действия (например, запуск submit-команд, модификация файловой системы) могут быть настроены на запрос явного разрешения пользователя.
- 💾 **Надёжность и состояние:** Все задачи, их статусы и логи хранятся в SQLite через механизмы LangGraph, что позволяет продолжать работу после перезапуска.
- 🔍 **Доказательства (Evidence):** Сбор артефактов и логов выполнения.
- 🔌 **API и CLI:** Полноценный REST API (FastAPI) и командный интерфейс.

## Быстрый старт

Убедитесь, что у вас установлен Python 3.12+ и `tmux`.

```bash
# Клонирование репозитория
git clone https://github.com/zarmih/UniversalAgent.git
cd UniversalAgent

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Запуск локально
python3 -m universal_agent.main

# Проверка Health
curl http://localhost:8765/health
```

Подробная инструкция по использованию, установке (через systemd) и типовым сценариям доступна в [docs/USAGE.md](docs/USAGE.md).

## Документация

- [Архитектура (ARCHITECTURE.md)](docs/ARCHITECTURE.md)
- [Безопасность (SECURITY.md)](docs/SECURITY.md)
- [Использование (USAGE.md)](docs/USAGE.md)
- [Конфигурация (CONFIGURATION.md)](docs/CONFIGURATION.md)
- [API (API.md)](docs/API.md)
- [Диагностика (TROUBLESHOOTING.md)](docs/TROUBLESHOOTING.md)
- [Roadmap (ROADMAP.md)](docs/ROADMAP.md)

## Лицензия
MIT License. См. файл [LICENSE](LICENSE) для подробностей.
