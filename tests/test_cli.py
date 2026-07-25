import subprocess


def test_cli_health():
    cli_path = "/mnt/SDD_1.7_TB/UniversalAgent/scripts/ua"
    res = subprocess.run([cli_path, "health"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "status" in res.stdout

def test_cli_create_task():
    cli_path = "/mnt/SDD_1.7_TB/UniversalAgent/scripts/ua"
    res = subprocess.run([cli_path, "create", "test cli task"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "queued" in res.stdout
