"""Tools module for OllamaAssist.
Provides simplified interfaces to MCP servers."""

from typing import Any
from src.mcp_client import mcp
import logging

async def brave(action: str, query: str = "", count: int = 5, offset: int = 0) -> Any:
    """Brave Search API wrapper"""
    try:
        logging.debug(f"Brave search called with: action={action}, query={query}, count={count}, offset={offset}")
        server_name = "brave-search"

        if action == "web":
            return await mcp(
                server=server_name,
                tool="brave_web_search",
                arguments={
                    "query": str(query),
                    "count": int(count),
                    "offset": int(offset)
                }
            )

        elif action == "local":
            return await mcp(
                server=server_name,
                tool="brave_local_search",
                arguments={
                    "query": str(query),
                    "count": int(count)
                }
            )

        else:
            return {"error": f"Unknown Brave action '{action}'. Available actions: web, local"}
            
    except Exception as e:
        logging.error(f"Brave search error: {str(e)}", exc_info=True)
        return {"error": f"Brave search failed: {str(e)}"}

async def filesystem(action: str, path: str = "", content: str = "") -> Any:
    """Filesystem operations wrapper.
    Maps simple action names to MCP filesystem server tools.
    
    Actions:
    - read: Read a file (maps to read_file)
    - write: Write to a file (maps to write_file)
    - list: List directory contents (maps to list_directory)
    - info: Get file info (maps to get_file_info)
    - search: Search for files (maps to search_files)
    - allowed: Show allowed directories (maps to list_allowed_directories)
    """
    try:
        server_name = "filesystem"
        
        # Map simple actions to MCP tool names
        tool_map = {
            "read": "read_file",
            "write": "write_file",
            "list": "list_directory",
            "info": "get_file_info",
            "search": "search_files",
            "allowed": "list_allowed_directories"
        }

        if action not in tool_map:
            return {
                "error": f"Unknown filesystem action '{action}'. Available actions: {', '.join(tool_map.keys())}"
            }

        # Build arguments based on the tool
        tool = tool_map[action]
        arguments = {}

        if tool == "read_file":
            arguments = {"path": path}
        elif tool == "write_file":
            arguments = {"path": path, "content": content}
        elif tool in ["list_directory", "get_file_info"]:
            arguments = {"path": path}
        elif tool == "search_files":
            arguments = {"path": path, "pattern": content}
        # list_allowed_directories needs no arguments

        return await mcp(server=server_name, tool=tool, arguments=arguments)

    except Exception as e:
        logging.error(f"Filesystem operation error: {str(e)}", exc_info=True)
        return {"error": f"Filesystem operation failed: {str(e)}"}