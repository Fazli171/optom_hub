# kino kodlari
# "kod": xabar_id (kanaldagi xabar tartib raqami)
movies = {
    "101": 8,
    "102": 6,
    "103": 10
}

# foydalanuvchilar (obuna bo'lganlar IDsi)
users = set()

# ishlatilgan screenshotlar (dublikatni oldini olish uchun)
used_photos = set()  # <--- Shuni qo'shish shart edi!

# xato yuborganlar
error_users = {}

# username lar
usernames = {}