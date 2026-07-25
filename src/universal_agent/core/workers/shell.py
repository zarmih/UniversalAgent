import subprocess
import logging

logger = logging.getLogger(__name__)

class ShellWorker:
    def __init__(self, allowlist=None):
        self.allowlist = allowlist or ["ls", "echo", "pwd", "whoami"]

    def execute(self, cmd: str, timeout: int = 10) -> dict:
        base_cmd = cmd.split()[0]
        if base_cmd not in self.allowlist:
            return {"error": f"Command {base_cmd} not in allowlist", "exit_code": -1}
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Timeout", "exit_code": -1}
