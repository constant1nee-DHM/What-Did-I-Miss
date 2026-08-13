import os
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer
from telethon import TelegramClient

load_dotenv(Path.home() / ".tg-digest" / ".env")

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
SESSION = str(Path.home() / ".tg-digest" / "reader")   
mcp = MCPServer("digest_maker")


async def get_client() -> TelegramClient:
    client = TelegramClient(SESSION, API_ID, API_HASH) # authorization check
    await client.connect()
    if not await client.is_user_authorized():
        await client.disconnect()
        raise RuntimeError("Not authorized. Run `python login.py` in a terminal first.")
    return client


@mcp.tool()
async def check_auth() -> str:
    try:
        client = await get_client()
    except RuntimeError as e:
        return f'{{"ok": false, "error": "{e}"}}'

    me = await client.get_me()
    await client.disconnect()
    return f'{{"ok": true, "account": "{me.username or me.id}"}}'


if __name__ == "__main__":
    mcp.run()