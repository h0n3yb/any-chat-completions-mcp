# Configuration Guide

This guide explains how to configure the MCP client and server to work with different AI services and customize behavior.

## Environment Variables

The MCP server uses environment variables to configure the connection to the AI service. These variables are loaded from a `.env` file in the project root directory.

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AI_CHAT_BASE_URL` | The base URL of the AI service API | `https://api.perplexity.ai` |
| `AI_CHAT_KEY` | Your API key for the AI service | `pplx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `AI_CHAT_MODEL` | The model to use for generating responses | `sonar` |
| `AI_CHAT_NAME` | A name for the AI service (used in tool names) | `perplexity` |

### Example `.env` File

```
AI_CHAT_BASE_URL=https://api.perplexity.ai
AI_CHAT_KEY=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
AI_CHAT_MODEL=sonar
AI_CHAT_NAME=perplexity
```

## Server Configuration

### Command-Line Arguments

The server supports the following command-line arguments:

| Argument | Description | Default |
|----------|-------------|---------|
| `--host` | The host to bind to | `0.0.0.0` |
| `--port` | The port to listen on | `8080` |

Example:
```bash
python any-chat-completions-mcp-server.py --host 127.0.0.1 --port 9000
```

### Tool Configuration

The server creates a tool with a name based on the `AI_CHAT_NAME` environment variable. For example, if `AI_CHAT_NAME` is set to `perplexity`, the tool will be named `chat-with-perplexity`.

### System Prompt Handling

The server properly handles system prompts by separating them from user messages. When a system prompt is provided by the client, the server sends it as a separate message with the "system" role to the AI service. This ensures that the AI service correctly interprets the system instructions.

The messages sent to the AI service follow this structure:
```json
{
  "messages": [
    {"role": "system", "content": "System prompt text here"},
    {"role": "user", "content": "User query text here"}
  ],
  "model": "model-name"
}
```

#### Backward Compatibility

The server and client are designed to be backward compatible:

- The server accepts both the new parameter format (`user_content` and `system_content`) and the legacy format (`content`).
- The client first tries to use the new parameter format. If that fails with a validation error, it falls back to the legacy format where the system prompt is included in the content string.

This ensures that the client can work with both updated and older server versions.

## Client Configuration

### Command-Line Arguments

The client supports the following command-line arguments:

| Argument | Description | Required |
|----------|-------------|----------|
| `<server-url>` | The URL of the MCP server | Yes |
| `[format]` | The initial output format (`raw`, `plain`, or `pretty`) | No (default: `pretty`) |
| `[prompt]` | The initial system prompt type (`none`, `jobs`, `products`, or `socials`) | No (default: `none`) |

Example:
```bash
python example_client.py http://localhost:8080/sse plain jobs
```

### Output Format Configuration

The client supports three output formats:

| Format | Description |
|--------|-------------|
| `raw` | Shows the unprocessed response text, including all markdown syntax |
| `plain` | Strips all markdown formatting and normalizes spacing |
| `pretty` | Renders markdown in the terminal using ANSI escape codes |

You can change the output format during the session using the `/format` command:
```
Query: /format raw
```

### System Prompt Configuration

The client supports several system prompts that guide the AI's behavior:

| Prompt Type | Description |
|-------------|-------------|
| `none` | No system prompt (default) |
| `jobs` | Instructs the AI to extract job information in a structured JSON format |
| `products` | Guides the AI to extract product information |
| `socials` | Helps the AI extract information from social media profiles or posts |

You can change the system prompt during the session using the `/prompt` command:
```
Query: /prompt jobs
```

#### System Prompts File

System prompts are defined in the `system_prompts.py` file. This file contains variables for each system prompt type:

```python
jobs_system_prompt = """
You are a specialized job data extraction assistant...
"""

products_system_prompt = """
You are a specialized product data extraction assistant...
"""

socials_system_prompt = """
You are a specialized social media data extraction assistant...
"""
```

To add or modify system prompts, edit this file and add or update the corresponding variables.

#### System Prompt Propagation

When a system prompt is selected in the client, it is properly propagated to the server as a separate parameter. The server then uses this system prompt as a "system" role message when communicating with the AI service. This ensures that the AI service correctly interprets the system instructions and user queries separately.

## Using with Different AI Services

The MCP server is designed to work with any AI service that implements the OpenAI-compatible chat completions API. Here are examples for different services:

### Perplexity AI

```
AI_CHAT_BASE_URL=https://api.perplexity.ai
AI_CHAT_KEY=pplx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AI_CHAT_MODEL=sonar
AI_CHAT_NAME=perplexity
```

### OpenAI

```
AI_CHAT_BASE_URL=https://api.openai.com/v1
AI_CHAT_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AI_CHAT_MODEL=gpt-4
AI_CHAT_NAME=openai
```

### Anthropic

```
AI_CHAT_BASE_URL=https://api.anthropic.com/v1
AI_CHAT_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AI_CHAT_MODEL=claude-3-opus-20240229
AI_CHAT_NAME=anthropic
```

## Advanced Configuration

### Customizing Markdown Rendering

If you want to customize how markdown is rendered in the terminal, you can modify the `_render_markdown_for_terminal` method in the `MCPClient` class. This method uses regular expressions to convert markdown syntax to ANSI escape codes for terminal formatting.

### Adding New Output Formats

To add a new output format:

1. Add a new value to the `OutputFormat` enum in `example_client.py`
2. Add a new case to the `format_response` method to handle the new format
3. Implement the formatting logic for the new format

Example:
```python
class OutputFormat(Enum):
    RAW = "raw"
    PLAIN = "plain"
    PRETTY = "pretty"
    HTML = "html"  # New format

def format_response(self, text: str) -> str:
    # ... existing code ...
    
    elif self.output_format == OutputFormat.HTML:
        # Convert markdown to HTML
        html_text = self._convert_to_html(text)
        return html_text
    
    # ... existing code ...

def _convert_to_html(self, text: str) -> str:
    # Implementation of markdown to HTML conversion
    # ...
```

### Adding New System Prompts

To add a new system prompt:

1. Add a new variable to `system_prompts.py` with the prompt text
2. Add a new value to the `SystemPromptType` enum in `example_client.py`
3. Update the `_get_system_prompt` method to handle the new prompt type

Example:

In `system_prompts.py`:
```python
research_system_prompt = """
You are a specialized research assistant...
"""
```

In `example_client.py`:
```python
class SystemPromptType(Enum):
    NONE = "none"
    JOBS = "jobs"
    PRODUCTS = "products"
    SOCIALS = "socials"
    RESEARCH = "research"  # New prompt type

def _get_system_prompt(self) -> Optional[str]:
    # ... existing code ...
    
    elif self.system_prompt_type == SystemPromptType.RESEARCH:
        return research_system_prompt
    
    # ... existing code ...
``` 