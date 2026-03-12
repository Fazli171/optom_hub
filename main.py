import asyncio
import logging
import requests

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, BufferedInputFile

from config import TOKEN, CHANNEL_ID, YOUTUBE_CHANNEL
from data import movies, users, used_photos

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

OCR_API_KEY = "helloworld"


def ocr_request(image_bytes, lang):

    payload = {
        "apikey": OCR_API_KEY,
        "language": lang,
        "isOverlayRequired": False
    }

    files = {
        "file": ("image.jpg", image_bytes)
    }

    r = requests.post(
        "https://api.ocr.space/parse/image",
        data=payload,
        files=files
    )

    result = r.json()

    print(f"\n===== OCR RESPONSE ({lang}) =====")
    print(result)
    print("===============================\n")

    try:
        return result["ParsedResults"][0]["ParsedText"].lower()
    except:
        return ""


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

        # 1️⃣ Ingliz tilida tekshiradi
        text_eng = await asyncio.to_thread(ocr_request, image_bytes, "eng")

        print("\n===== OCR TEXT ENG =====")
        print(text_eng)

        eng_keywords = [
            "subscribed",
            "subscriber",
            "obuna qilgan"
        ]

        if any(word in text_eng for word in eng_keywords):

            users.add(user_id)
            used_photos.add(photo.file_unique_id)

            await status.edit_text(
                "✅ Obuna tasdiqlandi (ENG)\n\n🎬 Endi kino kodini yuboring"
            )
            return


        # 2️⃣ Agar inglizcha topilmasa rus tilida tekshiradi
        text_rus = await asyncio.to_thread(ocr_request, image_bytes, "rus")

        print("\n===== OCR TEXT RUS =====")
        print(text_rus)

        rus_keywords = [
            "подпис",
            "подписан",
            "подписаться",
            "вы подписаны",
            "Вы подписа"
        ]

        if any(word in text_rus for word in rus_keywords):

            users.add(user_id)
            used_photos.add(photo.file_unique_id)

            await status.edit_text(
                "✅ Obuna tasdiqlandi (RUS)\n\n🎬 Endi kino kodini yuboring"
            )

        else:

            await status.edit_text(
                "❌ Obuna aniqlanmadi.\n\nKanalga obuna bo'lib qayta screenshot yuboring."
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