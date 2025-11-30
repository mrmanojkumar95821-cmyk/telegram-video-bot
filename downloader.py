import os
import yt_dlp
from typing import Dict, Any

# Path of cookies file
COOKIES_FILE = "youtube_cookies.txt"

PRESETS: Dict[str, str] = {
    "360p": "best[height<=360][ext=mp4]/best[height<=360]",
    "720p": "best[height<=720][ext=mp4]/best[height<=720]",
    "1080p": "best[height<=1080][ext=mp4]/best[height<=1080]",
    "best": "best[ext=mp4]/best",
    "audio": "bestaudio[ext=m4a]/bestaudio/best",
}

def download_video(url: str, preset_key: str) -> str:
    """
    Download video using yt-dlp with preset format selector.
    Returns path to downloaded file.
    Caller must delete the file after use.
    """
    if preset_key not in PRESETS:
        raise ValueError(f"Invalid preset: {preset_key}")

    # Create temp dir if not exists
    temp_dir = "downloads"
    os.makedirs(temp_dir, exist_ok=True)
    output_template = os.path.join(temp_dir, "temp.%(ext)s")

    ydl_opts: Dict[str, Any] = {
        "format": PRESETS[preset_key],
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "merge_output_format": "mp4",
    }

    # 🔥 ADD COOKIES SUPPORT
    if os.path.exists(COOKIES_FILE):
        ydl_opts["cookiefile"] = COOKIES_FILE
    else:
        print("⚠ WARNING: links may fail.")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Find the downloaded file
    base_path = os.path.join(temp_dir, "temp")
    for ext in [".mp4", ".webm", ".mkv", ".avi", ".m4a", ".opus", ".mp3"]:
        file_path = base_path + ext
        if os.path.exists(file_path):
            return file_path

    raise FileNotFoundError("Downloaded file not found")


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    return os.path.getsize(file_path)
