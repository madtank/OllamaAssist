import json
import os
import platform
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import logging

# Load environment variables at module level
load_dotenv()

from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

def get_server_config() -> Dict[str, Dict]:
    brave_command = os.getenv("BRAVE_SEARCH_COMMAND", "npx")
    brave_args = os.getenv("BRAVE_SEARCH_ARGS", "-y @modelcontextprotocol/server-brave-search").split()
    filesystem_command = os.getenv("FILESYSTEM_COMMAND", "mcp-filesystem-server")
    filesystem_args_env = os.getenv("FILESYSTEM_ARGS")
    filesystem_args = filesystem_args_env.split() if filesystem_args_env else ["/Users/username/Desktop"]
    
    return {
        "brave-search": {
            "command": brave_command,
            "args": brave_args,
            "env": {"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY", "")}
        },
        "filesystem": {
            "command": filesystem_command,
            "args": filesystem_args,
            "env": {}
        }
    }

async def mcp(
    server: str,
    tool: str,
    arguments: Optional[Dict] = None
) -> Any:
    """Main MCP function to communicate with servers."""
    try:
        if tool == "list_available_servers":
            async with stdio_client(StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/cli"],
                env=os.environ.copy()
            )) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool("list_available_servers")
                    return json.loads(result) if isinstance(result, str) else result

        servers = get_server_config()
        if server not in servers:
            return {"error": f"Server {server} not found. Known servers: {list(servers.keys())}"}
            
        config = servers[server]
        env = os.environ.copy()
        env.update(config.get("env", {}))
        
        async with stdio_client(StdioServerParameters(
            command=config["command"],
            args=config["args"],
            env=env
        )) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool, arguments=arguments or {})
                return json.loads(result) if isinstance(result, str) else result
                
    except Exception as e:
        logging.error(f"MCP error: {str(e)}", exc_info=True)
        return {"error": f"MCP operation failed: {str(e)}"}
