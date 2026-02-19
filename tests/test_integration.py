"""Integration tests for the Groq Whisper transcription.

These tests require a valid GROQ_WHISPER_API_KEY environment variable and
a real (or reachable) audio file URL.  They are skipped automatically when
the key is not present so the test suite can still run in CI without secrets.
"""
import os
import asyncio

import pytest

GROQ_WHISPER_API_KEY = os.getenv("GROQ_WHISPER_API_KEY")
pytestmark = pytest.mark.skipif(
    not GROQ_WHISPER_API_KEY,
    reason="GROQ_WHISPER_API_KEY is not set – skipping integration tests",
)


@pytest.mark.asyncio
async def test_groq_transcription_direct():
    """Call the Groq API directly with a tiny silent WAV and expect a string back."""
    from groq import AsyncGroq

    # Minimal valid WAV: 44-byte header + 1 sample of silence (16-bit, 16 kHz, mono)
    # fmt: off
    wav_header = bytes([
        0x52, 0x49, 0x46, 0x46,  # "RIFF"
        0x26, 0x00, 0x00, 0x00,  # chunk size = 38
        0x57, 0x41, 0x56, 0x45,  # "WAVE"
        0x66, 0x6D, 0x74, 0x20,  # "fmt "
        0x10, 0x00, 0x00, 0x00,  # subchunk1 size = 16
        0x01, 0x00,              # PCM
        0x01, 0x00,              # 1 channel
        0x80, 0x3E, 0x00, 0x00,  # 16000 Hz
        0x00, 0x7D, 0x00, 0x00,  # byte rate = 32000
        0x02, 0x00,              # block align = 2
        0x10, 0x00,              # bits per sample = 16
        0x64, 0x61, 0x74, 0x61,  # "data"
        0x02, 0x00, 0x00, 0x00,  # subchunk2 size = 2
        0x00, 0x00,              # 1 silent sample
    ])
    # fmt: on

    client = AsyncGroq(api_key=GROQ_WHISPER_API_KEY)
    transcription = await client.audio.transcriptions.create(
        file=("silence.wav", wav_header),
        model="whisper-large-v3",
        temperature=0,
        response_format="verbose_json",
    )
    # The result must be a string (may be empty for a silent clip)
    assert isinstance(transcription.text, str)


@pytest.mark.asyncio
async def test_transcribe_audio_integration(tmp_path):
    """End-to-end: serve a tiny WAV locally and call transcribe_audio."""
    import aiohttp
    from aiohttp import web
    import main as app_module

    # fmt: off
    wav_bytes = bytes([
        0x52, 0x49, 0x46, 0x46,
        0x26, 0x00, 0x00, 0x00,
        0x57, 0x41, 0x56, 0x45,
        0x66, 0x6D, 0x74, 0x20,
        0x10, 0x00, 0x00, 0x00,
        0x01, 0x00, 0x01, 0x00,
        0x80, 0x3E, 0x00, 0x00,
        0x00, 0x7D, 0x00, 0x00,
        0x02, 0x00, 0x10, 0x00,
        0x64, 0x61, 0x74, 0x61,
        0x02, 0x00, 0x00, 0x00,
        0x00, 0x00,
    ])
    # fmt: on

    # Spin up a tiny aiohttp server to serve the file
    async def serve_audio(_request):
        return web.Response(body=wav_bytes, content_type="audio/wav")

    runner_app = web.Application()
    runner_app.router.add_get("/audio.wav", serve_audio)
    runner = web.AppRunner(runner_app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]

    try:
        url = f"http://127.0.0.1:{port}/audio.wav"
        result = await app_module.transcribe_audio(url)
        assert isinstance(result, str)
        assert not result.startswith("❌")
    finally:
        await runner.cleanup()
