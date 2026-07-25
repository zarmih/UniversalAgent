import logging
import os
import subprocess

logger = logging.getLogger(__name__)

class ShellWorker:
    def __init__(self, workspace_path: str):
        self.workspace_path = os.path.abspath(workspace_path)
        # Ensure workspace exists
        os.makedirs(self.workspace_path, exist_ok=True)
        self.allowlist = ["pwd", "ls", "find", "cat", "head", "tail", "grep", "rg", "git", "pytest", "python"]
        self.dangerous_chars = [";", "|", ">", "<", "$(", "`", "&"]

    def is_safe_command(self, cmd_args: list[str]) -> bool:
        if not cmd_args:
            return False
        base_cmd = cmd_args[0]
        if base_cmd not in self.allowlist:
            return False
        
        # Check for dangerous characters in arguments
        for arg in cmd_args:
            for char in self.dangerous_chars:
                if char in arg:
                    return False
            # Prevent absolute paths escaping workspace unless it's /tmp or something safe (strictly blocked here)
            if arg.startswith("/") and not arg.startswith(self.workspace_path):
                return False
            if "../" in arg:
                return False
        return True

    def execute(self, cmd_args: list[str], timeout: int = 15) -> dict:
        if not self.is_safe_command(cmd_args):
            return {"status": "error", "error": f"Command not allowed or contains forbidden patterns: {cmd_args}"}
            
        try:
            # We strictly use shell=False and pass list of arguments
            res = subprocess.run(
                cmd_args,
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            return {
                "status": "ok",
                "stdout": res.stdout,
                "stderr": res.stderr,
                "exit_code": res.returncode
            }
        except subprocess.TimeoutExpired:
            return {"status": "error", "error": "Command timed out", "exit_code": -1}
        except Exception as e:
            return {"status": "error", "error": str(e), "exit_code": -2}
