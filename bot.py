import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from downloader import download_video, get_file_size, PRESETS

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    router = Router()
    dp.include_router(router)

    @router.message(CommandStart())
    async def cmd_start(message: Message):
        await message.answer(
            "👋 Welcome to Video Downloader Bot!\n\n"
            "Send me a **YouTube**, **Instagram Reel**, or **Facebook** video URL,\n"
            "and I'll provide quality options to download."
        )

    @router.message(F.text & ~F.text.startswith("/"))
    async def handle_url(message: Message, state: FSMContext):
        url = message.text.strip()
        # Basic URL validation
        if not any(domain in url.lower() for domain in ["youtube.com", "youtu.be", "instagram.com", "facebook.com", "fb.watch"]):
            await message.answer("❌ Please send a valid YouTube, Instagram Reel, or Facebook video URL.")
            return

        await state.set_data({"url": url})

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="📱 360p", callback_data="360p"),
                    InlineKeyboardButton(text="📺 720p", callback_data="720p"),
                ],
                [
                    InlineKeyboardButton(text="🖥️ 1080p", callback_data="1080p"),
                    InlineKeyboardButton(text="⭐ Best", callback_data="best"),
                ],
                [InlineKeyboardButton(text="🎵 Audio only", callback_data="audio")],
            ]
        )
        await message.answer("🎥 Choose quality:", reply_markup=keyboard)

    @router.callback_query(F.data.in_(PRESETS.keys()))
    async def process_quality(callback: CallbackQuery, state: FSMContext):
        preset = callback.data
        data = await state.get_data()
        url = data.get("url")

        if not url:
            await callback.answer("❌ No URL found. Send a URL first.")
            return

        await callback.message.edit_text("⏳ Downloading... This may take a moment.")

        try:
            file_path = await asyncio.to_thread(download_video, url, preset)
            size_bytes = await asyncio.to_thread(get_file_size, file_path)
            caption = f"✅ Downloaded: {preset.title()}\nSize: {size_bytes / (1024**2):.1f} MB"

            if size_bytes <= 50 * 1024 * 1024:
                with open(file_path, "rb") as video_file:
                    await callback.message.answer_video(video_file, caption=caption)
            else:
                with open(file_path, "rb") as doc_file:
                    await callback.message.answer_document(doc_file, caption=caption)

            # Cleanup
            os.remove(file_path)
            try:
                os.rmdir("downloads")
            except OSError:
                pass  # Not empty or doesn't exist

            await callback.message.delete()  # Clean up "Downloading" message

        except Exception as e:
            error_msg = f"❌ Download failed: {str(e)}"
            await callback.message.edit_text(error_msg)

        await callback.answer()
        await state.clear()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())