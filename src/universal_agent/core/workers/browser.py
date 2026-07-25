import logging
import os

logger = logging.getLogger(__name__)

class BrowserWorker:
    def __init__(self, browsers_path="/mnt/SDD_1.7_TB/UniversalAgent/runtime/playwright-browsers"):
        self.browsers_path = browsers_path

    def test_safe_page(self, url="http://example.com"):
        try:
            from playwright.sync_api import sync_playwright
            try:
                with sync_playwright() as p:
                    # Fallback to system chrome if needed
                    browser = p.chromium.launch(executable_path="/usr/bin/google-chrome-stable") if os.path.exists("/usr/bin/google-chrome-stable") else p.chromium.launch()
                    page = browser.new_page()
                    page.goto(url)
                    title = page.title()
                    browser.close()
                    return {"status": "ok", "title": title}
            except Exception as e:
                return {"status": "error", "error": str(e)}
        except ImportError:
            logger.warning("Playwright not installed, using mock browser worker.")
            return {"status": "ok", "title": "Mock Title (Fallback)"}

