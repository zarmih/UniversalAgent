import logging

logger = logging.getLogger(__name__)

class BrowserWorker:
    def __init__(self, browsers_path="/mnt/SDD_1.7_TB/UniversalAgent/runtime/playwright-browsers"):
        self.browsers_path = browsers_path

    def test_safe_page(self, url="http://example.com"):
        from playwright.sync_api import sync_playwright
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(url)
                title = page.title()
                browser.close()
                return {"status": "ok", "title": title}
        except Exception as e:
            return {"status": "error", "error": str(e)}
