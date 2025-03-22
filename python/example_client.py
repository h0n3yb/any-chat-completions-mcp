import asyncio
import json
import os
import sys
import re
from typing import Optional, Dict, Any, Union, List
from contextlib import AsyncExitStack
from enum import Enum

from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.types import TextContent

from dotenv import load_dotenv
# Load environment variables from .env
load_dotenv()

class OutputFormat(Enum):
    RAW = "raw"  # Raw output as received
    PLAIN = "plain"  # Strip markdown and normalize spacing
    PRETTY = "pretty"  # Attempt to render markdown in terminal

class MCPClient:
    def __init__(self, output_format: OutputFormat = OutputFormat.PRETTY):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.output_format = output_format
        self.system_prompt = "You are a helpful assistant."

    async def connect_to_sse_server(self, server_url: str):
        """Connect to an MCP server running with SSE transport"""
        # Store the context managers so they stay alive
        self._streams_context = sse_client(url=server_url)
        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)
        self.session: ClientSession = await self._session_context.__aenter__()

        # Initialize
        await self.session.initialize()

        # List available tools to verify connection
        print("Initialized SSE client...")
        print("Listing tools...")
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def cleanup(self):
        """Properly clean up the session and streams"""
        if hasattr(self, '_session_context'):
            await self._session_context.__aexit__(None, None, None)
        if hasattr(self, '_streams_context'):
            await self._streams_context.__aexit__(None, None, None)

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
        
        if not chat_tool:
            return "Error: No chat tool found on the server"
        
        try:
            # Try the new parameter format first
            if self.system_prompt:
                # Send system prompt separately
                tool_args = {
                    "user_content": query,
                    "system_content": self.system_prompt
                }
            else:
                # No system prompt
                tool_args = {
                    "user_content": query
                }
            
            # Call the chat tool with the properly formatted arguments
            result = await self.session.call_tool(chat_tool.name, tool_args)
        except Exception as e:
            # If the new format fails, try the legacy format
            if "validation error" in str(e):
                print("Server may be using an older version. Trying legacy format...")
                if self.system_prompt:
                    # Format with system prompt in the content
                    tool_args = {
                        "content": f"System: {self.system_prompt}\n\nUser: {query}"
                    }
                else:
                    # Format without system prompt
                    tool_args = {"content": query}
                
                # Call the chat tool with the legacy format
                result = await self.session.call_tool(chat_tool.name, tool_args)
            else:
                # If it's not a validation error, re-raise
                raise
        
        # Extract the content from the result
        content = self.extract_content(result)
        
        # Format the response based on the selected output format
        formatted_response = self.format_response(content)
        
        # Return the formatted result content
        return formatted_response

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
        
        # If result has content attribute that is a string
        if hasattr(result, 'content') and isinstance(result.content, str):
            return result.content
        
        # If result is a dictionary with a content field
        if isinstance(result, dict) and 'content' in result:
            return result['content']
        
        # If result is already a string
        if isinstance(result, str):
            return result
        
        # If result is an object with a text attribute
        if hasattr(result, 'text'):
            return result.text
        
        # If we can't determine the content, convert to string
        return str(result)

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
        
        # Format code blocks
        def format_code_block(match):
            code = match.group(1).strip()
            formatted_code = '\n' + code + '\n'
            return formatted_code
        
        text = re.sub(r'```(?:.*?)\n([\s\S]*?)```', format_code_block, text)
        
        # Format inline code
        text = re.sub(r'`([^`]+)`', r'"\1"', text)
        
        # Format lists
        text = re.sub(r'^- (.*?)$', r'  • \1', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+\. (.*?)$', r'  \g<0>', text, flags=re.MULTILINE)
        
        return text

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print(f"Output format: {self.output_format.value}")
        print("Type your queries or 'quit' to exit.")
        print("Commands:")
        print("  /format raw    - Switch to raw output format")
        print("  /format plain  - Switch to plain text format (strip markdown)")
        print("  /format pretty - Switch to pretty format (render markdown)")
        print("  /debug         - Toggle debug mode to show raw response objects")
        
        debug_mode = False
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                
                if query.lower() == 'quit':
                    break
                
                # Handle format switching commands
                if query.startswith('/format '):
                    format_name = query.split(' ')[1].lower()
                    try:
                        self.output_format = OutputFormat(format_name)
                        print(f"Output format switched to: {self.output_format.value}")
                    except ValueError:
                        print(f"Unknown format: {format_name}. Available formats: raw, plain, pretty")
                    continue
                
                # Toggle debug mode
                if query.lower() == '/debug':
                    debug_mode = not debug_mode
                    print(f"Debug mode: {'ON' if debug_mode else 'OFF'}")
                    continue
                
                # Process the query
                if debug_mode:
                    # In debug mode, get the raw result
                    response = await self.session.list_tools()
                    tools = response.tools
                    
                    chat_tool = None
                    for tool in tools:
                        if tool.name.startswith("chat-with-"):
                            chat_tool = tool
                            break
                    
                    if not chat_tool:
                        print("Error: No chat tool found on the server")
                        continue
                    
                    try:
                        # Try the new parameter format first
                        if self.system_prompt:
                            tool_args = {
                                "user_content": query,
                                "system_content": self.system_prompt
                            }
                        else:
                            tool_args = {
                                "user_content": query
                            }
                        
                        result = await self.session.call_tool(chat_tool.name, tool_args)
                    except Exception as e:
                        # If the new format fails, try the legacy format
                        if "validation error" in str(e):
                            print("Server may be using an older version. Trying legacy format...")
                            if self.system_prompt:
                                # Format with system prompt in the content
                                tool_args = {
                                    "content": f"System: {self.system_prompt}\n\nUser: {query}"
                                }
                            else:
                                # Format without system prompt
                                tool_args = {"content": query}
                            
                            # Call the chat tool with the legacy format
                            result = await self.session.call_tool(chat_tool.name, tool_args)
                        else:
                            # If it's not a validation error, re-raise
                            raise
                    
                    print("\nRaw Response Object:")
                    print(f"Type: {type(result)}")
                    print(f"Dir: {dir(result)}")
                    print(f"Repr: {repr(result)}")
                    
                    # Extract and format the content
                    content = self.extract_content(result)
                    formatted_response = self.format_response(content)
                    
                    print("\nExtracted Text Content:")
                    print(content)
                    
                    print("\nFormatted Response:")
                    print(formatted_response)
                else:
                    # Normal mode
                    response = await self.process_query(query)
                    print("\nResponse:")
                    print(response)
                    
            except Exception as e:
                print(f"\nError: {str(e)}")
                import traceback
                traceback.print_exc()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python example_client.py <URL of SSE MCP server (i.e. http://localhost:8080/sse)> [format]")
        print("Available formats: raw, plain, pretty (default: pretty)")
        sys.exit(1)

    # Parse format argument if provided
    output_format = OutputFormat.PRETTY
    if len(sys.argv) >= 3:
        try:
            output_format = OutputFormat(sys.argv[2].lower())
        except ValueError:
            print(f"Unknown format: {sys.argv[2]}. Using default: pretty")
    
    client = MCPClient(output_format=output_format)
    try:
        await client.connect_to_sse_server(server_url=sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main()) 