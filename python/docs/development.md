# Development Guide

This guide provides information for developers who want to modify or extend the MCP client.

## Project Structure

The project consists of the following main components:

- `any-chat-completions-mcp-server.py`: The MCP server implementation
- `example_client.py`: The MCP client implementation
- `.env`: Environment variables for API configuration
- `requirements.txt`: Python dependencies

## Client Architecture

The client is implemented as a Python class (`MCPClient`) with the following main components:

### Connection Management

The client uses the MCP library to establish and maintain a connection to the server:

```python
async def connect_to_sse_server(self, server_url: str):
    """Connect to an MCP server running with SSE transport"""
    # Store the context managers so they stay alive
    self._streams_context = sse_client(url=server_url)
    streams = await self._streams_context.__aenter__()

    self._session_context = ClientSession(*streams)
    self.session: ClientSession = await self._session_context.__aenter__()

    # Initialize
    await self.session.initialize()
    
    # ... list tools ...
```

### Tool Discovery and Calling

The client discovers available tools on the server and calls the appropriate tool with the user's query:

```python
async def process_query(self, query: str) -> str:
    """Process a query using the MCP server's chat tool"""
    # Get available tools
    response = await self.session.list_tools()
    tools = response.tools
    
    # Find the chat tool (should be named like "chat-with-foo")
    chat_tool = None
    for tool in tools:
        if tool.name.startswith("chat-with-"):
            chat_tool = tool
            break
    
    # ... call the tool ...
```

### Response Processing

The client processes responses from the server using the `extract_content` and `format_response` methods:

```python
# Extract the content from the result
content = self.extract_content(result)

# Format the response based on the selected output format
formatted_response = self.format_response(content)
```

### Interactive Loop

The client provides an interactive command-line interface through the `chat_loop` method:

```python
async def chat_loop(self):
    """Run an interactive chat loop"""
    # ... setup ...
    
    while True:
        try:
            query = input("\nQuery: ").strip()
            
            # ... handle commands and queries ...
                
        except Exception as e:
            # ... error handling ...
```

## Adding New Features

### Adding a New Output Format

To add a new output format:

1. Add a new value to the `OutputFormat` enum:
   ```python
   class OutputFormat(Enum):
       RAW = "raw"
       PLAIN = "plain"
       PRETTY = "pretty"
       NEW_FORMAT = "new-format"  # New format
   ```

2. Add a new case to the `format_response` method:
   ```python
   def format_response(self, text: str) -> str:
       # ... existing code ...
       
       elif self.output_format == OutputFormat.NEW_FORMAT:
           # Format the text for the new format
           formatted_text = self._format_for_new_format(text)
           return formatted_text
       
       # ... existing code ...
   ```

3. Implement the formatting logic for the new format:
   ```python
   def _format_for_new_format(self, text: str) -> str:
       # Implementation of the new format
       # ...
       return formatted_text
   ```

### Adding a New Command

To add a new command to the interactive loop:

1. Add a new condition to the `chat_loop` method:
   ```python
   # Handle new command
   if query.startswith('/new-command'):
       # Parse command arguments
       args = query.split(' ')[1:]
       
       # Implement command logic
       # ...
       
       print("Command executed successfully")
       continue
   ```

### Supporting a New Response Type

To support a new response type:

1. Add a new condition to the `extract_content` method:
   ```python
   def extract_content(self, result: Any) -> str:
       # ... existing code ...
       
       # Handle new response type
       if isinstance(result, NewResponseType):
           # Extract content from the new response type
           return result.some_attribute
       
       # ... existing code ...
   ```

## Testing

To test changes to the client:

1. Start the server:
   ```bash
   python any-chat-completions-mcp-server.py
   ```

2. In a separate terminal, run the client:
   ```bash
   python example_client.py http://localhost:8080/sse
   ```

3. Test the client by sending queries and using commands.

For more systematic testing, you can create a test script that:

1. Starts the server
2. Runs the client with predefined queries
3. Verifies that the responses match expected outputs

## Debugging

The client includes a debug mode that can be used to troubleshoot issues:

```
Query: /debug
Debug mode: ON

Query: What is the capital of France?

Raw Response Object:
Type: <class 'mcp.types.CallToolResult'>
Dir: ['__abstractmethods__', '__annotations__', ...]
Repr: CallToolResult(meta=None, content=[TextContent(type='text', text="The capital of France is Paris...")], isError=False)

Extracted Text Content:
The capital of France is Paris...

Formatted Response:
The capital of France is Paris...
```

You can also add additional debug output to specific methods by adding print statements or logging calls.

## Contributing

If you want to contribute to the project:

1. Fork the repository
2. Create a new branch for your changes
3. Make your changes
4. Test your changes
5. Submit a pull request

Please follow these guidelines when contributing:

- Follow the existing code style
- Add comments to explain complex logic
- Update documentation to reflect your changes
- Add tests for new features

## Resources

- [MCP Documentation](https://github.com/anthropics/anthropic-tools/tree/main/mcp)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [Server-Sent Events (SSE) Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) 