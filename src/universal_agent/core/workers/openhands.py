import logging
import subprocess

logger = logging.getLogger(__name__)

class OpenHandsAdapter:
    def __init__(self):
        pass

    def detect_images(self):
        try:
            res = subprocess.run("docker images | grep openhands", shell=True, capture_output=True, text=True)
            return [line for line in res.stdout.split('\n') if line]
        except Exception:
            return []

    def check_health(self):
        images = self.detect_images()
        if not images:
            return {"status": "error", "message": "No OpenHands images found"}
        return {"status": "ok", "images": images}
