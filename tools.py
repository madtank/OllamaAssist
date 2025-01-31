"""Tools module for OllamaAssist.
Provides simplified interfaces to MCP servers."""

from typing import Any
from src.mcp_client import mcp
import logging
from pathlib import Path

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
    """Filesystem operations wrapper for MCP filesystem server.
    
    Actions:
    - read_file: Read contents of a file
    - write_file: Write content to a file
    - list_directory: List contents of a directory
    - get_file_info: Get metadata about a file
    - search_files: Search for files matching pattern
    - list_allowed_directories: Show accessible directories
    """
    try:
        server_name = "filesystem"
        
        # Handle list_allowed_directories separately since it needs no path
        if action == "list_allowed_directories":
            return await mcp(server=server_name, tool=action, arguments={})
            
        # For all other actions, validate path if provided
        if path:
            # Get allowed directories first
            allowed_dirs = await mcp(server=server_name, tool="list_allowed_directories", arguments={})
            if "error" in allowed_dirs:
                return allowed_dirs
                
            # Check if path is within allowed directories
            path_obj = Path(path).resolve()
            if not any(str(path_obj).startswith(str(Path(allowed_dir).resolve())) 
                      for allowed_dir in allowed_dirs.get("directories", [])):
                return {"error": f"Path '{path}' is not in allowed directories"}

        # Handle specific tools directly
        if action == "read_file":
            return await mcp(server=server_name, tool=action, arguments={"path": path})
            
        elif action == "write_file":
            return await mcp(server=server_name, tool=action, 
                           arguments={"path": path, "content": content})
            
        elif action == "list_directory":
            return await mcp(server=server_name, tool=action, arguments={"path": path or "."})
            
        elif action == "get_file_info":
            return await mcp(server=server_name, tool=action, arguments={"path": path})
            
        elif action == "search_files":
            return await mcp(server=server_name, tool=action, 
                           arguments={"path": path, "pattern": content})
        
        else:
            return {
                "error": f"Unknown action '{action}'. Available actions: read_file, write_file, "
                        "list_directory, get_file_info, search_files, list_allowed_directories"
            }

    except Exception as e:
        logging.error(f"Filesystem operation error: {str(e)}", exc_info=True)
        return {"error": f"Filesystem operation failed: {str(e)}"}