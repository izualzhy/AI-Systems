from google.adk.agents.llm_agent import Agent

# ./adk_agent_samples/mcp_agent/agent.py
import os # Required for path operations
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from google_adk.adk_utils import ark_seed20_model

TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "accessible_files")
PATH_TO_YOUR_MCP_SERVER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "my_adk_mcp_server.py")
PYTHON_EXECUTABLE = "/Users/yingz/Documents/work/code/python312/bin/python3"


root_agent = LlmAgent(
    model=ark_seed20_model,
    name='filesystem_and_web_read_assistant_agent',
    instruction="""
    Help the user manage their files. You can list files, read files, etc.
    And for web read, Use the 'load_web_page' tool to fetch content from a URL provided by the user.
    """,
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",  # Argument for npx to auto-confirm install
                        "@modelcontextprotocol/server-filesystem",
                        # IMPORTANT: This MUST be an ABSOLUTE path to a folder the
                        # npx process can access.
                        # Replace with a valid absolute path on your system.
                        # For example: "/Users/youruser/accessible_mcp_files"
                        # or use a dynamically constructed absolute path:
                        os.path.abspath(TARGET_FOLDER_PATH),
                    ],
                ),
            ),
            # Optional: Filter which tools from the MCP server are exposed
            # tool_filter=['list_directory', 'read_file']
        ),
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command=PYTHON_EXECUTABLE, # Command to run your MCP server script
                    args=[PATH_TO_YOUR_MCP_SERVER_SCRIPT], # Argument is the path to the script
                    env={"PYTHONUNBUFFERED": "1"},  # Ensure Python output is not buffered
                )
            ),
            # tool_filter=['load_web_page'] # Optional: ensure only specific tools are loaded
        )
    ],
)
