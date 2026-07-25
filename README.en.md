# UniversalAgent 🚀

UniversalAgent is a local task orchestrator (MVP) built with **LangGraph**, **FastAPI**, and **SQLite**. It ensures reliable execution of complex and potentially dangerous tasks in isolated environments (workers) with manual approval policies and evidence collection.

⚠️ **Status:** Working Local Orchestrator / MVP. 

## Key Features

- 🛡️ **Isolated Execution (Workers):** Tasks run in separate `tmux` sessions.
- 🚦 **Approval Policy:** Dangerous actions require explicit user approval.
- 💾 **Reliability & State:** All tasks and states are persisted in SQLite via LangGraph.
- 🔍 **Evidence:** Artifacts and execution logs collection.
- 🔌 **API & CLI:** Full REST API (FastAPI) and command-line interface.

## Quick Start

Ensure you have Python 3.12+ and `tmux` installed.

```bash
git clone https://github.com/zarmih/UniversalAgent.git
cd UniversalAgent

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start locally
python3 -m universal_agent.main

# Health check
curl http://localhost:8765/health
```

For detailed usage, systemd installation, and typical scenarios, see [docs/USAGE.en.md](docs/USAGE.en.md).

## Documentation

- [Architecture (ARCHITECTURE.md)](docs/ARCHITECTURE.md)
- [Security (SECURITY.md)](docs/SECURITY.md)
- [Usage (USAGE.en.md)](docs/USAGE.en.md)
- [Configuration (CONFIGURATION.md)](docs/CONFIGURATION.md)
- [API (API.md)](docs/API.md)
- [Troubleshooting (TROUBLESHOOTING.md)](docs/TROUBLESHOOTING.md)
- [Roadmap (ROADMAP.md)](docs/ROADMAP.md)

## License
MIT License. See [LICENSE](LICENSE) for details.
