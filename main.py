import os
import sys
import logging
import asyncio
from aiohttp import web
import aiohttp
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ContentType
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# --- ENV VARIABLES ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BASE_URL = os.getenv("BASE_URL")
WHISPER_API_URL = os.getenv("WHISPER_API_URL")

# --- DYNAMIC PORT CONFIGURATION ---
# This is the magic part. It reads the PORT variable from Coolify.
# If you don't set it in Coolify, it defaults to 8000.
WEB_SERVER_PORT = int(os.getenv("PORT", 8000))
WEB_SERVER_HOST = "0.0.0.0"
WEBHOOK_PATH = "/webhook"

# Validation
if not TELEGRAM_TOKEN or not BASE_URL or not WHISPER_API_URL:
    logger.error("❌ MISSING VARIABLES! Check TELEGRAM_TOKEN, BASE_URL, WHISPER_API_URL")
    sys.exit(1)

WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"
TRANSCRIPTION_ENDPOINT = f"{WHISPER_API_URL}/audio/transcriptions"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# ==============================================================================
# 2. LOGIC
# ==============================================================================

async def transcribe_audio(file_url: str) -> str:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(file_url) as response:
                if response.status != 200:
                    return f"❌ Download Error: {response.status}"
                audio_data = await response.read()
        except Exception as e:
            return f"❌ Connection Error (Telegram): {e}"

        form_data = aiohttp.FormData()
        form_data.add_field('file', audio_data, filename='voice.ogg')
        form_data.add_field('model', 'whisper-1')
        form_data.add_field('response_format', 'text')

        try:
            async with session.post(TRANSCRIPTION_ENDPOINT, data=form_data) as resp:
                if resp.status == 200:
                    return await resp.text()
                else:
                    return f"❌ Whisper Error ({resp.status})"
        except Exception as e:
            logger.error(f"Whisper Connection Error: {e}")
            return "❌ Cannot reach Whisper container."

@dp.message(F.content_type == ContentType.VOICE)
async def handle_voice(message: types.Message):
    await bot.send_chat_action(message.chat.id, action="typing")
    try:
        file = await bot.get_file(message.voice.file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file.file_path}"
        text = await transcribe_audio(file_url)
        await message.reply(f"📝 {text}")
    except Exception as e:
        logger.error(f"Handler Error: {e}")
        await message.reply("❌ Error processing request.")

@dp.message()
async def handle_start(message: types.Message):
    if message.chat.type == "private":
        await message.reply("👋 Send me a voice message!")

# ==============================================================================
# 3. WEBHOOK LIFECYCLE & SERVER START
# ==============================================================================

async def on_startup(bot: Bot):
    logger.info(f"🔗 Setting Webhook to: {WEBHOOK_URL}")
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(bot: Bot):
    logger.info("🛑 Removing Webhook")
    await bot.delete_webhook()

def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    # Start the server using the dynamic port
    logger.info(f"🚀 Starting server on PORT: {WEB_SERVER_PORT}")
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

if __name__ == "__main__":
    main()