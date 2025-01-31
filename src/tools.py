from typing import Dict, Optional, Union, List
import logging
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from .config import config

logging.basicConfig(level=config.log_level)
logger = logging.getLogger(__name__)

async def mcp(
    server: Optional[str] = None,
    tool: Optional[str] = None,
    arguments: Optional[Dict] = None
) -> Union[str, Dict, List]:
    """MCP tool execution with environment-aware configuration"""
    try:
        if tool == 'list_available_servers':
            servers = config.get_enabled_servers()
            return {
                'available_servers': list(servers.keys()),
                'hint': 'Use tool_details with a server name to see available tools'
            }

        if not server:
            return {
                'error': 'Server parameter required',
                'hint': 'Use list_available_servers to see available servers'
            }

        server_config = config.get_server_config(server)
        if not server_config:
            return {
                'error': f'Server {server} not found or disabled',
                'available_servers': list(config.get_enabled_servers().keys())
            }

        # Connect to server using configuration
        async with stdio_client(StdioServerParameters(
      3) To execute a specific tool on a server:
         >>> await mcp(
               server='browser', 
               tool='openUrl',
               arguments={'url': 'https://example.com'}
             )
         Returns the execution result, often JSON or a success/error message.

    NOTE:
      - **All** actions (listing servers, discovering tools, running any tool) must be
        performed via `mcp`. There are no other functions you should call to interact
        with the underlying servers or tools.
      - If a server requires configuration or environment variables, load them through
        the config file or pass them in the `config_path`. `mcp` will handle everything.

    PARAMETERS:
      server (str, optional):
        The name of the target server. Required for step (2) and step (3).
      tool (str, optional):
        The action/command to run, which can be:
          - 'list_available_servers' to discover all servers (Step 1).
          - 'tool_details' to list all tools within a chosen server (Step 2).
          - An actual tool name (e.g., 'openUrl', 'writeFile', etc.) (Step 3).
      arguments (Dict, optional):
        A dictionary of arguments required by the tool for execution. 
        For instance, {'url': 'https://example.com'} for openUrl.
      config_path (str or Path, optional):
        An explicit path to a config file if not using the default search locations.

    RETURNS:
      Union[str, Dict, List]:
        - JSON-encoded string or dictionary containing results, errors, or hints.
        - For server- or tool-listing, a JSON string with structured data.
        - For actual tool execution, the raw (stringified) result from the tool.

    IMPORTANT:
      - This function must be used for every single request or command. 
      - Avoid calling lower-level server or tool APIs directly—always go through MCP.

    RAISES:
      Exception: If any errors occur in loading configuration, connecting to the server,
                 or executing the tool.
    ----------------------------------------------------------------------------------------
    """
    try:
        # Set up logging for debugging config path
        logging.debug(f"Input config_path: {config_path}")
        
        # Get project root (parent of src directory)
        project_root = Path(__file__).parent.parent
        
        # Check config locations
        search_paths = []
        if config_path:
            search_paths.append(Path(config_path))
        else:
            search_paths.extend([
                project_root / 'mcp_config.json',  # Project root
                Path.cwd() / 'mcp_config.json',    # Current working directory
                Path.home() / '.config' / 'autogen' / 'mcp_config.json',  # User config
            ])
        
        # Log all paths being checked
        logging.debug(f"Project root: {project_root}")
        logging.debug(f"Current working directory: {Path.cwd()}")
        logging.debug(f"Searching config in paths: {search_paths}")
        
        # Find first existing config file
        found_config = None
        for path in search_paths:
            logging.debug(f"Checking path: {path} - Exists: {path.exists()}")
            if path.exists():
                found_config = path
                break
        
        if not found_config:
            paths_checked = '\n'.join(str(p) for p in search_paths)
            error_msg = f"Error: No configuration file found. Checked:\n{paths_checked}"
            logging.error(error_msg)
            return error_msg

        logging.debug(f"Using config file: {found_config}")
        
        # Determine system-specific npx path
        system = platform.system()
        if system == "Darwin":  # macOS
            default_npx = Path("/opt/homebrew/bin/npx")
        elif system == "Windows":
            default_npx = Path(os.getenv("APPDATA", "")) / "npm/npx.cmd"
        else:  # Linux/Other
            default_npx = Path("/usr/local/bin/npx")

        # Fallback to just "npx" if default doesn't exist
        npx_path = str(default_npx if default_npx.exists() else "npx")

        # Load config data
        with open(found_config) as f:
            config_data = json.load(f)
            servers = config_data.get('mcpServers', {})

        # 1) Discovery of all servers
        if tool == 'list_available_servers':
            enabled_servers = [name for name, cfg in servers.items() if cfg.get('enabled', True)]
            return json.dumps({
                'available_servers': enabled_servers,
                'hint': 'Use tool_details with a server name to see available tools'
            }, indent=2)

        # 2) Listing tools for a specific server
        if tool == 'tool_details' and not server:
            return json.dumps({
                'error': 'Server parameter required for tool_details',
                'hint': 'First use list_available_servers to see available servers',
                'available_servers': [name for name, cfg in servers.items() if cfg.get('enabled', True)]
            }, indent=2)

        # If user didn’t specify a server for actual tool execution
        if not server:
            return json.dumps({
                'error': 'Server parameter required',
                'hint': 'Use list_available_servers to see available servers'
            }, indent=2)
        
        # Validate server name
        if server not in servers:
            return json.dumps({
                'error': f'Server {server} not found',
                'available_servers': [name for name, cfg in servers.items() if cfg.get('enabled', True)],
                'hint': 'Use one of the available servers listed above'
            }, indent=2)

        # Build connection parameters
        config = servers[server]
        command = npx_path if config['command'] == 'npx' else config['command']
        env = os.environ.copy()
        env.update(config.get('env', {}))
        arguments = arguments or {}

        # Connect to server
        async with stdio_client(StdioServerParameters(
            command=command, 
            args=config.get('args', []), 
            env=env
        )) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 2a) Return tool details for a server
                if tool == 'tool_details':
                    result = await session.list_tools()
                    return json.dumps({
                        'server': server,
                        'available_tools': [{
                            'name': t.name,
                            'description': t.description,
                            'input_schema': t.inputSchema
                        } for t in result.tools],
                        'hint': 'Use these tool names with this server to execute commands'
                    }, indent=2)

                # 3) Execute actual tool
                if not tool:
                    return "Error: Tool name required"

                result = await session.call_tool(tool, arguments=arguments)
                return str(result)

    except Exception as e:
        return f"Error: {str(e)}"