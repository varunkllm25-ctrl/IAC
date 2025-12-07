"""
math_clinet.py
=============
This file demonstrates how to connect to a Math MCP server, discover available math tools, and use an LLM agent to invoke those tools. It is designed for educational purposes and shows how to:
- Connect to an MCP server using stdio transport
- Discover and list available tools
- Use a LangChain agent to interact with the tools
- Print only the final answer from the agent's response

Key Concepts:
- MultiServerMCPClient: Connects to one or more MCP servers and discovers tools.
- create_react_agent: Creates an LLM agent that can use discovered tools.
- Async programming: Uses asyncio for asynchronous tool discovery and invocation.

How it works:
- The client connects to the math server using stdio transport
- It discovers the available tools (add, sub, multiply)
- It asks the agent to perform operations using the discovered tools
"""

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import asyncio
import logging
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("math_client")

# Configure server parameters for stdio transport
SERVER_PARAMS = {
    "math": {
        "command": "python",
        "args": ["-m", "iceberg_mcp.math.math_server"],
        "transport": "stdio",
        "tools": "all"
    }
}

# Initialize the client with stdio transport
client = MultiServerMCPClient(SERVER_PARAMS)

async def main():
    try:
        # Discover available tools from the math server
        tools = await client.get_tools()
        print("Discovered tools:", tools)

        # Create an LLM agent that can use the discovered tools
        model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        agent = create_react_agent(model, tools)

        # Get user input for the operation
        query = input("Enter your math operation (e.g., 'add 3 and 5'): ")
        
        # Process the query using the agent
        math_response = await agent.ainvoke({"messages": [HumanMessage(content=query)]})

        # Extract and print the response
        if 'messages' in math_response and len(math_response['messages']) > 1:
            ai_message = math_response['messages'][-1]
            print("\nResult:", ai_message.content)
        else:
            print("\nResponse:", math_response)

    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())