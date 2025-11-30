import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from downloader import download_video, get_file_size, PRESETS

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_URL")  # Render app URL
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("👋 Send me any YouTube/Instagram/Facebook link to download!")


@router.message(F.text)
async def ask_quality(message: Message, state: FSMContext):
    url = message.text.strip()

    if not any(x in url for x in ["youtu", "instagram", "facebook", "fb.watch"]):
        return await message.answer("❌ Invalid link. Send YouTube/IG/FB video URLs only.")

    await state.set_data({"url": url})

    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📱 360p", callback_data="360p"),
                InlineKeyboardButton(text="📺 720p", callback_data="720p")
            ],
            [
                InlineKeyboardButton(text="🖥️ 1080p", callback_data="1080p"),
                InlineKeyboardButton(text="⭐ Best", callback_data="best")
            ],
            [
                InlineKeyboardButton(text="🎵 Audio only", callback_data="audio")
            ]
        ]
    )
    await message.answer("🎥 Choose quality:", reply_markup=keyboard)


@router.callback_query(F.data.in_(PRESETS.keys()))
async def dl_video(callback: CallbackQuery, state: FSMContext):
    preset = callback.data
    data = await state.get_data()
    url = data.get("url")

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
    logging.info("Webhook set: " + WEBHOOK_URL)


async def init_app():
    bot = Bot(
        TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    app = web.Application()
    app["bot"] = bot

    async def webhook_handler(request):
        update = await request.json()
        await dp.feed_webhook_update(bot, update)
        return web.Response(text="OK")

    app.router.add_post(WEBHOOK_PATH, webhook_handler)

    await on_startup(bot)
    return app


if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    web.run_app(init_app(), port=port)
