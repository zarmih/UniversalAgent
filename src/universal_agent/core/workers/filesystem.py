import logging
import os

logger = logging.getLogger(__name__)

class FilesystemWorker:
    def __init__(self, workspace_path: str):
        self.workspace_path = os.path.abspath(workspace_path)
        os.makedirs(self.workspace_path, exist_ok=True)

    def _resolve_safe_path(self, rel_path: str) -> str:
        # Resolve path safely
        abs_path = os.path.abspath(os.path.join(self.workspace_path, rel_path))
        if not abs_path.startswith(self.workspace_path):
            raise ValueError(f"Path traversal detected: {rel_path}")
        return abs_path

    def read_file(self, path: str) -> dict:
        try:
            safe_path = self._resolve_safe_path(path)
            if not os.path.isfile(safe_path):
                return {"status": "error", "error": "File not found"}
            with open(safe_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"status": "ok", "content": content}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def write_file(self, path: str, content: str) -> dict:
        try:
            safe_path = self._resolve_safe_path(path)
            os.makedirs(os.path.dirname(safe_path), exist_ok=True)
            with open(safe_path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def list_dir(self, path: str = ".") -> dict:
        try:
            safe_path = self._resolve_safe_path(path)
            if not os.path.isdir(safe_path):
                return {"status": "error", "error": "Directory not found"}
            items = os.listdir(safe_path)
            return {"status": "ok", "items": items}
        except Exception as e:
            return {"status": "error", "error": str(e)}
