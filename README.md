# any-chat-completions-mcp MCP Server

Integrate Claude with Any OpenAI SDK Compatible Chat Completion API - OpenAI, Perplexity, Groq, xAI, PyroPrompts and more.

This implements the Model Context Protocol Server. Learn more: [https://modelcontextprotocol.io](https://modelcontextprotocol.io)

This MCP server is available in two implementations:
- TypeScript: Direct integration with Claude Desktop via MCP
- Python: Standalone server implementation with SSE support

It has one tool, `chat` which relays a question to a configured AI Chat Provider.

![Claude uses OpenAI](img/screencap.mov)

<a href="https://glama.ai/mcp/servers/nuksdrfb55"><img width="380" height="200" src="https://glama.ai/mcp/servers/nuksdrfb55/badge" /></a>

## Development

### TypeScript Implementation

Install dependencies:
```bash
cd typescript
npm install
```

Build the server:
```bash
npm run build
```

For development with auto-rebuild:
```bash
npm run watch
```

### Python Implementation

Install dependencies:
```bash
cd python
pip install -r requirements.txt
```

Run the server:
```bash
python any-chat-completions-mcp-server.py --host 0.0.0.0 --port 8080
```

The server requires the following environment variables:
- `AI_CHAT_KEY`: Your API key for the chat service
- `AI_CHAT_NAME`: Name of the service (e.g., "OpenAI", "Perplexity")
- `AI_CHAT_MODEL`: Model to use (e.g., "gpt-4", "sonar")
- `AI_CHAT_BASE_URL`: Base URL of the API (e.g., "https://api.openai.com/v1", https://api.perplexity.ai)

For testing, you can use the example client:
```bash
python example_client.py http://localhost:8080/sse
```

## Claude Desktop Integration (TypeScript)

To add OpenAI to Claude Desktop, add the server config:

On MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "chat-openai": {
      "command": "node",
      "args": [
        "/path/to/any-chat-completions-mcp/typescript/build/index.js"
      ],
      "env": {
        "AI_CHAT_KEY": "OPENAI_KEY",
        "AI_CHAT_NAME": "OpenAI",
        "AI_CHAT_MODEL": "gpt-4o",
        "AI_CHAT_BASE_URL": "https://api.openai.com/v1"
      }
    }
  }
}
```

You can add multiple providers by referencing the same MCP server multiple times, but with different env arguments:

```json
{
  "mcpServers": {
    "chat-pyroprompts": {
      "command": "node",
      "args": [
        "/path/to/any-chat-completions-mcp/typescript/build/index.js"
      ],
      "env": {
        "AI_CHAT_KEY": "PYROPROMPTS_KEY",
        "AI_CHAT_NAME": "PyroPrompts",
        "AI_CHAT_MODEL": "ash",
        "AI_CHAT_BASE_URL": "https://api.pyroprompts.com/openaiv1"
      }
    },
    "chat-perplexity": {
      "command": "node",
      "args": [
        "/path/to/any-chat-completions-mcp/typescript/build/index.js"
      ],
      "env": {
        "AI_CHAT_KEY": "PERPLEXITY_KEY",
        "AI_CHAT_NAME": "Perplexity",
        "AI_CHAT_MODEL": "sonar",
        "AI_CHAT_BASE_URL": "https://api.perplexity.ai"
      }
    }
  }
}
```

With these configurations, you'll see a tool for each in the Claude Desktop Home:

![Claude Desktop Home with Chat Tools](img/claude_desktop_home.png)

And then you can chat with other LLMs and it shows in chat like this:

![Claude Chat with OpenAI](img/claude_chat_openai.png)

### Debugging

#### TypeScript Implementation
Since MCP servers communicate over stdio, debugging can be challenging. We recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector), which is available as a package script:

```bash
cd typescript
npm run inspector
```

The Inspector will provide a URL to access debugging tools in your browser.

#### Python Implementation
The Python server includes detailed logging that can be viewed in the terminal. You can also use the example client's debug mode:

```bash
python example_client.py http://localhost:8080/sse
# Then type /debug to toggle debug mode
```

The server logs all requests and responses (with sensitive information redacted) to help with debugging.

### Acknowledgements

- Obviously the modelcontextprotocol and Anthropic team for the MCP Specification and integration into Claude Desktop. [https://modelcontextprotocol.io/introduction](https://modelcontextprotocol.io/introduction)
- [PyroPrompts](https://pyroprompts.com?ref=github-any-chat-completions-mcp) for sponsoring this project. Use code `CLAUDEANYCHAT` for 20 free automation credits on Pyroprompts.
