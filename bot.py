import os
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import URLInputFile
from aiohttp import web

from downloader import download_video, get_file_size, PRESETS

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")  # from Render env
WEBHOOK_HOST = os.getenv("WEBHOOK_URL")  # render URL
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await message.answer("👋 Send me any YouTube/Instagram/Facebook video link!")

@router.message(F.text)
async def ask_quality(message: Message, state: FSMContext):
    url = message.text.strip()
    if not any(x in url for x in ["youtu", "instagram", "facebook", "fb.watch"]):
        return await message.answer("❌ Invalid link. Send YouTube/IG/FB link only.")

    await state.set_data({"url": url})

    kb = [
        [("📱 360p", "360p"), ("📺 720p", "720p")],
        [("🖥️ 1080p", "1080p"), ("⭐ Best", "best")],
        [("🎵 Audio Only", "audio")]
    ]

    inline = [
        [web.InlineKeyboardButton(text=t, callback_data=d) for t, d in row]
        for row in kb
    ]

    await message.answer("🎥 Choose quality:", reply_markup=web.InlineKeyboardMarkup(inline_keyboard=inline))

@router.callback_query(F.data.in_(PRESETS.keys()))
async def dl_video(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    url = data.get("url")
    preset = callback.data

    await callback.message.edit_text("⏳ Downloading...")

    try:
        file_path = download_video(url, preset)
        size = get_file_size(file_path)
        caption = f"✅ {preset} • {size/1024/1024:.1f}MB"

        with open(file_path, "rb") as f:
            if size <= 50 * 1024 * 1024:
                await callback.message.answer_video(f, caption=caption)
            else:
                await callback.message.answer_document(f, caption=caption)

        os.remove(file_path)
        await callback.message.delete()
        await state.clear()
    except Exception as e:
        await callback.message.edit_text(f"❌ Error: {e}")

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)
    logging.info("Webhook set!")

async def init_app():
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    app = web.Application()
    app["bot"] = bot

    async def handler(request):
        body = await request.json()
        update = Bot.parse_update(body)
        await dp.update.update(update)
        return web.Response()

    app.router.add_post(WEBHOOK_PATH, handler)
    await on_startup(bot)
    return app

if __name__ == "__main__":
    web.run_app(init_app(), port=int(os.getenv("PORT", 10000)))
