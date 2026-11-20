import os
import sys
import logging
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ContentType
from groq import AsyncGroq


# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================
# Logging is fully disabled: nothing is written anywhere.
logging.disable(logging.CRITICAL)
logger = logging.getLogger(__name__)

# --- ENV VARIABLES ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WHISPER_API_URL = os.getenv("WHISPER_API_URL")
GROQ_WHISPER_API_KEY = os.getenv("GROQ_WHISPER_API_KEY")
_TOPIC_ID_STR = os.getenv("TOPIC_ID")
TOPIC_ID = int(_TOPIC_ID_STR) if _TOPIC_ID_STR else None

# Validation
if not TELEGRAM_TOKEN or not GROQ_WHISPER_API_KEY:
    logger.error("❌ MISSING VARIABLES! Check TELEGRAM_TOKEN, GROQ_WHISPER_API_KEY")
    sys.exit(1)

# --- TIMEOUT SETTINGS ---
# 15 minutes (900 seconds)
WHISPER_TIMEOUT_SECONDS = 900 

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# ==============================================================================
# 2. LOGIC
# ==============================================================================

async def transcribe_audio(file_url: str) -> str:
    """Download audio from Telegram and transcribe it using the Groq Whisper API."""
    timeout_config = aiohttp.ClientTimeout(total=WHISPER_TIMEOUT_SECONDS)

    async with aiohttp.ClientSession(timeout=timeout_config) as session:
        try:
            async with session.get(file_url) as response:
                if response.status != 200:
                    return f"❌ Download Error: {response.status}"
                audio_data = await response.read()
        except Exception as e:
            return f"❌ Connection Error (Telegram): {e}"

    try:
        client = AsyncGroq(api_key=GROQ_WHISPER_API_KEY)
        transcription = await client.audio.transcriptions.create(
            file=("voice.ogg", audio_data),
            model="whisper-large-v3",
            temperature=0,
            response_format="verbose_json",
        )
        return transcription.text
    except asyncio.TimeoutError:
        logger.error("Groq Whisper Request Timed Out")
        return "❌ Error: Time limit exceeded (15 min)."
    except Exception as e:
        logger.error(f"Groq Whisper Error: {e}")
        return "❌ Cannot reach Groq Whisper API."

@dp.message(F.content_type == ContentType.VOICE)
async def handle_voice(message: types.Message):
    if TOPIC_ID is not None and message.message_thread_id != TOPIC_ID:
        return
    await bot.send_chat_action(message.chat.id, action="typing")
    try:
        file = await bot.get_file(message.voice.file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file.file_path}"
        
        text = await transcribe_audio(file_url)
        
        # --- SMART SPLITTING LOGIC ---
        # Telegram limit is 4096. We split by 4000 to be safe.
        if len(text) > 4000:
            # Loop through text in chunks of 4000 characters
            for x in range(0, len(text), 4000):
                chunk = text[x : x + 4000]
                await message.reply(f"📝 {chunk}")
                # Small sleep to avoid hitting Telegram spam limits
                await asyncio.sleep(0.5) 
        else:
            # Short message - send as is
            await message.reply(f"{text}")
            
    except Exception as e:
        logger.error(f"Handler Error: {e}")
        await message.reply("❌ Error processing request.")

@dp.message()
async def handle_start(message: types.Message):
    if TOPIC_ID is not None and message.message_thread_id != TOPIC_ID:
        return
    if message.chat.type == "private":
        await message.reply("👋 Send me a voice message!")

# ==============================================================================
# 3. START (LONG POLLING — no domain, no HTTPS, no open port needed)
# ==============================================================================

async def main():
    # Remove the old webhook, otherwise getUpdates fails with 409 Conflict.
    # drop_pending_updates=False keeps voice messages that arrived during the switch.
    await bot.delete_webhook(drop_pending_updates=False)
    logger.info("🚀 Starting long polling")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
