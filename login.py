"""One-time interactive Telegram login.

Run this yourself from a terminal, ONCE:   python login.py

It creates ~/.tg-digest/reader.session — an authenticated device. Every other
part of the project (including the MCP server) reuses that file silently and
never prompts again.

Never run this logic inside the MCP server: that process has no terminal, so a
prompt would block forever.
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

load_dotenv(Path.home() / ".tg-digest" / ".env")

API_ID = os.environ.get("TG_API_ID")
API_HASH = os.environ.get("TG_API_HASH")

SESSION_DIR = Path.home() / ".tg-digest"
SESSION = SESSION_DIR / "reader.session"


async def main() -> None:
    if not API_ID or not API_HASH:
        raise SystemExit(
            "Missing credentials.\n"
            "Create ~/.tg-digest/.env with:\n"
            "  TG_API_ID=1234567\n"
            "  TG_API_HASH=abc123...\n"
            "Get both from https://my.telegram.org/apps"
        )

    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    # str(SESSION) without the .session suffix — Telethon appends it itself.
    client = TelegramClient(str(SESSION_DIR / "reader"), int(API_ID), API_HASH)

    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"Already logged in as {me.first_name} (@{me.username}).")
        await client.disconnect()
        return

    phone = input("Phone number (with country code, e.g. +49...): ").strip()
    await client.send_code_request(phone)

    code = input("Code from Telegram: ").strip()
    try:
        await client.sign_in(phone=phone, code=code)
    except SessionPasswordNeededError:
        # Account has two-step verification enabled.
        password = input("Two-step verification password: ").strip()
        await client.sign_in(password=password)

    me = await client.get_me()
    print(f"\nLogged in as {me.first_name} (@{me.username}).")

    # Lock down the session file — it is a live login to your account.
    if SESSION.exists():
        SESSION.chmod(0o600)
        print(f"Session written to {SESSION} (mode 600).")

    # Quick sanity check: how many broadcast channels can we see?
    from telethon.tl.types import Channel

    n = 0
    async for dialog in client.iter_dialogs():
        ent = dialog.entity
        if isinstance(ent, Channel) and getattr(ent, "broadcast", False):
            n += 1
    print(f"Found {n} subscribed channels.")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())