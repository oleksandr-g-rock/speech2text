<div align="center">
<img src="logo_s2t.png" alt="Voice Transcriber Logo" width="200"/>

# 🎙️ AI Voice Transcriber Bot
**Turn Voice into Text with the Power of AI & Telegram**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)](https://www.docker.com/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-blueviolet.svg)](https://docs.aiogram.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
</div>

---

## 🚀 The Mission
Stop wasting time listening to long, rambling voice notes. **AI Voice Transcriber** is a high-performance Telegram bot that converts audio messages into clean, readable text instantly. 

Built with **Aiogram 3.x** and powered by **OpenAI Whisper**, it’s designed for speed, privacy, and handling even the longest "podcast-style" voice messages your friends send you.

---

## ✨ Superpowers
* **⚡ Webhook Powered:** Zero-latency response. It hears the message and starts working immediately.
* **🧠 Language Genius:** Automatically detects the language (English, Spanish, Ukrainian, etc.) without you telling it.
* **📏 Smart Chunking:** Bypasses Telegram's 4096-character limit by intelligently splitting long transcripts into multiple messages.
* **⏳ Marathon Runner:** Custom timeout logic allows processing of massive audio files (up to 15+ minutes) without breaking a sweat.
* **🔒 Privacy Guard:** Works with self-hosted Whisper instances. Your voice data stays on your infrastructure.
* **👥 Group Ready:** Drop it in a group chat, turn off Privacy Mode, and it will transcribe everything for everyone.

---



## 🛠️ Quick Start (Docker)

Since the project is fully containerized, deployment is a breeze.

### 1. Build the Image
Navigate to your project folder and run:

    docker build -t voice-transcriber .

### 2. Run the Container
Run the bot while passing your specific credentials as environment variables:

    docker run -d \
      --name voice-bot \
      -e TELEGRAM_TOKEN=your_token_here \
      -e BASE_URL=https://your-domain.com \
      -e WHISPER_API_URL=http://your-whisper-api:9000/v1 \
      -e PORT=8000 \
      -p 8000:8000 \
      voice-transcriber

---

## ⚙️ Environment Configuration

| Variable | Importance | Description |
| :--- | :--- | :--- |
| **TELEGRAM_TOKEN** | Critical | Get this from [@BotFather](https://t.me/BotFather). |
| **BASE_URL** | Critical | Your public HTTPS domain (Webhooks require SSL). |
| **WHISPER_API_URL** | Critical | The endpoint for your Whisper ASR service. |
| **PORT** | Optional | Internal port for the bot server (Default: 8000). |

---

## 🏗️ How It Works



1.  **Trigger:** User sends a voice note. Telegram hits our Webhook.
2.  **Fetch:** The bot grabs the file from Telegram's servers.
3.  **Process:** The audio is streamed to the Whisper API.
4.  **Polish:** The bot formats the text, splits it if it's too long, and replies directly to the user.

---

## 🤝 Contributing
Got a cool idea or a bug fix? Feel free to fork the repo and open a Pull Request. Let's make transcription even better!

## 📄 License
This project is open-source and available under the **MIT License**.

---
<div align="center">
  Built with ❤️ by AI enthusiasts.
</div>