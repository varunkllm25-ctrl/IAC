#!/usr/bin/env python3
"""
Simple MCP client to test the math server functionality
"""
import asyncio
import sys
import os
import subprocess
import json
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

async def test_mcp_stdio():
    """Test MCP server over stdio transport"""
    print("🧪 Testing Math MCP Server over STDIO...")
    
    # Start the math server as a subprocess
    cmd = [sys.executable, os.path.join(os.path.dirname(__file__), 'math_server.py')]
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"📥 Initialize response: {response}")
            
            if response.get('result'):
                print("✅ Server initialized successfully!")
                
                # Test list_tools
                tools_request = {
                    "jsonrpc": "2.0", 
                    "id": 2,
                    "method": "tools/list"
                }
                
                print("📤 Requesting tools list...")
                process.stdin.write(json.dumps(tools_request) + '\n')
                process.stdin.flush()
                
                tools_response_line = process.stdout.readline()
                if tools_response_line:
                    tools_response = json.loads(tools_response_line.strip())
                    print(f"📥 Tools response: {tools_response}")
                    
                    if 'result' in tools_response and 'tools' in tools_response['result']:
                        tools = tools_response['result']['tools']
                        print(f"🛠️  Available tools: {[tool['name'] for tool in tools]}")
                        
                        # Test calling add tool
                        add_request = {
                            "jsonrpc": "2.0",
                            "id": 3, 
                            "method": "tools/call",
                            "params": {
                                "name": "add",
                                "arguments": {"a": 15, "b": 27}
                            }
                        }
                        
                        print("📤 Testing add(15, 27)...")
                        process.stdin.write(json.dumps(add_request) + '\n')
                        process.stdin.flush()
                        
                        add_response_line = process.stdout.readline()
                        if add_response_line:
                            add_response = json.loads(add_response_line.strip())
                            print(f"📥 Add response: {add_response}")
                            
                            if 'result' in add_response:
                                result = add_response['result']['content'][0]['text']
                                print(f"🧮 Math result: {result}")
                            
        # Test list_prompts
        prompts_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "prompts/list"
        }
        
        print("📤 Requesting prompts list...")
        process.stdin.write(json.dumps(prompts_request) + '\n')
        process.stdin.flush()
        
        prompts_response_line = process.stdout.readline()
        if prompts_response_line:
            prompts_response = json.loads(prompts_response_line.strip())
            print(f"📥 Prompts response: {prompts_response}")
            
            if 'result' in prompts_response and 'prompts' in prompts_response['result']:
                prompts = prompts_response['result']['prompts']
                print(f"💬 Available prompts: {[prompt['name'] for prompt in prompts]}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        # Read stderr for any error messages
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"🚨 Server stderr: {stderr_output}")
    
    finally:
        # Clean up
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("🧹 Test completed")

async def test_direct_functions():
    """Test the math functions directly"""
    print("\n🧪 Testing Math Functions Directly...")
    
    from math_server import add, sub, multiply, Add_Prompt, Sub_Prompt, Multiply_Prompt
    
    # Test math operations
    tests = [
        (add, 10, 5, "add(10, 5)"),
        (sub, 20, 8, "sub(20, 8)"), 
        (multiply, 6, 9, "multiply(6, 9)")
    ]
    
    for func, a, b, desc in tests:
        try:
            result = await func(a, b)
            print(f"✅ {desc} = {result}")
        except Exception as e:
            print(f"❌ {desc} failed: {e}")
    
    # Test prompts
    prompt_tests = [
        (Add_Prompt, 7, 3, "Add_Prompt(7, 3)"),
        (Sub_Prompt, 15, 4, "Sub_Prompt(15, 4)"),
        (Multiply_Prompt, 8, 6, "Multiply_Prompt(8, 6)")
    ]
    
    for func, a, b, desc in prompt_tests:
        try:
            result = await func(a, b)
            print(f"💬 {desc} = '{result}'")
        except Exception as e:
            print(f"❌ {desc} failed: {e}")

async def main():
    """Run all tests"""
    print("🚀 Starting Math MCP Server Tests\n")
    
    await test_direct_functions()
    await test_mcp_stdio()
    
    print("\n✨ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())