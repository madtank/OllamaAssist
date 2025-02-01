# OllamaAssist

A Streamlit interface for Ollama models with full MCP (Model Context Protocol) integration. Works with any tool-calling capable model like deepseek-r1-tool-calling:14b or llama2:latest.

## Key Features

- **Local LLM Execution**: Run models locally using Ollama (deepseek-r1)
- **MCP Integration**: Universal tool protocol support
- **Streamlit Interface**: Real-time streaming chat interface
- **Dynamic Tool Support**: Automatic capability detection

## What is MCP (Model Context Protocol)?

[MCP](https://modelcontextprotocol.io) is a universal protocol that standardizes how AI models interact with tools and services. It provides:

- **Universal Tool Interface**: Common protocol for all AI tools
- **Standardized Messages**: Consistent communication format
- **Discoverable Capabilities**: Self-describing tools and services
- **Language Agnostic**: Works with any programming language
- **Growing Ecosystem**: [Many tools available](https://github.com/modelcontextprotocol/servers)

Learn more:
- [MCP Documentation](https://modelcontextprotocol.io)
- [MCP Specification](https://spec.modelcontextprotocol.io)
- [Official Servers](https://github.com/modelcontextprotocol/servers)

## Prerequisites

- Python 3.9+
- Ollama desktop app installed and running
- MCP-compatible tools
- python-dotenv
- An Ollama-compatible model with tool-calling support

## Installation

1. Prerequisites:
   ```bash
   # Install Ollama desktop app from https://ollama.ai/download
   
   # Make sure Ollama is running
   # Then pull the recommended model (or choose another tool-calling capable model)
   ollama pull MFDoom/deepseek-r1-tool-calling:14b
   
   # Alternative models that support tool calling:
   # ollama pull llama2:latest
   ```

2. Setup:
   ```bash
   git clone https://github.com/madtank/OllamaAssist.git
   cd OllamaAssist
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Environment Configuration

OllamaAssist uses environment variables for configuration. Create a `.env` file:

```properties
# Brave Search Configuration
BRAVE_API_KEY=your_api_key_here

# Optional: Override default commands
#BRAVE_COMMAND=docker
#BRAVE_ARGS=run -i --rm -e BRAVE_API_KEY mcp/brave-search

# Filesystem Configuration
#FILESYSTEM_PATHS=/path1:/path2:/path3
```

Variables can be:
- Set in .env file
- Commented out to use defaults
- Override using environment variables

## MCP Configuration

OllamaAssist uses MCP to provide powerful capabilities through standardized tools. Configure available tools in `mcp_config.json`:

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your-api-key-here"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"]
    }
  }
}
```

### Available MCP Servers

The project supports various MCP servers:

#### Core Functionality
- **brave-search** - Web and local search capabilities
- **filesystem** - Secure file operations
- **chromadb** - Vector database operations
- **postgres** - SQL database integration
- **mcp-memory** - Long-term context persistence
- **sqlite** - Lightweight database operations

#### AI & Development
- **huggingface** - Model and dataset access
- **langchain** - AI workflow integration
- **git** - Repository operations
- **jupyter** - Notebook integration

Check out [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers) for more.

### Adding MCP Servers

1. Each server entry needs:
   - `command`: The MCP tool executable
   - `args`: Optional command line arguments
   - `env`: Environment variables (like API keys)

2. Common MCP servers:
   - `brave-search`: Web search (requires Brave API key)
   - `filesystem`: Local file operations
   - `sequential-thinking`: Self-reflection capabilities
   - Add your own MCP-compatible tools!

### Configuring API Keys

For services requiring authentication:

1. Get your API key (e.g., Brave Search API)
2. Add it to the appropriate server's `env` section
3. Never commit API keys to version control

## Using MCP Tools

Example tool implementation:
```python
async def brave(action: str, query: str = "", count: int = 5) -> Any:
    """Brave Search API wrapper"""
    server_name = "brave-search"
    return await mcp(
        server=server_name,
        tool=f"brave_{action}_search",
        arguments={"query": query, "count": count}
    )
```

## Adding Custom MCP Tools

1. Create an MCP-compatible tool
2. Add it to `mcp_config.json`
3. The tool will be automatically available to the chatbot

## Running the Application

1. Ensure Ollama desktop app is running
2. Launch OllamaAssist:
   ```bash
   streamlit run streamlit_app.py
   ```

## Testing

Run tests:
```bash
python -m pytest tests/test_tools.py -v
```

## Development

### Creating MCP Tools

Want to create your own MCP tool? Follow these guides:
- [Building MCP Servers](https://modelcontextprotocol.io/docs/build-server)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Server Examples](https://github.com/modelcontextprotocol/servers/tree/main/examples)

### Testing MCP Tools

Use the MCP Inspector to test your tools:
```bash
mcp dev your_server.py
```

Or install in Claude Desktop:
```bash
mcp install your_server.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Test your changes
4. Submit a pull request

## Roadmap

- [ ] Additional MCP server integrations
- [ ] Enhanced model capability detection
- [ ] Advanced tool chaining
- [ ] UI improvements for tool interactions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [MCP](https://github.com/llmOS/mcp) for the universal tool protocol
- [Ollama](https://github.com/jmorganca/ollama) for local LLM execution
- [Streamlit](https://streamlit.io/) for the web interface