# Usage Guide

This guide explains how to use the MCP client to interact with AI services through the MCP server.

## Starting the Client

To start the client, run:

```bash
python example_client.py <server-url> [format] [prompt]
```

Where:
- `<server-url>` is the URL of the MCP server (e.g., `http://localhost:8080/sse`)
- `[format]` (optional) is the initial output format (`raw`, `plain`, or `pretty`, default is `pretty`)
- `[prompt]` (optional) is the initial system prompt type (`none`, `jobs`, `products`, or `socials`, default is `none`)

Example:
```bash
python example_client.py http://localhost:8080/sse pretty jobs
```

## Interactive Commands

Once the client is running, you can use the following commands:

### Sending Queries

Simply type your query and press Enter to send it to the AI service:

```
Query: What is the capital of France?
```

### Changing Output Format

You can change the output format during the session using the `/format` command:

```
Query: /format raw     # Switch to raw format (shows the unprocessed response)
Query: /format plain   # Switch to plain text format (strips markdown)
Query: /format pretty  # Switch to pretty format (renders markdown in terminal)
```

### Changing System Prompt

You can change the system prompt during the session using the `/prompt` command:

```
Query: /prompt none     # Disable system prompt
Query: /prompt jobs     # Use jobs system prompt
Query: /prompt products # Use products system prompt
Query: /prompt socials  # Use socials system prompt
```

System prompts are special instructions that guide the AI's behavior. For example, the jobs system prompt instructs the AI to extract job information in a specific format.

When you select a system prompt, it is sent to the server as a separate "system" message, ensuring that the AI service correctly interprets it as system instructions rather than user input.

### Debug Mode

To toggle debug mode, which shows detailed information about the response objects:

```
Query: /debug
```

When debug mode is ON, you'll see:
- The raw response object type
- The object's attributes
- The string representation of the object
- The extracted text content
- The formatted response

To turn off debug mode, run the `/debug` command again.

### Exiting the Client

To exit the client, type:

```
Query: quit
```

## Output Formats

The client supports three output formats:

### Raw Format

Shows the unprocessed response text, including all markdown syntax and formatting.

### Plain Format

Strips all markdown formatting and normalizes spacing for a clean, plain text output. This is useful when you want to copy the text without any formatting.

### Pretty Format

Attempts to render markdown in the terminal using ANSI escape codes for formatting. This includes:
- Bold and italic text
- Headers
- Code blocks
- Lists

## System Prompts

The client supports several system prompts that guide the AI's behavior:

### None (Default)

No system prompt is used. The AI will respond to queries based on its general training.

### Jobs

The jobs system prompt instructs the AI to extract job information from websites in a structured JSON format. This is useful for analyzing job postings.

### Products

The products system prompt guides the AI to extract product information in a specific format.

### Socials

The socials system prompt helps the AI extract information from social media profiles or posts.

### How System Prompts Work

When you select a system prompt, the client sends it to the server as a separate parameter. The server then includes this as a "system" role message when communicating with the AI service. This ensures that the AI service correctly interprets the system instructions and user queries separately.

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

This proper separation of system and user messages allows the AI to better understand the context and purpose of your queries.

#### Backward Compatibility

The client is designed to work with both updated and older server versions:

1. It first attempts to send the system prompt as a separate parameter.
2. If the server doesn't support this format, the client automatically falls back to including the system prompt in the content string.

You might see a message like "Server may be using an older version. Trying legacy format..." if the client needs to use the fallback mechanism. This is normal and doesn't affect functionality.

## Examples

### Basic Query

```
Query: What is the capital of France?

Response:
The capital of France is Paris. It is the largest city in France and serves as the country's major cultural, economic, and political center.
```

### Using System Prompt

```
Query: /prompt jobs
System prompt switched to: jobs

Query: https://example.com/careers

Response:
{
  "company_name": "Example Company",
  "jobs": [
    {
      "title": "Software Engineer",
      "description": "Develop and maintain web applications",
      ...
    }
  ],
  "total_jobs_found": 1,
  "data_collection_date": "2023-05-15"
}
```

### Using Debug Mode

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

### Changing Output Format

```
Query: /format plain
Output format switched to: plain

Query: What is **Machine Learning**?

Response:
Machine Learning is a subset of artificial intelligence that focuses on developing systems that can learn from and make decisions based on data.
```

## Best Practices

1. **Start with Pretty Format**: The pretty format provides the best readability for most responses.
2. **Use Plain Format for Copying**: Switch to plain format when you need to copy text without formatting.
3. **Use Debug Mode for Troubleshooting**: If responses aren't displaying correctly, use debug mode to see the raw response structure.
4. **Be Specific in Queries**: More specific queries tend to yield better results from the AI service.
5. **Choose the Right System Prompt**: Select a system prompt that matches your task (e.g., use the jobs prompt when analyzing job postings).
6. **Check Server Connection**: If you're not getting responses, ensure the server is running and the URL is correct.
7. **Understand System Prompt Effects**: Different system prompts can dramatically change how the AI responds to the same query.

## Next Steps

For information on configuring the client and server, see the [Configuration Guide](configuration.md).

For details on how the client handles and formats responses, see the [Response Handling Guide](response-handling.md). 