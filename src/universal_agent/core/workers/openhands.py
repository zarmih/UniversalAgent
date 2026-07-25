import logging
import subprocess

from ..config import config

logger = logging.getLogger(__name__)

class OpenHandsAdapter:
    def __init__(self):
        self.enabled = config.enable_openhands_run

    def detect_images(self):
        try:
            # We strictly pass shell=False now for safety
            res = subprocess.run(["docker", "images"], capture_output=True, text=True, check=False)
            if res.returncode == 0:
                lines = res.stdout.split('\n')
                return [line for line in lines if "openhands" in line]
            return []
        except Exception as e:
            logger.error(f"Failed to detect OpenHands images: {e}")
            return []

    def check_health(self):
        images = self.detect_images()
        if not images:
            return {"status": "error", "message": "No OpenHands images found"}
        return {"status": "ok", "images": images}
