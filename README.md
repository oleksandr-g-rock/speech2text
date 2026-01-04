<div align="center">

<img src="./logo_s2t.png" alt="Bot Logo" width="200" height="200">

# 🎙️ Telegram Voice Transcriber

**Turn your voice notes into text instantly.**
<br>
A robust, asynchronous Telegram bot that transcribes voice messages using OpenAI's Whisper model (or self-hosted alternatives).

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## ⚡ Features

* **🗣️ Instant Transcription:** Send a voice message, get text back.
* **🐳 Docker Native:** Easy to deploy anywhere (VPS, Local, Cloud).
* **🔄 Webhook Architecture:** Uses `aiohttp` webhooks for instant response times (no polling lag).
* **✂️ Smart Splitting:** Automatically splits long transcriptions into multiple messages to bypass Telegram's 4096 character limit.
* **⏳ Long Audio Support:** Optimized with a 15-minute timeout window to handle large files and slow hardware without crashing.
* **🌍 Universal API:** Works with any OpenAI-compatible Whisper endpoint (Local Whisper, Faster-Whisper, etc.).

---

## 🛠️ Prerequisites

1.  **Telegram Bot Token:** Get one from [@BotFather](https://t.me/BotFather).
2.  **Whisper API Endpoint:** You need a running instance of Whisper.
    * *Option A (Recommended):* Self-hosted Whisper (e.g., via Docker).
    * *Option B:* Any API that mimics the OpenAI `/v1/audio/transcriptions` format.
3.  **Public Domain (HTTPS):** Required for Webhooks (e.g., `https://your-domain.com`).

---

## 🚀 Quick Start (Docker)

The easiest way to run the bot is using Docker.

### 1. Clone the repository
```bash
git clone [https://github.com/your-username/your-repo.git](https://github.com/your-username/your-repo.git)
cd your-repo