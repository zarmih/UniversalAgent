import logging
import os
import subprocess
import time
import uuid

from ..config import config

logger = logging.getLogger(__name__)

class AgyAdapter:
    def __init__(self):
        self.enabled = config.enable_agy_submit
        self.socket = "universal-agent"
        self.session = "universal-agent-agy"
        self.lock_file = "/tmp/agy_worker.lock"

    def ensure_session(self) -> bool:
        res = subprocess.run(["tmux", "-L", self.socket, "has-session", "-t", self.session], capture_output=True)
        return res.returncode == 0

    def status(self) -> str:
        if not self.ensure_session():
            return "inactive"
        if os.path.exists(self.lock_file):
            return "busy"
        return "active"

    def check_health(self):
        st = self.status()
        if st == "inactive":
            return {"status": "error", "message": "AGY session inactive"}
        return {"status": "ok", "message": f"AGY adapter is {st}"}

    def get_output(self) -> str:
        res = subprocess.run(["tmux", "-L", self.socket, "capture-pane", "-p", "-t", self.session], capture_output=True, text=True)
        return res.stdout

    def cancel(self):
        subprocess.run(["tmux", "-L", self.socket, "send-keys", "-t", self.session, "C-c"])
        if os.path.exists(self.lock_file):
            os.remove(self.lock_file)
        return {"status": "cancelled"}

    def submit(self, goal: str, timeout: int = 60, require_approval: bool = True):
        if not self.enabled:
            return {"status": "error", "error": "AGY submit is disabled by configuration"}
        
        # Guard against recursive session
        if os.environ.get("TMUX", "").endswith(self.socket):
            res_sess = subprocess.run(["tmux", "display-message", "-p", "#S"], capture_output=True, text=True)
            if res_sess.stdout.strip() == self.session:
                return {"status": "error", "error": "Cannot submit from within the AGY session itself"}

        if not self.ensure_session():
            return {"status": "error", "error": "AGY worker session not running"}

        if self.status() == "busy":
            return {"status": "error", "error": "AGY worker is busy"}
            
        # In a real setup, we would check if the task is approved via TaskStore.
        # But this function only gets the goal text, so the caller (graph node) handles approval logic.
        if require_approval:
            # We assume the caller verified it. If not, this is a placeholder check.
            pass

        task_id = str(uuid.uuid4())
        wrapped_goal = f"BEGIN_TASK_{task_id}\n{goal}\nEND_TASK_{task_id}\nWhen finished, you MUST output a JSON line: {{\"task_done\": \"{task_id}\"}}"

        # Acquire lock
        with open(self.lock_file, "w") as f:
            f.write(task_id)
            
        try:
            # Send keys safely using load-buffer and paste-buffer
            subprocess.run(["tmux", "-L", self.socket, "set-buffer", wrapped_goal])
            subprocess.run(["tmux", "-L", self.socket, "paste-buffer", "-t", self.session, "-d"])
            subprocess.run(["tmux", "-L", self.socket, "send-keys", "-t", self.session, "Enter"])

            start_time = time.time()
            marker = f'"task_done": "{task_id}"'
            
            while time.time() - start_time < timeout:
                out = self.get_output()
                if marker in out:
                    os.remove(self.lock_file)
                    return {"status": "succeeded", "result": out, "evidence": [{"type": "agy_output", "content": out}]}
                time.sleep(2)
                
            # Timeout
            self.cancel()
            return {"status": "error", "error": "Timeout waiting for AGY completion"}
            
        except Exception as e:
            if os.path.exists(self.lock_file):
                os.remove(self.lock_file)
            return {"status": "error", "error": str(e)}
