# OllamaAssist

OllamaAssist is a chatbot application that combines Ollama's local LLM capabilities with MCP (Modular Command Protocol) - a universal tool protocol for LLMs. Think of MCP as "USB for AI tools" - it provides a standardized way for LLMs to interact with various tools and services.

## Key Features

- **Local LLM Execution**: Run models locally using Ollama
- **MCP Integration**: Universal tool protocol support
- **Streamlit Interface**: Easy-to-use chat interface
- **Function Calling**: Enhanced with MCP's tool ecosystem

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
- Ollama installed and running
- MCP-compatible tools you wish to use
- python-dotenv

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/madtank/OllamaAssist.git
   cd OllamaAssist
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
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

MCP has a growing ecosystem of tools. Some popular ones include:

| Server | Purpose | Package |
|--------|----------|---------|
| brave-search | Web & local search | @modelcontextprotocol/server-brave-search |
| filesystem | File operations | @modelcontextprotocol/server-filesystem |
| sequential-thinking | Structured reasoning | @modelcontextprotocol/server-sequential-thinking |

Find more at the [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)

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

OllamaAssist automatically discovers and uses available MCP tools. Example interactions:

```python
# Web search
await mcp(
    server="brave-search",
    tool="brave_web_search",
    arguments={"query": "search terms"}
)

# File operations
await mcp(
    server="filesystem",
    tool="read_file",
    arguments={"path": "/path/to/file"}
)
```

## Adding Custom MCP Tools

1. Create an MCP-compatible tool
2. Add it to `mcp_config.json`
3. The tool will be automatically available to the chatbot

## Running the Application

1. Start Ollama:
   ```bash
   ollama serve
   ```

2. Launch OllamaAssist:
   ```bash
   streamlit run ollama_chatbot.py
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

Contributions welcome! Please feel free to:
- Add new MCP tool integrations
- Improve documentation
- Submit bug fixes
- Enhance the user interface

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [MCP](https://github.com/llmOS/mcp) for the universal tool protocol
- [Ollama](https://github.com/jmorganca/ollama) for local LLM execution
- [Streamlit](https://streamlit.io/) for the web interface