import os

from pydantic import BaseModel


class AppConfig(BaseModel):
    project_root: str = "/mnt/SDD_1.7_TB/UniversalAgent"
    data_dir: str = "/mnt/SDD_1.7_TB/UniversalAgent/data"
    workspaces_dir: str = "/mnt/SDD_1.7_TB/UniversalAgent/workspaces"
    db_path: str = "/mnt/SDD_1.7_TB/UniversalAgent/data/universal_agent.db"
    port: int = 8765
    host: str = "127.0.0.1"
    
    # Feature flags
    enable_agy_submit: bool = False
    enable_openhands_run: bool = False
    allow_external_network: bool = False

config = AppConfig()

# Ensure directories exist
os.makedirs(config.data_dir, exist_ok=True)
os.makedirs(config.workspaces_dir, exist_ok=True)
