import logging
import os

logger = logging.getLogger(__name__)

class FilesystemWorker:
    def __init__(self, allowed_roots=None):
        self.allowed_roots = allowed_roots or ["/mnt/SDD_1.7_TB/UniversalAgent"]

    def read_file(self, path: str):
        for root in self.allowed_roots:
            if os.path.abspath(path).startswith(os.path.abspath(root)):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        return {"content": f.read(), "status": "ok"}
                except Exception as e:
                    return {"status": "error", "error": str(e)}
        return {"status": "error", "error": "Access denied outside allowed roots"}
