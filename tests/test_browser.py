from universal_agent.core.workers.browser import BrowserWorker


def test_browser_fallback():
    worker = BrowserWorker()
    # It should fallback to system chrome or return error but not crash
    result = worker.test_safe_page()
    assert result["status"] in ["ok", "error"]
    if result["status"] == "ok":
        assert "title" in result
