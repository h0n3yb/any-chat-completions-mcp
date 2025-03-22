# MCP Client Example

This is an example implementation of a client for the MCP (Model Control Protocol) using SSE (Server-Sent Events) transport.

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Anthropic API key:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

### Running the Example Client

```bash
python example_client.py
```

This will run a simple example that demonstrates how to:
- Connect to an MCP server
- Send queries
- Process responses
- Handle tool calls

### Using the Client in Your Code

The main client implementation is in `mcp_client.py`. You can import and use the `MCPClient` class in your own code:

```python
from mcp_client import MCPClient

async def your_function():
    client = MCPClient()
    try:
        await client.connect_to_sse_server("your_server_url")
        response = await client.process_query("your query")
        print(response)
    finally:
        await client.cleanup()
```

## Features

- Asynchronous communication with MCP server
- Automatic tool handling
- Clean resource management
- Integration with Claude API
- Support for SSE transport

## Requirements

- Python 3.7+
- Anthropic API key
- Running MCP server with SSE transport 