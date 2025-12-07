# Math MCP Example: Server & Client

#############################################
## Directory Structure & Environment Setup
#############################################

Recommended project structure:

```
iceberg-mcp-main/
├── iceberg_mcp/
│   └── math/
│       ├── math_server.py
│       ├── math_clinet.py
│       └── README.md
├── .venv/                # Python virtual environment (recommended)
└── ...                   # Other project files
```

### Setting up your Python environment

1. **Create a virtual environment (recommended):**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install required dependencies:**
   (Make sure you are in the root directory or where your requirements are listed)
   ```sh
   pip install mcp fastmcp fastapi-mcp langchain-mcp-adapters uvicorn
   # And any other dependencies your project needs
   ```

3. **Set your OpenAI API key:**
   ```sh
   export OPENAI_API_KEY=sk-...your-key-here...
   ```

---

## Overview

- **Server:** Exposes math tools (add, sub, multiply) and prompt templates using FastMCP and SSE (Server-Sent Events).
- **Client:** Connects to the server, discovers available tools, and uses an LLM agent to invoke those tools.

---

## Learning Objectives
- Understand how to register and expose tools in a Python server.
- Learn how to connect to a tool server and discover available tools.
- See how an LLM agent can use external tools to answer questions.
- Practice async programming and client-server communication.

---
#############################################
## Server: `math_server.py`
#############################################



### What does it do?
- Registers three math tools: `add`, `sub`, `multiply`.
- Registers three prompt templates for natural language generation.
- Exposes an ASGI app for Uvicorn to serve via SSE.
- Logs every tool and prompt call for transparency.

### Key code sections
```python
from mcp.server.fastmcp import FastMCP
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("math_server")

# Create the server
mcp = FastMCP("Math")
app = mcp.sse_app  # Expose the SSE ASGI app

# Register tools
@mcp.tool()
def add(a: int, b: int) -> int:
    result = a + b
    logger.info(f"add({a}, {b}) = {result}")
    return result

# ... (sub, multiply, and prompts similar)

print("Registered tools:", mcp.list_tools())
```

###   >>>>>>>>>>>>>>>>>>>>>>>> How to run the server===================================================================================
From the `iceberg_mcp/math` directory:
```sh
uvicorn math_server:app --port 3000
```
Or from the project root:
```sh
uvicorn iceberg_mcp.math.math_server:app --port 3000
```

#############################################

## Client: `math_clinet.py`
#############################################


### What does it do?
- Connects to the math server using SSE.
- Discovers available tools.
- Uses a LangChain agent to ask the server to add 3 and 5.
- Prints only the final answer from the agent's response.

### Key code sections
```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import asyncio

client = MultiServerMCPClient({
    "math": {
        "transport": "sse",
        "url": "http://localhost:3000/sse"
    },
})

async def main():
    tools = await client.get_tools()
    print("Discovered tools:", tools)
    agent = create_react_agent("openai:gpt-4.1", tools)
    math_response = await agent.ainvoke({"messages": "use the add tool to add 3 and 5"})
    if 'messages' in math_response and len(math_response['messages']) > 1:
        ai_message = math_response['messages'][-1]
        print(ai_message.content)
    else:
        print(math_response)

if __name__ == "__main__":
    asyncio.run(main())
```

### OpenAI API Key Setup #############################################



To use the LLM agent (e.g., GPT-4), you need an OpenAI API key. This is required for the client to access OpenAI's language models.

**How to set your OpenAI API key:**

- The recommended way is to set the `OPENAI_API_KEY` environment variable in your shell:

```sh
export OPENAI_API_KEY=sk-...your-key-here...
```

- Alternatively, you can set it in your Python code (not recommended for production):

```python
import os
os.environ["OPENAI_API_KEY"] = "sk-...your-key-here..."
```

**You must set the API key before running the client, or you will get authentication errors.**

###  >>>>>>>>>>>>>>>>>>> How to run the client################################################################
From the `iceberg_mcp/math` directory:
```sh
python math_clinet.py
```

---

## Experiment & Learn
- Try changing the numbers in the client prompt.
- Add new tools (e.g., division) to the server and see if the client discovers them.
- Add more prompts or logging to see how the server responds.
- Explore how async programming enables real-time tool discovery and invocation.

---

## Troubleshooting
- If the client prints `[]` for tools, check server logs and package versions.
- Make sure both server and client use compatible MCP and adapter versions.
- Ensure the server is running before starting the client.

---

## Summary
This example demonstrates how to:
- Build a tool-augmented AI server in Python
- Connect and interact with it using a modern LLM agent
- Use async programming for efficient, real-time communication

Happy learning! 