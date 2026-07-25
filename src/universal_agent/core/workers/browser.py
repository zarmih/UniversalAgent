import logging
import os
import subprocess
from urllib.parse import urlparse

from ..config import config

logger = logging.getLogger(__name__)

class BrowserWorker:
    def __init__(self):
        self.allow_external = config.allow_external_network

    def is_allowed_url(self, url: str) -> bool:
        if url.startswith("data:"):
            return True
        parsed = urlparse(url)
        if parsed.hostname in ["127.0.0.1", "localhost"]:
            return True
        return self.allow_external

    def test_safe_page(self, url="http://example.com"):
        if not self.is_allowed_url(url):
            return {"status": "error", "error": "External network blocked by policy"}
            
        logger.warning("Playwright not installed, trying system chrome via subprocess.")
        chrome_paths = ["/usr/bin/google-chrome", "/snap/bin/chromium", "/usr/bin/google-chrome-stable", "/usr/bin/chromium-browser"]
        for cp in chrome_paths:
            if os.path.exists(cp):
                try:
                    res = subprocess.run(
                        [cp, "--headless", "--disable-gpu", "--dump-dom", url],
                        capture_output=True, text=True, check=False, timeout=10
                    )
                    if res.returncode == 0:
                        # Parse a primitive title tag
                        title = "No Title"
                        if "<title>" in res.stdout:
                            title = res.stdout.split("<title>")[1].split("</title>")[0]
                        return {"status": "ok", "title": title}
                except Exception as e:
                    return {"status": "error", "error": str(e)}
        return {"status": "error", "error": "Playwright missing and no system chrome found"}
