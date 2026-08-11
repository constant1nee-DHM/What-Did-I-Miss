from typing import Any

import httpx2
from mcp.server import MCPServer

# Initialize MCPServer
mcp = MCPServer("digest_maker")

# Constants
NWS_API_BASE = "" # telegram api (telethon)
USER_AGENT = ""   # claude api 