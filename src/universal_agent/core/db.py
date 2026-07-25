import json
import sqlite3

from .config import config
from .models import EvidenceRecord, TaskEvent, TaskRecord


def get_db():
    conn = sqlite3.connect(config.db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                goal TEXT NOT NULL,
                status TEXT NOT NULL,
                permission_tier TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                plan TEXT,
                result TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS task_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                status_from TEXT,
                status_to TEXT NOT NULL,
                reason TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(task_id) REFERENCES tasks(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                worker TEXT NOT NULL,
                summary TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                exit_code INTEGER,
                data TEXT,
                FOREIGN KEY(task_id) REFERENCES tasks(id)
            )
        ''')
        conn.commit()

init_db()

class TaskStore:
    @staticmethod
    def create_task(task: TaskRecord):
        with get_db() as conn:
            conn.execute(
                "INSERT INTO tasks (id, goal, status, permission_tier, created_at, updated_at, plan, result) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (task.id, task.goal, task.status, task.permission_tier, task.created_at, task.updated_at, json.dumps(task.plan), task.result)
            )
    
    @staticmethod
    def update_task(task: TaskRecord):
        with get_db() as conn:
            conn.execute(
                "UPDATE tasks SET status=?, permission_tier=?, updated_at=?, plan=?, result=? WHERE id=?",
                (task.status, task.permission_tier, task.updated_at, json.dumps(task.plan), task.result, task.id)
            )

    @staticmethod
    def get_task(task_id: str) -> TaskRecord:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
            if row:
                d = dict(row)
                d['plan'] = json.loads(d['plan']) if d['plan'] else []
                return TaskRecord(**d)
        return None

    @staticmethod
    def list_tasks():
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
            res = []
            for row in rows:
                d = dict(row)
                d['plan'] = json.loads(d['plan']) if d['plan'] else []
                res.append(TaskRecord(**d))
            return res

    @staticmethod
    def add_event(event: TaskEvent):
        with get_db() as conn:
            conn.execute(
                "INSERT INTO task_events (task_id, status_from, status_to, reason, timestamp) VALUES (?, ?, ?, ?, ?)",
                (event.task_id, event.status_from, event.status_to, event.reason, event.timestamp)
            )

    @staticmethod
    def get_events(task_id: str):
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM task_events WHERE task_id=? ORDER BY timestamp ASC", (task_id,)).fetchall()
            return [TaskEvent(**dict(row)) for row in rows]

    @staticmethod
    def add_evidence(ev: EvidenceRecord):
        with get_db() as conn:
            conn.execute(
                "INSERT INTO evidence (task_id, worker, summary, timestamp, exit_code, data) VALUES (?, ?, ?, ?, ?, ?)",
                (ev.task_id, ev.worker, ev.summary, ev.timestamp, ev.exit_code, json.dumps(ev.data))
            )

    @staticmethod
    def get_evidence(task_id: str):
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM evidence WHERE task_id=? ORDER BY timestamp ASC", (task_id,)).fetchall()
            res = []
            for row in rows:
                d = dict(row)
                d['data'] = json.loads(d['data']) if d['data'] else {}
                res.append(EvidenceRecord(**d))
            return res
