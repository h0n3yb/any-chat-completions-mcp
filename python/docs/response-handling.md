# Response Handling Guide

This guide explains how the MCP client processes and formats responses from the server.

## Response Structure

When the client calls a tool on the MCP server, the server returns a response with a specific structure. In the case of the chat tool, the response is a `CallToolResult` object with the following structure:

```
CallToolResult(
    meta=None, 
    content=[
        TextContent(
            type='text', 
            text="The actual response text...", 
            annotations=None
        )
    ], 
    isError=False
)
```

The key components are:
- `meta`: Metadata about the response (usually `None`)
- `content`: A list of content objects, typically containing a single `TextContent` object
- `isError`: A boolean indicating whether an error occurred

The `TextContent` object contains:
- `type`: The type of content (usually `'text'`)
- `text`: The actual text content of the response
- `annotations`: Any annotations on the text (usually `None`)

## Response Processing Flow

The client processes responses from the server in the following steps:

1. **Call the Tool**: The client calls the appropriate tool on the server with the user's query
2. **Extract Content**: The client extracts the text content from the response
3. **Format Content**: The client formats the extracted content according to the selected output format
4. **Display Result**: The formatted content is displayed to the user

## Content Extraction

The client uses the `extract_content` method to extract the text content from the response:

```python
def extract_content(self, result: Any) -> str:
    """Extract content from the result, handling different response types."""
    # Handle CallToolResult with content attribute that is a list of TextContent objects
    if hasattr(result, 'content') and isinstance(result.content, list):
        # Combine all text content from the list
        combined_text = ""
        for item in result.content:
            if hasattr(item, 'text') and item.text:
                combined_text += item.text
        if combined_text:
            return combined_text
    
    # ... other extraction methods ...
```

This method handles various response structures, with the primary case being a `CallToolResult` with a list of `TextContent` objects. It extracts the text from each `TextContent` object and combines them into a single string.

## Content Formatting

After extracting the text content, the client formats it according to the selected output format using the `format_response` method:

```python
def format_response(self, text: str) -> str:
    """Format the response text based on the selected output format."""
    if self.output_format == OutputFormat.RAW:
        return text
    
    elif self.output_format == OutputFormat.PLAIN:
        # Strip markdown and normalize spacing
        plain_text = self._strip_markdown(text)
        return plain_text
    
    elif self.output_format == OutputFormat.PRETTY:
        # Attempt to render markdown in terminal
        pretty_text = self._render_markdown_for_terminal(text)
        return pretty_text
    
    return text  # Default fallback
```

### Raw Format

The raw format returns the text content exactly as received from the server, with no modifications.

### Plain Format

The plain format strips all markdown formatting and normalizes spacing using the `_strip_markdown` method:

```python
def _strip_markdown(self, text: str) -> str:
    """Strip markdown formatting and normalize spacing."""
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    
    # Remove inline code
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Remove headers
    text = re.sub(r'#{1,6}\s+(.*)', r'\1', text)
    
    # Remove bold/italic
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    
    # Remove links
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    
    # Normalize whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'\s{2,}', ' ', text)
    
    return text.strip()
```

This method uses regular expressions to remove various markdown elements and normalize whitespace.

### Pretty Format

The pretty format attempts to render markdown in the terminal using ANSI escape codes for formatting:

```python
def _render_markdown_for_terminal(self, text: str) -> str:
    """Render markdown for terminal display with basic formatting."""
    # ANSI escape codes for formatting
    BOLD = '\033[1m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    
    # Format headers
    text = re.sub(r'^# (.*?)$', f"\n{BOLD}\\1{RESET}\n", text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', f"\n{BOLD}\\1{RESET}\n", text, flags=re.MULTILINE)
    text = re.sub(r'^### (.*?)$', f"\n{UNDERLINE}\\1{RESET}\n", text, flags=re.MULTILINE)
    
    # Format bold and italic
    text = re.sub(r'\*\*(.*?)\*\*', f"{BOLD}\\1{RESET}", text)
    text = re.sub(r'\*(.*?)\*', f"{ITALIC}\\1{RESET}", text)
    
    # ... other formatting ...
    
    return text
```

This method uses regular expressions to convert markdown syntax to ANSI escape codes for terminal formatting.

## Debug Mode

The client includes a debug mode that provides detailed information about the response objects:

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

This mode is useful for understanding the structure of the response objects and troubleshooting issues with response handling.

## Error Handling

The client includes error handling to gracefully handle issues with response processing:

```python
try:
    response = await self.process_query(query)
    print("\nResponse:")
    print(response)
except Exception as e:
    print(f"\nError: {str(e)}")
    import traceback
    traceback.print_exc()
```

If an error occurs during response processing, the client will display an error message and a stack trace to help diagnose the issue.

## Customizing Response Handling

If you need to customize how responses are handled, you can modify the following methods in the `MCPClient` class:

- `extract_content`: To change how content is extracted from response objects
- `format_response`: To change how content is formatted
- `_strip_markdown`: To change how markdown is stripped for plain text format
- `_render_markdown_for_terminal`: To change how markdown is rendered for pretty format 