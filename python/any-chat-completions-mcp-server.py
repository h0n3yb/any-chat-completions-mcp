#!/usr/bin/env python3
import os
import httpx
import uvicorn
import argparse
import json
import logging
from typing import Any
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("any-chat-completions-mcp")

# Load environment variables
load_dotenv()

# Get environment variables
AI_CHAT_BASE_URL = os.getenv("AI_CHAT_BASE_URL")
AI_CHAT_KEY = os.getenv("AI_CHAT_KEY")
AI_CHAT_MODEL = os.getenv("AI_CHAT_MODEL")
AI_CHAT_NAME = os.getenv("AI_CHAT_NAME")

# Check required environment variables
if not AI_CHAT_BASE_URL:
    raise ValueError("AI_CHAT_BASE_URL is required")
if not AI_CHAT_KEY:
    raise ValueError("AI_CHAT_KEY is required")
if not AI_CHAT_MODEL:
    raise ValueError("AI_CHAT_MODEL is required")
if not AI_CHAT_NAME:
    raise ValueError("AI_CHAT_NAME is required")

# Clean AI_CHAT_NAME for use in tool name
AI_CHAT_NAME_CLEAN = AI_CHAT_NAME.lower().replace(' ', '-')

# Initialize FastMCP server
mcp = FastMCP("any-chat-completions-mcp", version="0.1.0")

@mcp.tool(name=f"chat-with-{AI_CHAT_NAME_CLEAN}")
async def chat_with_ai(content: str = None, user_content: str = None, system_content: str = None) -> str:
    """Text chat with an AI assistant.
    
    Args:
        content: The content of the chat (legacy parameter)
        user_content: The user message to send to the AI assistant
        system_content: Optional system instructions to guide the AI's behavior
    """
    # Handle both old and new parameter formats for backward compatibility
    actual_user_content = user_content if user_content is not None else content
    
    if not actual_user_content:
        raise ValueError("User content is required")
        
    # Make request to OpenAI-compatible API
    headers = {
        "Authorization": f"Bearer {AI_CHAT_KEY}",
        "Content-Type": "application/json"
    }
    
    # Prepare messages array
    messages = []
    
    # Add system message if provided
    if system_content:
        messages.append({"role": "system", "content": system_content})
    
    # Add user message
    messages.append({"role": "user", "content": actual_user_content})
    
    data = {
        "messages": messages,
        "model": AI_CHAT_MODEL
    }
    
    # Log the request being sent (excluding sensitive information)
    safe_data = data.copy()
    if 'messages' in safe_data:
        # Keep message structure but truncate long content for readability
        for i, msg in enumerate(safe_data['messages']):
            if len(msg.get('content', '')) > 100:
                safe_data['messages'][i]['content'] = msg['content'][:100] + '...'
    
    logger.debug(f"Sending request to {AI_CHAT_BASE_URL}/chat/completions")
    logger.debug(f"Request data: {json.dumps(safe_data, indent=2)}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{AI_CHAT_BASE_URL}/chat/completions",
                headers=headers,
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            # Log response status and basic info (not the full content)
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response model: {result.get('model', 'unknown')}")
            logger.debug(f"Response usage: {result.get('usage', {})}")
            
            message_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return message_content
        except Exception as e:
            logger.error(f"Error communicating with AI service: {str(e)}")
            return f"Error communicating with AI service: {str(e)}"

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

if __name__ == "__main__":
    mcp_server = mcp._mcp_server  # noqa: WPS437
    
    parser = argparse.ArgumentParser(description='Run MCP SSE-based AI chat server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    args = parser.parse_args()

    # Create and run the Starlette app with SSE support
    starlette_app = create_starlette_app(mcp_server, debug=True)
    uvicorn.run(starlette_app, host=args.host, port=args.port)