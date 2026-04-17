import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    CallbackContext,
    filters
)

from database import add_movie, get_movie, delete_movie, count_movies

BOT_TOKEN = "8538645649:AAHVWz7OZ0k7FdoLqAiuI3ihnEsihu7LQDA"
ADMIN_ID = 5660330328

CHANNELS = [
    "@Uzb_yangiliklari_qora_habarlar",
    "@Fudbol_tv_fudbol_yangiliklari",
    "@Uztop_Kinolar"
]

INSTAGRAM_URL = "https://instagram.com/uztop_kinolar"

DATA_FILE = "kino_data.json"
USERS_FILE = "users.json"
BLOCK_FILE = "block.json"

REKLAMA_MODE = {}

# ================= JSON =================
def load_json(file, default):
    if not os.path.exists(file):
        return default
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ================= OBUNA =================
def is_subscribed(user_id, bot):
    for ch in CHANNELS:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status not in ("member", "administrator", "creator"):
                return False
        except:
            return False
    return True

def subscribe_keyboard():
    btn = []
    for i, ch in enumerate(CHANNELS):
        btn.append([InlineKeyboardButton(f"📢 Kanal {i+1}", url=f"https://t.me/{ch[1:]}")])

    btn.append([InlineKeyboardButton("📷 Instagram", url=INSTAGRAM_URL)])
    btn.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")])
    return InlineKeyboardMarkup(btn)

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📷 Instagram", url=INSTAGRAM_URL)],
        [InlineKeyboardButton("🤝 Ulashish", switch_inline_query="Top Kinolar")]
    ])

# ================= START =================
def start(update: Update, context: CallbackContext):
    user = update.effective_user

    blocked = load_json(BLOCK_FILE, [])
    if user.id in blocked:
        return

    users = load_json(USERS_FILE, {})
    users[str(user.id)] = user.username or "no_username"
    save_json(USERS_FILE, users)

    if not is_subscribed(user.id, context.bot):
        update.message.reply_text(
            "🔐 Kanallarga obuna bo‘ling:",
            reply_markup=subscribe_keyboard()
        )
        return

    text = (
        "🎬 <b>TOP KINOLAR BOTIGA XUSH KELIBSIZ!</b>\n\n"
        "🔥 Eng yangi kinolar\n"
        "🔑 Maxsus KINO KODLARI orqali\n"
        "⚡ Tez va qulay tomosha\n\n"
        "📌 Foydalanish:\n"
        "👉 Kino kodini yuboring (masalan: K001)\n\n"
        "🎥 Har kuni yangi kinolar qo‘shiladi!"
    )

    update.message.reply_text(text, reply_markup=main_keyboard(), parse_mode="HTML")

# ================= CHECK =================
def check_sub(update: Update, context: CallbackContext):
    q = update.callback_query
    q.answer()

    if is_subscribed(q.from_user.id, context.bot):
        q.message.edit_text(
            "✅ Obuna tasdiqlandi!\n\nKod yuboring 👇",
            reply_markup=main_keyboard()
        )
    else:
        q.message.edit_text(
            "❌ Siz hali obuna bo‘lmadingiz!\n\n👇 Kanallarga kiring:",
            reply_markup=subscribe_keyboard()
        )

# ================= KINO =================
def kino_kod(update: Update, context: CallbackContext):
    user = update.effective_user

    blocked = load_json(BLOCK_FILE, [])
    if user.id in blocked:
        return

    if not is_subscribed(user.id, context.bot):
        update.message.reply_text(
            "❌ Siz kanallarga obuna bo‘lmagansiz!\n\n👇 Pastdagi tugmani bosing",
            reply_markup=subscribe_keyboard()
        )
        return

    code = update.message.text.strip().upper()
    movie = get_movie(code)

    if not movie:
        update.message.reply_text("❌ Kino topilmadi!")
        return

    caption = (
        "🎬 <b>KINO TAYYOR!</b>\n\n"
        f"🔑 <b>Kod:</b> {code}\n\n"
        "🎥 Har kuni yangi kinolar\n"
        "📲 Instagram yangiliklar\n\n"
        "🤖 @UzTopKinolar_bot"
    )

    update.message.reply_video(
        video=movie[0],
        caption=caption,
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

# ================= ADMIN VIDEO =================
def admin_video(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return

    if REKLAMA_MODE.get(update.effective_user.id):
        return

    if not update.message.video:
        return

    count = count_movies() + 1
    new_code = f"K{count:03d}"

    add_movie(new_code, update.message.video.file_id)

    update.message.reply_text(f"✅ Qo‘shildi: {new_code}")

# ================= DELETE =================
def delete(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        update.message.reply_text("❗ /delete K001")
        return

    code = context.args[0].upper()
    delete_movie(code)

    update.message.reply_text(f"🗑 O‘chirildi: {code}")

# ================= USERS =================
def users_count(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return

    users = load_json(USERS_FILE, {})
    update.message.reply_text(f"👥 Userlar: {len(users)}")

# ================= STAT =================
def stat(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return

    users = load_json(USERS_FILE, {})
    kino = count_movies()

    update.message.reply_text(f"📊 STAT\n👥 {len(users)}\n🎬 {kino}")

# ================= REKLAMA =================
def reklama(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return

    REKLAMA_MODE[update.effective_user.id] = True
    update.message.reply_text("📢 Reklama yubor")

def reklama_send(update: Update, context: CallbackContext):
    if not REKLAMA_MODE.get(update.effective_user.id):
        return

    users = load_json(USERS_FILE, {})
    ok, no = 0, 0

    for uid in users:
        try:
            uid = int(uid)

            if update.message.text:
                context.bot.send_message(uid, update.message.text)

            elif update.message.photo:
                context.bot.send_photo(uid, update.message.photo[-1].file_id)

            elif update.message.video:
                context.bot.send_video(uid, update.message.video.file_id)

            ok += 1
        except:
            no += 1

    update.message.reply_text(f"✅ {ok} | ❌ {no}")
    REKLAMA_MODE[update.effective_user.id] = False

# ================= MAIN =================
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stat", stat))
    dp.add_handler(CommandHandler("reklama", reklama))
    dp.add_handler(CommandHandler("delete", delete))
    dp.add_handler(CommandHandler("users", users_count))

    dp.add_handler(CallbackQueryHandler(check_sub, pattern="check_sub"))

    dp.add_handler(MessageHandler(filters.Regex(r"^K\d+"), kino_kod))
    dp.add_handler(MessageHandler(filters.VIDEO, admin_video))
    dp.add_handler(MessageHandler(
        filters.TEXT | filters.PHOTO | filters.VIDEO,
        reklama_send
    ))

    print("BOT ISHLADI")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
