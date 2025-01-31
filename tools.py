import os
import json
from pathlib import Path
from typing import Optional, Union, Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def mcp(
    server: Optional[str] = None,
    tool: Optional[str] = None,
    arguments: Optional[Dict] = None,
    config_path: Optional[Union[str, Path]] = None
) -> Union[str, Dict, List]:
    try:
        # Load config data
        with open(found_config) as f:
            config_data = json.load(f)
            servers = config_data.get('mcpServers', {})

        # Override config with environment variables
        for server_name, server_config in servers.items():
            env_prefix = f"{server_name.upper().replace('-', '_')}_"
            if os.getenv(f"{env_prefix}COMMAND"):
                server_config['command'] = os.getenv(f"{env_prefix}COMMAND")
            if os.getenv(f"{env_prefix}ARGS"):
                server_config['args'] = os.getenv(f"{env_prefix}ARGS").split()
            if 'env' not in server_config:
                server_config['env'] = {}
            # Add any ENV_ prefixed variables
            for key, value in os.environ.items():
                if key.startswith(f"{env_prefix}ENV_"):
                    env_key = key.replace(f"{env_prefix}ENV_", "")
                    server_config['env'][env_key] = value

        # Rest of the existing code...
