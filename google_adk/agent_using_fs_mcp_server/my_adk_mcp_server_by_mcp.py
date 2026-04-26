#!/usr/bin/env python
# coding=utf-8
# my_adk_mcp_server_lowlevel.py
import asyncio
import json
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed, skipping .env loading", file=sys.stderr)

from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions

from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.load_web_page import load_web_page
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

print("Initializing ADK load_web_page tool...", file=sys.stderr)
adk_tool_to_expose = FunctionTool(load_web_page)
print(f"ADK tool '{adk_tool_to_expose.name}' initialized.", file=sys.stderr)

print("Creating MCP Server instance...", file=sys.stderr)
app = Server("adk-tool-exposing-mcp-server")

@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    print("MCP Server: Received list_tools request.", file=sys.stderr)
    mcp_tool_schema = adk_to_mcp_tool_type(adk_tool_to_expose)
    print(f"MCP Server: Advertising tool: {mcp_tool_schema.name}", file=sys.stderr)
    return [mcp_tool_schema]

@app.call_tool()
async def call_mcp_tool(name: str, arguments: dict) -> list[mcp_types.Content]:
    print(f"MCP Server: Received call_tool for '{name}' with args: {arguments}", file=sys.stderr)

    if name == adk_tool_to_expose.name:
        try:
            result = await adk_tool_to_expose.run_async(args=arguments, tool_context=None)
            print(f"MCP Server: ADK tool executed successfully.", file=sys.stderr)
            response_text = json.dumps(result, indent=2, ensure_ascii=False)
            return [mcp_types.TextContent(type="text", text=response_text)]
        except Exception as e:
            print(f"MCP Server: Error executing ADK tool: {e}", file=sys.stderr)
            error_text = json.dumps({"error": f"Failed to execute tool: {str(e)}"})
            return [mcp_types.TextContent(type="text", text=error_text)]
    else:
        print(f"MCP Server: Tool '{name}' not found.", file=sys.stderr)
        error_text = json.dumps({"error": f"Tool '{name}' not implemented."})
        return [mcp_types.TextContent(type="text", text=error_text)]

async def run_mcp_stdio_server():
    from mcp.server.stdio import stdio_server
    print("MCP Stdio Server: Starting...", file=sys.stderr)
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=app.name,
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
    print("MCP Stdio Server: Stopped.", file=sys.stderr)

async def run_mcp_streamable_http_server(host: str = "0.0.0.0", port: int = 8000):
    from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
    from starlette.applications import Starlette
    from starlette.routing import Mount
    from starlette.middleware.cors import CORSMiddleware
    import uvicorn

    print(f"MCP Streamable HTTP Server: Starting on {host}:{port}...", file=sys.stderr)

    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,
        json_response=True,
        stateless=True,
    )

    async def handle_streamable_http(scope, receive, send):
        await session_manager.handle_request(scope, receive, send)

    starlette_app = Starlette(
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lambda app: session_manager.run(),
    )
    
    # 添加 CORS 中间件
    starlette_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    config = uvicorn.Config(starlette_app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)

    try:
        await server.serve()
    except KeyboardInterrupt:
        print("\nMCP Streamable HTTP Server stopped by user.", file=sys.stderr)
    finally:
        await session_manager.shutdown()
        print("MCP Streamable HTTP Server: Stopped.", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "http":
        host = sys.argv[2] if len(sys.argv) > 2 else "0.0.0.0"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
        print(f"Launching MCP Server via Streamable HTTP on {host}:{port}...", file=sys.stderr)
        try:
            asyncio.run(run_mcp_streamable_http_server(host=host, port=port))
        except KeyboardInterrupt:
            print("\nMCP Server (HTTP) stopped by user.", file=sys.stderr)
        except Exception as e:
            print(f"MCP Server (HTTP) error: {e}", file=sys.stderr)
    else:
        print("Launching MCP Server via stdio...", file=sys.stderr)
        try:
            asyncio.run(run_mcp_stdio_server())
        except KeyboardInterrupt:
            print("\nMCP Server (stdio) stopped by user.", file=sys.stderr)
        except Exception as e:
            print(f"MCP Server (stdio) error: {e}", file=sys.stderr)
