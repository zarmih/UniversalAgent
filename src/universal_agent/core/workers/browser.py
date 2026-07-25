import logging
import os
import subprocess

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

