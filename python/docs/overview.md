# MCP Client Overview

## What is MCP?

MCP (Model Control Protocol) is a protocol designed to standardize the way AI models interact with tools and services. It provides a consistent interface for models to access external capabilities, regardless of the specific model or provider being used.

## Purpose of the MCP Client

The MCP client in this project serves as a bridge between users and AI services through the MCP protocol. It allows users to:

1. Connect to an MCP server running with SSE (Server-Sent Events) transport
2. Send queries to the AI service through the server
3. Receive and format responses in a user-friendly way

## Key Features

- **Universal AI Service Access**: Works with any AI service that implements the OpenAI-compatible chat completions API
- **Configurable Output Formatting**: Supports multiple output formats (raw, plain text, and pretty-printed markdown)
- **Interactive Chat Interface**: Provides a command-line interface for interactive conversations
- **Debug Mode**: Includes a debug mode to inspect the raw response objects
- **Robust Error Handling**: Gracefully handles connection issues and response parsing errors

## Architecture

The MCP client follows a client-server architecture:

1. **MCP Server**: Hosts tools that can be called by the client. In our case, the server provides a chat tool that connects to an AI service (like Perplexity AI).
2. **MCP Client**: Connects to the server, lists available tools, and calls the appropriate tool with user queries.
3. **AI Service**: The backend AI service (e.g., Perplexity AI) that processes the queries and generates responses.

```
User → MCP Client → MCP Server → AI Service (Perplexity, etc.)
```

## Response Flow

1. User enters a query in the client
2. Client sends the query to the server using the appropriate tool
3. Server forwards the query to the AI service
4. AI service generates a response
5. Server returns the response to the client
6. Client formats the response according to the selected output format
7. Formatted response is displayed to the user

## Implementation Details

The client is implemented in Python using asynchronous programming (asyncio) for efficient communication with the server. It uses the MCP library to handle the protocol-specific aspects of the communication.

The main components of the client are:

- **MCPClient class**: The core client implementation
- **OutputFormat enum**: Defines the available output formats
- **Connection management**: Handles establishing and maintaining the connection to the server
- **Response processing**: Extracts and formats the content from the server responses
- **Interactive loop**: Provides the command-line interface for user interaction 