from universal_agent.core.workers.agy import AgyAdapter
from universal_agent.core.workers.browser import BrowserWorker
from universal_agent.core.workers.filesystem import FilesystemWorker
from universal_agent.core.workers.llm import LLMWorker
from universal_agent.core.workers.openhands import OpenHandsAdapter
from universal_agent.core.workers.shell import ShellWorker


def test_shell_worker_allowlist(tmp_path):
    worker = ShellWorker(str(tmp_path))
    # Allowed
    assert worker.is_safe_command(["ls", "-la"]) == True
    # Disallowed command
    assert worker.is_safe_command(["rm", "-rf", "/"]) == False
    # Dangerous chars
    assert worker.is_safe_command(["ls", ";", "echo"]) == False
    # Path escape
    assert worker.is_safe_command(["cat", "/etc/passwd"]) == False
    
    res = worker.execute(["pwd"])
    assert res["status"] == "ok"
    assert str(tmp_path) in res["stdout"]

def test_filesystem_traversal(tmp_path):
    worker = FilesystemWorker(str(tmp_path))
    # Safe
    res = worker.write_file("test.txt", "hello")
    assert res["status"] == "ok"
    res2 = worker.read_file("test.txt")
    assert res2["content"] == "hello"
    
    # Path traversal block
    res3 = worker.read_file("../../../etc/passwd")
    assert res3["status"] == "error"
    assert "traversal" in res3["error"]

def test_browser_policy():
    worker = BrowserWorker()
    assert worker.is_allowed_url("data:text/html,<h1>hi</h1>") == True
    assert worker.is_allowed_url("http://127.0.0.1:8765") == True
    # Default config blocks external
    assert worker.is_allowed_url("http://example.com") == False

def test_browser_fallback_local():
    worker = BrowserWorker()
    # Mocking url that is allowed
    res = worker.test_safe_page("data:text/html,<title>SafeTest</title>")
    assert res["status"] in ["ok", "error"]
    if res["status"] == "ok":
        assert "SafeTest" in res.get("title", "")

def test_openhands_mock():
    worker = OpenHandsAdapter()
    res = worker.check_health()
    # Either ok or error if no images, but it shouldn't crash
    assert res["status"] in ["ok", "error"]

def test_llm_mock():
    worker = LLMWorker()
    # Assume mock endpoints would be used or we just assert initialized
    assert worker.model_name == "local-llama"

def test_agy_mock():
    worker = AgyAdapter()
    # It should be disabled by default config
    assert worker.enabled == False
    res = worker.submit("test", require_approval=False)
    assert res["status"] == "error"
