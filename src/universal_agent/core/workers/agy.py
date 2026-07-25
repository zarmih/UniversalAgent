import json
import logging
import os
import re
import subprocess
import time
import uuid
from datetime import UTC, datetime

from ..config import config

logger = logging.getLogger(__name__)

def sanitize_output(text: str) -> str:
    if not text:
        return ""
    # Mask emails
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '***@***.***', text)
    # Mask tokens / cookies / bearers
    text = re.sub(r'(?i)(bearer |token=|cookie=|token |key )([a-zA-Z0-9_\-\.]{20,})', r'\1***', text)
    # Mask conversation IDs / UUIDs
    text = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '***-UUID-***', text)
    # Mask home secret paths (e.g. /home/mikhail/.gemini)
    text = re.sub(r'/home/\w+/\.(gemini|config|ssh|local)[/\w\-\.]*', '/home/***/secret/***', text)
    return text

class AgyAdapter:
    def __init__(self):
        self.enabled = config.enable_agy_submit
        self.socket = "universal-agent"
        self.session = "universal-agent-agy"
        self.lock_file = "/tmp/agy_worker.lock"
        self.artifacts_dir = "/mnt/SDD_1.7_TB/UniversalAgent/artifacts/agy-worker"
        os.makedirs(self.artifacts_dir, exist_ok=True)
        self.last_attempt_file = os.path.join(self.artifacts_dir, "last_attempt.json")

    def ensure_session(self) -> bool:
        res = subprocess.run(
            ["timeout", "5s", "tmux", "-L", self.socket, "has-session", "-t", self.session],
            capture_output=True
        )
        return res.returncode == 0

    def status(self) -> str:
        if not self.ensure_session():
            return "inactive"
        if os.path.exists(self.lock_file):
            return "busy"
        return "active"

    def get_output(self) -> str:
        res = subprocess.run(
            ["timeout", "5s", "tmux", "-L", self.socket, "capture-pane", "-p", "-t", self.session],
            capture_output=True, text=True
        )
        return res.stdout

    def cancel(self):
        subprocess.run(["timeout", "5s", "tmux", "-L", self.socket, "send-keys", "-t", self.session, "C-c"])
        if os.path.exists(self.lock_file):
            os.remove(self.lock_file)
        return {"status": "cancelled"}
        
    def _get_worker_pid(self) -> str:
        res = subprocess.run(
            ["timeout", "5s", "tmux", "-L", self.socket, "list-panes", "-t", self.session, "-F", "#{pane_pid}"],
            capture_output=True, text=True
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip().split('\n')[0]
        return ""

    def save_attempt(self, evidence: dict):
        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        path = os.path.join(self.artifacts_dir, f"attempt-{ts}.json")
        try:
            with open(path, "w") as f:
                json.dump(evidence, f, indent=2)
            with open(self.last_attempt_file, "w") as f:
                json.dump(evidence, f, indent=2)
        except Exception as e:
            logger.debug(f"Failed to save attempt evidence: {e}")
        return path

    def _do_cleanup(self, evidence: dict):
        evidence["cleanup_attempted"] = True
        try:
            subprocess.run(["timeout", "5s", "systemctl", "--user", "stop", "universal-agent-agy.service"], capture_output=True)
            subprocess.run(["timeout", "5s", "tmux", "-L", self.socket, "kill-session", "-t", self.session], capture_output=True)
            evidence["cleanup_success"] = True
        except Exception as e:
            logger.debug(f"Cleanup error: {e}")
            evidence["cleanup_success"] = False
            
        res_srv = subprocess.run(["timeout", "5s", "systemctl", "--user", "is-active", "universal-agent-agy.service"], capture_output=True, text=True)
        evidence["service_active_after"] = (res_srv.stdout.strip() == "active")
        evidence["session_exists_after"] = self.ensure_session()
        self.save_attempt(evidence)

    def submit(self, goal: str, timeout: int = 60, require_approval: bool = True):
        evidence = {
            "timestamp": datetime.now(UTC).isoformat(),
            "launcher": "/home/mikhail/.local/bin/agy",
            "node_version": "unknown",
            "proxy_configured": False,
            "proxy_reachable": False,
            "worker_pid": "",
            "session_socket": f"{self.session} / {self.socket}",
            "ready_detected": False,
            "submitted": False,
            "exact_expected_marker": "",
            "success": False,
            "failure_kind": "",
            "sanitized_output_excerpt": "",
            "duration": 0
        }

        try:
            if not self.enabled:
                evidence["failure_kind"] = "disabled"
                return {"status": "error", "error": "AGY submit is disabled by configuration"}
            
            # Guard against recursive session
            if os.environ.get("TMUX", "").endswith(self.socket):
                res_sess = subprocess.run(["timeout", "5s", "tmux", "display-message", "-p", "#S"], capture_output=True, text=True)
                if res_sess.stdout.strip() == self.session:
                    evidence["failure_kind"] = "recursive_submit"
                    return {"status": "error", "error": "Cannot submit from within the AGY session itself"}

            if not self.ensure_session():
                evidence["failure_kind"] = "no_session"
                return {"status": "error", "error": "AGY worker session not running"}

            if self.status() == "busy":
                evidence["failure_kind"] = "busy"
                return {"status": "error", "error": "AGY worker is busy"}

            task_id = str(uuid.uuid4()).replace("-", "")
            # No-echo marker logic
            wrapped_goal = f"BEGIN_TASK_{task_id}\n{goal}\nEND_TASK_{task_id}\nWhen finished, output a JSON line exactly like this but replace the word ID with the task ID: {{\"task_done\": \"{task_id}\"}}"
            
            expected_marker = f'{{"task_done": "{task_id}"}}'
            evidence["exact_expected_marker"] = expected_marker
            evidence["worker_pid"] = self._get_worker_pid()

            with open(self.lock_file, "w") as f:
                f.write(task_id)
                
            start_time = time.time()
            
            # Determine readiness
            out = self.get_output()
            if "Eligibility check failed" in out:
                evidence["failure_kind"] = "eligibility_error"
                evidence["sanitized_output_excerpt"] = sanitize_output(out[-500:])
                self.cancel()
                return {"status": "error", "error": "Eligibility error detected"}
                
            evidence["ready_detected"] = True

            subprocess.run(["timeout", "5s", "tmux", "-L", self.socket, "set-buffer", wrapped_goal])
            subprocess.run(["timeout", "5s", "tmux", "-L", self.socket, "paste-buffer", "-t", self.session, "-d"])
            subprocess.run(["timeout", "5s", "tmux", "-L", self.socket, "send-keys", "-t", self.session, "Enter"])
            
            evidence["submitted"] = True

            while time.time() - start_time < timeout:
                out = self.get_output()
                if expected_marker in out:
                    if os.path.exists(self.lock_file):
                        os.remove(self.lock_file)
                    evidence["success"] = True
                    evidence["duration"] = round(time.time() - start_time, 2)
                    evidence["sanitized_output_excerpt"] = sanitize_output(out[-1000:])
                    return {"status": "succeeded", "result": out, "evidence": [{"type": "agy_output", "content": out}]}
                
                if "Eligibility check failed" in out:
                    self.cancel()
                    evidence["failure_kind"] = "eligibility_error"
                    evidence["duration"] = round(time.time() - start_time, 2)
                    evidence["sanitized_output_excerpt"] = sanitize_output(out[-1000:])
                    return {"status": "error", "error": "Eligibility error detected after submit"}

                time.sleep(2)
                
            self.cancel()
            evidence["failure_kind"] = "timeout"
            evidence["duration"] = round(time.time() - start_time, 2)
            evidence["sanitized_output_excerpt"] = sanitize_output(out[-1000:])
            return {"status": "error", "error": "Timeout waiting for AGY completion"}
                
        except Exception as e:
            if os.path.exists(self.lock_file):
                os.remove(self.lock_file)
            evidence["failure_kind"] = "exception"
            evidence["sanitized_output_excerpt"] = str(e)
            evidence["duration"] = round(time.time() - start_time, 2)
            return {"status": "error", "error": str(e)}
        finally:
            self.save_attempt(evidence)
            if not evidence.get("success") and evidence.get("failure_kind") not in ("disabled", "recursive_submit"):
                self._do_cleanup(evidence)
            else:
                evidence["cleanup_attempted"] = False
                self.save_attempt(evidence)
