from unittest.mock import MagicMock, patch

from universal_agent.core.workers.llm import LLMWorker


def test_llm_disabled():
    worker = LLMWorker()
    worker.enabled = False
    res = worker.generate("hello")
    assert res["status"] == "error"
    assert "disabled" in res["error"]

def test_llm_health_ok(monkeypatch):
    worker = LLMWorker()
    worker.enabled = True
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_res = MagicMock()
        mock_res.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_res
        
        res = worker.check_health()
        assert res["status"] == "ok"

def test_llm_generate_ok(monkeypatch):
    worker = LLMWorker()
    worker.enabled = True
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_res = MagicMock()
        mock_res.read.return_value = b'{"choices": [{"message": {"content": "mock completion"}}]}'
        mock_urlopen.return_value.__enter__.return_value = mock_res
        
        res = worker.generate("hello")
        assert res["status"] == "ok"
        assert res["completion"] == "mock completion"

def test_llm_generate_error(monkeypatch):
    worker = LLMWorker()
    worker.enabled = True
    with patch("urllib.request.urlopen", side_effect=Exception("mock error")):
        res = worker.generate("hello")
        assert res["status"] == "error"
        assert "mock error" in res["error"]
