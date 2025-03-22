# Installation Guide

This guide will walk you through the process of setting up the MCP client and server.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- An API key for an AI service (e.g., Perplexity AI)

## Step 1: Clone the Repository

If you haven't already, clone the repository to your local machine:

```bash
git clone <repository-url>
cd any-chat-completions-mcp/python
```

## Step 2: Create a Virtual Environment (Recommended)

It's recommended to use a virtual environment to avoid conflicts with other Python packages:

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

If you encounter any issues with the `mcp` package, you may need to install it directly from the source:

```bash
pip install git+https://github.com/anthropics/anthropic-mcp.git
```

## Step 4: Configure Environment Variables

Create a `.env` file in the project root directory with your AI service credentials:

```
AI_CHAT_BASE_URL=https://api.perplexity.ai
AI_CHAT_KEY=your-api-key-here
AI_CHAT_MODEL=sonar
AI_CHAT_NAME=perplexity
```

Replace `your-api-key-here` with your actual API key.

## Step 5: Verify Installation

To verify that everything is set up correctly, you can run the server:

```bash
python any-chat-completions-mcp-server.py
```

You should see output indicating that the server is running, typically on port 8080.

## Step 6: Run the Client

In a separate terminal window, run the client:

```bash
python example_client.py http://localhost:8080/sse
```

If everything is set up correctly, you should see output indicating that the client has connected to the server and is ready to process queries.

## Troubleshooting

### Package Installation Issues

If you encounter issues installing the `mcp` package, try:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Connection Issues

If the client cannot connect to the server, ensure that:

1. The server is running
2. The URL is correct (typically `http://localhost:8080/sse`)
3. There are no firewalls blocking the connection

### API Key Issues

If you receive authentication errors, check that:

1. Your API key is correct
2. The API key is properly set in the `.env` file
3. The `.env` file is in the correct location (project root directory)

## Next Steps

Once you have successfully installed and run the client, proceed to the [Usage Guide](usage.md) to learn how to use the client effectively. 