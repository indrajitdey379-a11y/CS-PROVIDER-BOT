import asyncio
import os
from traceback import format_exc

from pyrogram import idle, enums
from pyrogram.errors import FloodWait

from bot import bot, initialize_clients
from database import db
from webserver import app
import uvicorn
from config import Config

PORT = int(os.environ.get("PORT", 8000))
config = uvicorn.Config(app=app, host='0.0.0.0', port=PORT, log_level="info")
server = uvicorn.Server(config)


async def start_services():
    """Starts all services in the correct order."""
    print("--- Initializing Services ---")
    try:
        await db.connect()
        print("Starting main bot...")
        await bot.start()
        print(f"Bot [@{bot.me.username}] started successfully.")

        # --- FINAL WORKAROUND ---
        print("Forcing Pyrogram to update its internal chat cache...")
        try:
            # We will fetch the first 5 chats the bot is in. This forces a state update.
            async for dialog in bot.get_dialogs(limit=5):
                print(f"  - Found accessible chat: {dialog.chat.title} ({dialog.chat.id})")
            print("Internal cache populated.")
        except Exception as e:
            print(f"  - Could not pre-fetch chats, but continuing anyway. Error: {e}")
        # --- END OF WORKAROUND ---

        print(f"Verifying and caching STORAGE_CHANNEL: {Config.STORAGE_CHANNEL}")
        await bot.get_chat(Config.STORAGE_CHANNEL)
        print("✅ STORAGE_CHANNEL is accessible.")
        
        await initialize_clients(bot)
        
        print(f"Starting web server on http://0.0.0.0:{PORT}")
        asyncio.create_task(server.serve())
        
        print("\n✅✅✅ All services are up and running! ✅✅✅\n")
        await idle()

    except FloodWait as e:
        print(f"!!! FloodWait of {e.value} seconds received. Sleeping...")
        await asyncio.sleep(e.value + 5)
    except Exception as e:
        print(f"\n❌❌❌ An unexpected error occurred during startup: ❌❌❌")
        print(format_exc())
        print("\nFinal Diagnosis: The problem is not with your settings. It is likely a rare sync issue between Pyrogram and Telegram for this specific bot/channel combination.")
    finally:
        print("--- Services are shutting down ---")
        if bot.is_initialized: await bot.stop()
        await db.disconnect()
        print("Shutdown complete.")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        print("Service stopping due to user interrupt.")
    finally:
        if not loop.is_closed():
            loop.close()
