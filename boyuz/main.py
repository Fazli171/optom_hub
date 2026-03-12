import asyncio
import logging
import io
from PIL import Image
import easyocr

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, BufferedInputFile

from config import TOKEN, ADMIN_ID, CHANNEL_ID, YOUTUBE_CHANNEL
from data import movies, users, used_photos

# logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# OCR model
reader = easyocr.Reader(['en', 'ru'], gpu=False)

TARGET_WORDS = {
    "subscribed",
    "подписаны",
    "obuna bolgan",
    "views",
    "k views"
}


def get_text_from_photo(image_bytes: bytes):
    img = Image.open(io.BytesIO(image_bytes))

    img = img.resize((640, 640))

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")

    result = reader.readtext(buffer.getvalue(), detail=0)

    return " ".join(result).lower()


@dp.message(CommandStart())
async def start(message: Message):

    if message.from_user.id in users:
        await message.answer("🎬 Kino kodini yuboring:")
        return

    caption = (
        f"📢 Botdan foydalanish uchun YouTube kanalimizga obuna bo'ling:\n"
        f"{YOUTUBE_CHANNEL}\n\n"
        f"📸 Obuna bo'lganingiz haqida screenshot yuboring!"
    )

    try:
        photo = BufferedInputFile.from_file("exsep.jpg")
        await message.answer_photo(photo, caption=caption)
    except:
        await message.answer(caption)


@dp.message(F.photo)
async def check_screenshot(message: Message):

    user_id = message.from_user.id
    photo = message.photo[-1]

    if photo.file_unique_id in used_photos:
        await message.answer("❌ Bu screenshot oldin ishlatilgan")
        return

    status = await message.answer("🔍 Tekshirilmoqda...")

    try:

        file = await bot.get_file(photo.file_id)
        file_bytes = await bot.download_file(file.file_path)

        image_bytes = file_bytes.read()

        text = await asyncio.to_thread(get_text_from_photo, image_bytes)

        if any(word in text for word in TARGET_WORDS):

            users.add(user_id)
            used_photos.add(photo.file_unique_id)

            await status.edit_text(
                "✅ Tasdiqlandi!\n\n🎬 Endi kino kodini yuboring"
            )

        else:
            await status.edit_text(
                "❌ Obuna topilmadi.\n\nKanalga obuna bo'lib qayta screenshot yuboring."
            )

    except Exception as e:
        logging.error(e)
        await status.edit_text("⚠️ Xatolik yuz berdi. Qayta yuboring.")


@dp.message(F.text)
async def movie_code(message: Message):

    user_id = message.from_user.id
    code = message.text.strip()

    if user_id not in users:
        await message.answer("⚠️ Avval screenshot yuboring!")
        return

    if code not in movies:
        await message.answer("❌ Bunday kodli kino yo'q")
        return

    try:

        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=CHANNEL_ID,
            message_id=movies[code]
        )

    except:
        await message.answer("❌ Kino yuborishda xatolik")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())