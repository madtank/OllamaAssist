import os
import json
import ollama
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class Config:
    # Application settings
    PAGE_TITLE = "Streamlit AI Chatbot with Ollama Integration"
    DEFAULT_MODEL = "MFDoom/deepseek-r1-tool-calling:14b"

    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize config paths
        self.project_root = Path(__file__).parent.parent
        self.config_file = self.project_root / 'mcp_config.json'
        
        # Load MCP config
        self.mcp_config = self._load_mcp_config()
        
        # Initialize Ollama models
        self._init_ollama_models()
        
        # Apply environment overrides
        self._apply_env_overrides()

    def _init_ollama_models(self):
        """Initialize available Ollama models"""
        try:
            models_info = ollama.list()
            self.OLLAMA_MODELS = tuple(model['model'] for model in models_info['models'])
            
            # Validate default model
            if self.DEFAULT_MODEL not in self.OLLAMA_MODELS and self.OLLAMA_MODELS:
                self.DEFAULT_MODEL = self.OLLAMA_MODELS[0]
        except Exception as e:
            self.OLLAMA_MODELS = (self.DEFAULT_MODEL,)
            
    def _load_mcp_config(self) -> Dict[str, Any]:
        """Load MCP server configuration from JSON"""
        if not self.config_file.exists():
            return {"mcpServers": {}}
            
        with open(self.config_file) as f:
            return json.load(f)

    def _apply_env_overrides(self):
        """Apply environment variable overrides to server configs"""
        servers = self.mcp_config.get('mcpServers', {})
        
        for server_name, config in servers.items():
            prefix = f"{server_name.upper().replace('-', '_')}_"
            
            # Override enabled status
            if os.getenv(f"{prefix}ENABLED"):
                config['enabled'] = os.getenv(f"{prefix}ENABLED").lower() == 'true'
            
            # Override command
            if os.getenv(f"{prefix}COMMAND"):
                config['command'] = os.getenv(f"{prefix}COMMAND")
            
            # Override args
            if os.getenv(f"{prefix}ARGS"):
                config['args'] = os.getenv(f"{prefix}ARGS").split()
            
            # Add/override environment variables
            if 'env' not in config:
                config['env'] = {}
                
            # Special handling for API keys and paths
            if server_name == 'brave-search' and os.getenv('BRAVE_API_KEY'):
                config['env']['BRAVE_API_KEY'] = os.getenv('BRAVE_API_KEY')
            elif server_name == 'filesystem' and os.getenv('FILESYSTEM_PATHS'):
                paths = os.getenv('FILESYSTEM_PATHS').split(':')
                config['args'] = ['-y', '@modelcontextprotocol/server-filesystem'] + paths

    def get_server_config(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific server"""
        return self.mcp_config.get('mcpServers', {}).get(server_name)

    def get_enabled_servers(self) -> Dict[str, Dict[str, Any]]:
        """Get all enabled server configurations"""
        return {
            name: config 
            for name, config in self.mcp_config.get('mcpServers', {}).items() 
            if config.get('enabled', True)
        }

    @property
    def debug(self) -> bool:
        """Get debug mode status"""
        return os.getenv('DEBUG', 'false').lower() == 'true'

    @property
    def log_level(self) -> str:
        """Get logging level"""
        return os.getenv('LOG_LEVEL', 'INFO')

# Create global config instance
config = Config()