from typing import Any, Dict
from .base import BaseTool
from ..mcp_client import mcp

class FilesystemTool(BaseTool):
    @property
    def name(self) -> str:
        return "filesystem"
        
    @property
    def description(self) -> str:
        return "File system operations: read, write, list, search files and directories"
        
    @property
    def parameters(self) -> Dict:
        return {
            "action": {
                "type": "string",
                "enum": ["read", "write", "list", "info", "search", "allowed"],
                "description": "File operation to perform"
            },
            "path": {
                "type": "string", 
                "description": "File/directory path"
            },
            "content": {
                "type": "string",
                "description": "Content to write or search pattern"
            }
        }
        
    async def execute(self, action: str, path: str = "", content: str = "") -> Any:
        """Execute filesystem operations via MCP"""
        server_name = "filesystem"
        
        tool_map = {
            "read": "read_file",
            "write": "write_file", 
            "list": "list_directory",
            "info": "get_file_info",
            "search": "search_files",
            "allowed": "list_allowed_directories"
        }
        
        if action not in tool_map:
            return {"error": f"Unknown action '{action}'. Available: {', '.join(tool_map.keys())}"}
            
        args = {"path": path}
        if action == "write":
            args["content"] = content
        elif action == "search":
            args["pattern"] = content
        elif action == "allowed":
            args = {}
            
        return await mcp(server=server_name, tool=tool_map[action], arguments=args)
