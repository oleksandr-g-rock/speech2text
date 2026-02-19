"""Unit tests for the transcribe_audio function in main.py."""
import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Force valid env variables before importing main so sys.exit(1) is not triggered
# and aiogram token validation passes (format: digits:alphanumeric-35chars)
os.environ["TELEGRAM_TOKEN"] = "123456789:AABBCCDDEEFFaabbccddeeff1234567890X"
os.environ["BASE_URL"] = "https://example.com"
os.environ["GROQ_WHISPER_API_KEY"] = "test_groq_key"

import main  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_aiohttp_response(status: int, data: bytes = b"audio"):
    """Return a mock aiohttp response context manager."""
    response = MagicMock()
    response.status = status
    response.read = AsyncMock(return_value=data)
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=response)
    cm.__aexit__ = AsyncMock(return_value=False)
    return cm


def _make_session(download_response):
    """Return a mock aiohttp.ClientSession context manager."""
    session = MagicMock()
    session.get = MagicMock(return_value=download_response)
    session_cm = MagicMock()
    session_cm.__aenter__ = AsyncMock(return_value=session)
    session_cm.__aexit__ = AsyncMock(return_value=False)
    return session_cm


def _make_groq_client(text: str):
    """Return a mock AsyncGroq client that returns a transcription."""
    transcription = MagicMock()
    transcription.text = text

    create_mock = AsyncMock(return_value=transcription)
    audio_mock = MagicMock()
    audio_mock.transcriptions.create = create_mock

    client = MagicMock()
    client.audio = audio_mock
    return client, create_mock


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_transcribe_audio_success():
    """Happy path: download succeeds, Groq returns a transcription."""
    expected_text = "Привіт, як справи?"
    audio_bytes = b"fake_ogg_audio"

    download_response = _make_aiohttp_response(200, audio_bytes)
    session_cm = _make_session(download_response)
    groq_client, create_mock = _make_groq_client(expected_text)

    with patch("aiohttp.ClientSession", return_value=session_cm), \
         patch("main.AsyncGroq", return_value=groq_client):
        result = await main.transcribe_audio("https://example.com/voice.ogg")

    assert result == expected_text
    create_mock.assert_awaited_once()
    call_kwargs = create_mock.call_args.kwargs
    assert call_kwargs["model"] == "whisper-large-v3"
    assert call_kwargs["response_format"] == "verbose_json"
    file_arg = call_kwargs["file"]
    assert file_arg[0] == "voice.ogg"
    assert file_arg[1] == audio_bytes


@pytest.mark.asyncio
async def test_transcribe_audio_download_error():
    """If Telegram returns non-200 status, an error message is returned."""
    download_response = _make_aiohttp_response(404)
    session_cm = _make_session(download_response)

    with patch("aiohttp.ClientSession", return_value=session_cm):
        result = await main.transcribe_audio("https://example.com/voice.ogg")

    assert "Download Error" in result
    assert "404" in result


@pytest.mark.asyncio
async def test_transcribe_audio_connection_error():
    """If the download raises an exception, a connection error message is returned."""
    session = MagicMock()
    session.get = MagicMock(side_effect=Exception("network failure"))
    session_cm = MagicMock()
    session_cm.__aenter__ = AsyncMock(return_value=session)
    session_cm.__aexit__ = AsyncMock(return_value=False)

    with patch("aiohttp.ClientSession", return_value=session_cm):
        result = await main.transcribe_audio("https://example.com/voice.ogg")

    assert "Connection Error" in result


@pytest.mark.asyncio
async def test_transcribe_audio_groq_error():
    """If the Groq API raises an exception, an error message is returned."""
    audio_bytes = b"fake_ogg_audio"
    download_response = _make_aiohttp_response(200, audio_bytes)
    session_cm = _make_session(download_response)

    groq_client = MagicMock()
    groq_client.audio.transcriptions.create = AsyncMock(
        side_effect=Exception("Groq API unreachable")
    )

    with patch("aiohttp.ClientSession", return_value=session_cm), \
         patch("main.AsyncGroq", return_value=groq_client):
        result = await main.transcribe_audio("https://example.com/voice.ogg")

    assert "Cannot reach Groq Whisper API" in result


@pytest.mark.asyncio
async def test_transcribe_audio_timeout():
    """If the Groq call times out, a timeout error message is returned."""
    audio_bytes = b"fake_ogg_audio"
    download_response = _make_aiohttp_response(200, audio_bytes)
    session_cm = _make_session(download_response)

    groq_client = MagicMock()
    groq_client.audio.transcriptions.create = AsyncMock(
        side_effect=asyncio.TimeoutError()
    )

    with patch("aiohttp.ClientSession", return_value=session_cm), \
         patch("main.AsyncGroq", return_value=groq_client):
        result = await main.transcribe_audio("https://example.com/voice.ogg")

    assert "Time limit exceeded" in result


@pytest.mark.asyncio
async def test_transcribe_audio_groq_key_passed():
    """The AsyncGroq client must be initialised with GROQ_WHISPER_API_KEY."""
    audio_bytes = b"fake_ogg_audio"
    download_response = _make_aiohttp_response(200, audio_bytes)
    session_cm = _make_session(download_response)

    transcription = MagicMock(text="hello")
    groq_client = MagicMock()
    groq_client.audio.transcriptions.create = AsyncMock(return_value=transcription)

    with patch("aiohttp.ClientSession", return_value=session_cm), \
         patch("main.AsyncGroq", return_value=groq_client) as mock_async_groq:
        await main.transcribe_audio("https://example.com/voice.ogg")

    mock_async_groq.assert_called_once_with(api_key=main.GROQ_WHISPER_API_KEY)
