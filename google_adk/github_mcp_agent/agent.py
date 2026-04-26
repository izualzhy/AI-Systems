import os

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from google_adk.adk_utils import ark_seed20_model

GITHUB_TOKEN = os.environ.get("GITHUB_FINE_GRAINED_ACCESS_TOKEN")

os.environ['HTTP_RPOXY'] = 'http://127.0.0.1:7897'
os.environ['HTTPS_RPOXY'] = 'http://127.0.0.1:7897'

root_agent = Agent(
    model=ark_seed20_model,
    name="github_agent",
    instruction="Help users get information from GitHub",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://api.githubcopilot.com/mcp/",
                headers={
                    "Authorization": f"Bearer {GITHUB_TOKEN}",
                    "X-MCP-Toolsets": "all",
                    "X-MCP-Readonly": "true"
                },
            ),
        )
    ],
)
