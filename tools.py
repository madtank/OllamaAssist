import os
import json
from pathlib import Path
from typing import Optional, Union, Dict, List, Any
from dotenv import load_dotenv
import asyncio
import platform
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()

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
            "env": {
                "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY", "")
            }
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
) -> Union[str, Dict, Any]:
    """
    Main MCP function to communicate with servers.
    
    Special handling:
    - For tool="list_available_servers": ignores server parameter
    - For tool="tool_details": requires valid server parameter
    """
    if tool == "list_available_servers":
        # Special case: list_available_servers is a top-level command
        # that doesn't need/use the server parameter
        async with stdio_client(StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/cli"],
            env=os.environ.copy()
        )) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("list_available_servers")
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    return result

    # Normal case: requires a valid server
    servers = get_server_config()
    if server not in servers:
        return {"error": f"Server {server} not found. Known servers: {list(servers.keys())}"}
    config = servers[server]
    command = config["command"]
    args = config["args"]
    env = os.environ.copy()
    env.update(config.get("env", {}))
    if command == "npx" and platform.system() == "Darwin":
        pass
    async with stdio_client(StdioServerParameters(command=command, args=args, env=env)) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool, arguments=arguments or {})
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return result

async def brave(action: str, query: str = "", count: int = 5, offset: int = 0) -> Any:
    """
    Brave function with subcommands: 'help', 'web', 'local'
    Example usage:
      await brave("help")
      await brave("web", "AI breakthroughs", count=3, offset=0)
      await brave("local", "best pizza")
    """
    server_name = "brave-search"

    if action == "help":
        return await mcp(server=server_name, tool="tool_details")

    elif action == "web":
        return await mcp(
            server=server_name,
            tool="brave_web_search",
            arguments={"query": query, "count": count, "offset": offset}
        )

    elif action == "local":
        return await mcp(
            server=server_name,
            tool="brave_local_search",
            arguments={"query": query, "count": count}
        )

    else:
        return {"error": f"Unknown Brave action '{action}'. Try 'help', 'web', or 'local'."}

async def filesystem(action: str, path: str = "", content: str = "") -> Any:
    """
    Filesystem function with subcommands: 'help', 'read', 'write'
    Example usage:
      await filesystem("help")
      await filesystem("read", "/some/file.txt")
      await filesystem("write", "/some/file.txt", "Hello world")
    """
    server_name = "filesystem"

    if action == "help":
        return await mcp(server=server_name, tool="tool_details")

    elif action == "read":
        return await mcp(server=server_name, tool="read_file", arguments={"path": path})

    elif action == "write":
        return await mcp(server=server_name, tool="write_file", arguments={
            "path": path,
            "content": content
        })

    else:
        return {"error": f"Unknown filesystem action '{action}'. Try 'help', 'read', 'write'."}

if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Test Brave
        print(await brave("help"))
        print(await brave("web", "Python programming", count=2))
        
        # Test Filesystem
        print(await filesystem("help"))
        print(await filesystem("read", "/tmp/test.txt"))

    asyncio.run(main())
