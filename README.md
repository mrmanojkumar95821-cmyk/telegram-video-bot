# Telegram Video Downloader Bot

## 🚀 Quick Start (Local)

1. **Clone/Download** this repo
2. **Setup env**:
   ```
   cp .env.example .env
   # Edit .env: BOT_TOKEN=your_botfather_token
   ```
3. **Install deps**:
   ```
   pip install -r requirements.txt
   ```
4. **Run**:
   ```
   python bot.py
   ```

## 📱 Usage

1. `/start` - Get welcome message
2. Send **YouTube**, **Instagram Reel**, or **Facebook** video URL
3. Choose quality from inline buttons: **360p**, **720p**, **1080p**, **Best**, **Audio only**
4. Receive video (or document if >50MB)

**Supported**: Public videos only. Single videos (no playlists/shorts lists).

## ⚙️ Features

- Quality presets via yt-dlp format selectors
- Auto-detect file size: `send_video` (<=50MB) or `send_document` (>50MB)
- Async non-blocking downloads
- Temp file cleanup
- Basic URL validation & error handling

## 🌐 Deploy on Render - Detailed Step-by-Step Guide (Free Tier Available)

### Step 1: Setup GitHub Repository

In your project directory (`telegrambot`):

```cmd
git init
git add .
git commit -m "Initial commit: Telegram Video Downloader Bot"
```

1. Go to [github.com/new](https://github.com/new) → Create new repo (e.g., `telegram-video-bot`) **Public**
2. Copy repo URL: `https://github.com/YOUR_USERNAME/telegram-video-bot.git`

```cmd
git remote add origin https://github.com/YOUR_USERNAME/telegram-video-bot.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render

1. Sign up/Login at [render.com](https://render.com) (GitHub login easy)
2. Dashboard → **New** → **Background Worker** (for polling bots)
3. **Repository** → Connect GitHub → Authorize → Select your repo (`telegram-video-bot`)
4. **Name**: `video-downloader-bot` (auto or custom)
5. **Region**: Choose closest (e.g., Singapore for Asia)
6. **Branch**: `main`
7. **Build Command**:
   ```
   pip install -r requirements.txt
   ```
8. **Start Command**:
   ```
   python bot.py
   ```
9. **Environment** → **Add Environment Variable**:
   | Key       | Value                  |
   |-----------|------------------------|
   | `BOT_TOKEN` | `your_actual_bot_token` |
10. **Create Background Worker** → Render builds & deploys (2-5 min)

### Step 3: Verify Deployment

- **Logs** tab: See "Bot started polling" → No errors
- Test bot in Telegram: `/start`, send YT URL
- Auto-deploys on git push!

**Tips**:
- Free tier: 750 hours/month (~24/7)
- Disk ephemeral: Downloads /tmp ok, but our code uses `./downloads` cleaned
- Scale: Multiple instances if high traffic
- Webhook alt: Change to Web Service, set webhook URL

[Render Docs: Background Workers](https://render.com/docs/background-workers)

## 🛠️ Customization

- Edit [`downloader.py`](downloader.py) `PRESETS` for new qualities
- Add webhook: Modify `main()` for `dp.start_webhook(...)` (Render web service)

## ⚠️ Limitations & Legal

- **Public videos only** (no login/private)
- Respect YouTube/Instagram/Facebook ToS
- Telegram limits: 50MB video, 2GB document, 4MB audio?
- No playlists, channels, or live streams
- Rate limits may apply (yt-dlp handles)

## 🔧 Troubleshooting

- **No response**: Check token, logs
- **Download fails**: Private video? Invalid URL?
- **Large files**: Sent as document
- Logs: `logging.INFO`

**Get Bot Token**: [@BotFather](https://t.me/botfather) → /newbot

⭐ Star if useful!