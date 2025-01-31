import os
import json
from pathlib import Path
from typing import Optional, Union, Dict, List, Any
from dotenv import load_dotenv
import asyncio
import platform
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from .mcp_client import mcp
import logging

# Load environment variables
load_dotenv()

async def brave(action: str, query: str = "", count: int = 5, offset: int = 0) -> Any:
    """
    Brave Search API with web and local search capabilities
    
    Actions:
    - web: Search the web (query, count, offset)
    - local: Search for local businesses/places (query, count)
    
    Features:
    - Web search with pagination
    - Local business/places search
    - Multiple result formats
    - Safe search options
    """
    try:
        logging.debug(f"Brave search called with: action={action}, query={query}, count={count}, offset={offset}")
        server_name = "brave-search"

        if action == "web":
            args = {
                "query": str(query),
                "count": int(count),
                "offset": int(offset)
            }
            logging.debug(f"Calling brave web search with args: {args}")
            return await mcp(
                server=server_name,
                tool="brave_web_search",
                arguments=args
            )

        elif action == "local":
            args = {
                "query": str(query),
                "count": int(count)
            }
            logging.debug(f"Calling brave local search with args: {args}")
            return await mcp(
                server=server_name,
                tool="brave_local_search",
                arguments=args
            )

        else:
            return {"error": f"Unknown Brave action '{action}'. Available actions: web, local"}
            
    except Exception as e:
        logging.error(f"Brave search error: {str(e)}", exc_info=True)
        return {"error": f"Brave search failed: {str(e)}"}

async def filesystem(action: str, path: str = "", content: str = "") -> Any:
    """
    Filesystem MCP Server for file operations within allowed directories.
    
    Actions:
    - read:   Read complete file contents (UTF-8).
    - write:  Create or overwrite a file with content.
    - list:   List contents of a directory.
    - info:   Get metadata info for a file/directory.
    - search: Recursively search for files/directories by pattern.
    - allowed: Show which directories the server is permitted to access.

    Features:
    - Read/write files
    - Create/list/delete directories
    - Move/rename files/directories
    - Search files
    - Get file metadata
    - Allowed directories can be restricted in the server config
    """
    server_name = "filesystem"

    # read a file
    if action == "read":
        return await mcp(
            server=server_name, 
            tool="read_file", 
            arguments={"path": path}
        )

    # write to a file
    elif action == "write":
        return await mcp(
            server=server_name,
            tool="write_file",
            arguments={"path": path, "content": content}
        )

    # list directory contents
    elif action == "list":
        # 'list_directory' expects a path (directory), returns file/dir listings
        return await mcp(
            server=server_name, 
            tool="list_directory",
            arguments={"path": path}
        )

    # get file info
    elif action == "info":
        # 'get_file_info' returns metadata (size, times, type, permissions, etc.)
        return await mcp(
            server=server_name,
            tool="get_file_info",
            arguments={"path": path}
        )

    # search files
    elif action == "search":
        # 'search_files' might expect a 'pattern' argument. 
        # If so, you could reuse `path` or add a new param to the function signature
        return await mcp(
            server=server_name,
            tool="search_files",
            arguments={
                "path": path,        # starting directory
                "pattern": content   # we can reuse 'content' as the pattern
            }
        )

    # show allowed directories
    elif action == "allowed":
        # 'list_allowed_directories' does not require arguments
        return await mcp(
            server=server_name,
            tool="list_allowed_directories",
            arguments={}
        )

    # unknown action
    else:
        return {
            "error": (
                f"Unknown filesystem action '{action}'. Available actions: "
                "read, write, list, info, search, allowed"
            )
        }

if __name__ == "__main__":
    async def main():
        # Test Brave
        print(await brave("help"))
        print(await brave("web", "Python programming", count=2))
        
        # Test Filesystem
        print(await filesystem("help"))
        print(await filesystem("read", "/tmp/test.txt"))

    asyncio.run(main())