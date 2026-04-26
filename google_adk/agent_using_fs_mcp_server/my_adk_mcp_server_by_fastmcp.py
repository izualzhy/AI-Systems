#!/usr/bin/env python
# coding=utf-8
# my_adk_mcp_server_fastmcp.py
import json
import sys
from typing import Any
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.load_web_page import load_web_page

load_dotenv()

print("Initializing ADK load_web_page tool...", file=sys.stderr)
adk_tool_to_expose = FunctionTool(load_web_page)
print(f"ADK tool '{adk_tool_to_expose.name}' initialized.", file=sys.stderr)

print("Creating FastMCP Server instance...", file=sys.stderr)
app = FastMCP("adk-tool-exposing-mcp-server", stateless_http=True)

@app.tool(name=adk_tool_to_expose.name, description=adk_tool_to_expose.description)
async def load_web_page_wrapper(**kwargs: Any) -> str:
    """Wrapper for ADK load_web_page tool."""
    print(f"MCP Server: Calling ADK tool with args: {kwargs}", file=sys.stderr)
    try:
        result = await adk_tool_to_expose.run_async(args=kwargs, tool_context=None)
        print(f"MCP Server: ADK tool executed successfully.", file=sys.stderr)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"MCP Server: Error executing ADK tool: {e}", file=sys.stderr)
        return json.dumps({"error": f"Failed to execute tool: {str(e)}"})

def run_mcp_stdio_server():
    print("MCP Stdio Server: Starting...", file=sys.stderr)
    app.run(transport="stdio")
    print("MCP Stdio Server: Stopped.", file=sys.stderr)

def run_mcp_streamable_http_server(host: str = "0.0.0.0", port: int = 8000):
    print(f"MCP Streamable HTTP Server: Starting on {host}:{port}...", file=sys.stderr)
    # 获取底层的 FastAPI 应用并添加 CORS 中间件
    fastapi_app = app.streamable_http_app()
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    import uvicorn
    uvicorn.run(fastapi_app, host=host, port=port)
    print("MCP Streamable HTTP Server: Stopped.", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "http":
        host = sys.argv[2] if len(sys.argv) > 2 else "0.0.0.0"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
        print(f"Launching MCP Server via Streamable HTTP on {host}:{port}...", file=sys.stderr)
        try:
            run_mcp_streamable_http_server(host=host, port=port)
        except KeyboardInterrupt:
            print("\nMCP Server (HTTP) stopped by user.", file=sys.stderr)
        except Exception as e:
            print(f"MCP Server (HTTP) error: {e}", file=sys.stderr)
    else:
        print("Launching MCP Server via stdio...", file=sys.stderr)
        try:
            run_mcp_stdio_server()
        except KeyboardInterrupt:
            print("\nMCP Server (stdio) stopped by user.", file=sys.stderr)
        except Exception as e:
            print(f"MCP Server (stdio) error: {e}", file=sys.stderr)
