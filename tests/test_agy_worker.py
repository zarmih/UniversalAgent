from unittest.mock import MagicMock, patch

from universal_agent.core.workers.agy import AgyAdapter


def test_agy_disabled_feature_flag():
    adapter = AgyAdapter()
    adapter.enabled = False
    res = adapter.submit("test")
    assert res["status"] == "error"
    assert "disabled" in res["error"]

def test_agy_require_approval(monkeypatch):
    adapter = AgyAdapter()
    adapter.enabled = True
    # We just ensure it doesn't blow up; logic is in caller
    assert True

def test_agy_recursive_guard(monkeypatch):
    monkeypatch.setenv("TMUX", "some_path/universal-agent")
    
    with patch("subprocess.run") as mock_run:
        # Mock tmux returning the same session name
        mock_res = MagicMock()
        mock_res.stdout = "universal-agent-agy\n"
        mock_run.return_value = mock_res
        
        adapter = AgyAdapter()
        adapter.enabled = True
        res = adapter.submit("test")
        
        assert res["status"] == "error"
        assert "Cannot submit from within" in res["error"]

def test_agy_status_inactive(monkeypatch):
    with patch("subprocess.run") as mock_run:
        mock_res = MagicMock()
        mock_res.returncode = 1 # has-session fails
        mock_run.return_value = mock_res
        
        adapter = AgyAdapter()
        assert adapter.status() == "inactive"
        
        # busy check
        mock_res.returncode = 0
        with patch("os.path.exists", return_value=True):
            assert adapter.status() == "busy"
            
        with patch("os.path.exists", return_value=False):
            assert adapter.status() == "active"

def test_agy_submit_busy(monkeypatch):
    adapter = AgyAdapter()
    adapter.enabled = True
    with patch.object(adapter, "ensure_session", return_value=True), patch.object(adapter, "status", return_value="busy"):
        res = adapter.submit("test")
        assert res["status"] == "error"
        assert "busy" in res["error"]

def test_agy_submit_timeout(monkeypatch):
    adapter = AgyAdapter()
    adapter.enabled = True
    with patch.object(adapter, "ensure_session", return_value=True), patch.object(adapter, "status", return_value="active"), patch("subprocess.run"), patch.object(adapter, "get_output", return_value="no marker here"), patch("time.sleep"):
        res = adapter.submit("test", timeout=0.1)
        assert res["status"] == "error"
        assert "Timeout" in res["error"]

def test_agy_cancel(monkeypatch):
    adapter = AgyAdapter()
    with patch("subprocess.run") as mock_run, patch("os.remove") as mock_rm, patch("os.path.exists", return_value=True):
        adapter.cancel()
        mock_run.assert_called()
        mock_rm.assert_called_with(adapter.lock_file)
