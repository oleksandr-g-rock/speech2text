<div align="center">
<img src="logo_s2t.png" alt="Voice Transcriber Logo" width="200"/>

# 🎙️ AI Voice Transcriber Bot
**Turn Voice into Text with the Power of AI & Telegram**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-blueviolet.svg?logo=telegram)](https://docs.aiogram.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Whisper](https://img.shields.io/badge/Model-Whisper-74aa9c.svg)](https://github.com/openai/whisper)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
</div>

---

## 🚀 The Mission
Stop wasting time listening to long, rambling voice notes. **AI Voice Transcriber** is a high-performance Telegram bot that converts audio messages into clean, readable text instantly.

Built with **Aiogram 3.x**, it serves as a bridge between Telegram and the **OpenAI Whisper** protocol.

### 🎯 Why this bot?
Unlike rigid solutions, **you choose the brain**. Connect this bot to:
1.  **Self-Hosted Whisper:** Run it locally on your GPU for **100% privacy** and zero cost.
2.  **OpenAI-Compatible APIs:** Connect to any cloud provider supporting the Whisper schema.

---

## ✨ Superpowers

* **⚡ Webhook Powered:** Zero-latency response. The bot reacts the moment the audio hits the server.
* **🔌 Backend Agnostic:** Works with **any** API endpoint that speaks "Whisper" (Local Docker, Faster-Whisper, or Cloud).
* **📏 Smart Chunking:** Bypasses Telegram's 4096-character limit by intelligently splitting long transcripts into readable parts.
* **⏳ Marathon Ready:** Custom 15-minute timeout logic allows processing massive "podcast-style" voice notes without crashing.
* **🗣️ Polyglot:** Automatically detects languages (English, Ukrainian, Spanish, etc.) and transcribes them faithfully.

---

## 🛠️ Quick Start (Docker)

The project is fully containerized. You can run it in seconds.

### 1. Build the Image
    docker build -t voice-transcriber .

### 2. Run the Container
Replace the variables with your actual data.

    docker run -d \
      --name voice-bot \
      -p 8000:8000 \
      -e TELEGRAM_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11" \
      -e BASE_URL="[https://your-public-domain.com](https://your-public-domain.com)" \
      -e WHISPER_API_URL="http://whisper-service:9000/v1" \
      -e PORT=8000 \
      voice-transcriber

---

## ⚙️ Configuration

Control the bot using Environment Variables.

| Variable | Required | Description |
| :--- | :---: | :--- |
| **TELEGRAM_TOKEN** | ✅ | Your bot token from [@BotFather](https://t.me/BotFather). |
| **BASE_URL** | ✅ | Your public HTTPS domain. **Must be SSL** (Telegram Webhooks requirement). |
| **WHISPER_API_URL** | ✅ | The address of your Speech-to-Text backend (see below). |
| **PORT** | ❌ | Internal app port (Default: `8000`). |

---

## 🔌 The "Backend Magic" (WHISPER_API_URL)

This bot is designed to be **modular**. It doesn't run the model itself; it sends audio to an API. This keeps the bot lightweight and fast.

**Option A: Local / Self-Hosted (Recommended for Privacy)**
Run a separate Docker container for Whisper (e.g., `onerahmet/openai-whisper-asr-webservice` or `fedirz/faster-whisper-server`).
    
    WHISPER_API_URL=http://localhost:9000

**Option B: Cloud / OpenAI API**
If you want to use a proxy or an enterprise endpoint compatible with OpenAI.
    
    WHISPER_API_URL=[https://api.your-provider.com/v1](https://api.your-provider.com/v1)

*Note: The code currently sends a standard POST request without an Authorization header, which is ideal for internal self-hosted networks.*

---

## 🏗️ Architecture Flow

1.  **User** sends a voice note 🎤
2.  **Telegram** sends a Webhook event to this Bot ⚡
3.  **Bot** downloads the audio file (`.ogg`) 📥
4.  **Bot** streams audio to `WHISPER_API_URL` 🌊
5.  **Whisper** returns raw text 📝
6.  **Bot** splits text (if >4000 chars) and replies to user 💬

---

## 🤝 Contributing
Got a cool idea? Maybe adding support for `Authorization` headers or different AI models?
Fork the repo, make your changes, and open a **Pull Request**.

## 📄 License
This project is open-source and available under the **MIT License**.

---
<div align="center">
  Built with ❤️ for privacy and speed.
</div>