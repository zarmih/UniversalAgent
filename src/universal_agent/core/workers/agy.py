import logging

from ..config import config

logger = logging.getLogger(__name__)

class AgyAdapter:
    def __init__(self):
        self.enabled = config.enable_agy_submit

    def submit_task(self, goal: str):
        if not self.enabled:
            return {"status": "error", "error": "AGY submit is disabled by configuration to prevent recursion"}
        
        # Mock actual submit logic for this MVP to avoid deep side-effects during tests
        return {"status": "succeeded", "result": "mocked AGY result"}

    def check_health(self):
        return {"status": "ok", "message": "AGY adapter is healthy"}
