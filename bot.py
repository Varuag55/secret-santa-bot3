import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
import random

# ---------------------------
# НАЛАШТУВАННЯ
# ---------------------------
ORGANIZER_ID = @Varyag_Drift  # <<< ВСТАВ СЮДИ СВІЙ TELEGRAM ID !!! 

FUNNY_NAMES = [
     "МаксімУм", "СвєтОфор", "ЛізАрдія", "КрісТаЛіна", "ОлЕГОСКОП",
    "МіЛаванда", "КатЮпітер", "СофиТрон", "ДіАнтиквар", "ЛєнОрион",
    "ЛеонідОС", "НаталІнка", "АняМальна", "ЖєкаМотор", "ЛіЛюкс", "АльБінГалактика"
]

registered_users = {}      # user_id → funny_name
matched_pairs = {}         # funny_name → funny_name
already_drawn = False      # щоб не запускали рулетку 20 разів

logging.basicConfig(level=logging.INFO)


# ---------------------------
# START
# ---------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"choose_{name}")]
        for name in FUNNY_NAMES
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "✨ *Ласкаво просимо до Космічного Секретного Санти!* ✨\n\n"
        "Сьогодні Всесвіт вирішив, що саме ти обраний для участі "
        "у священному розподілі подарунків родини, яка п’є Jagermeister, "
        "грає в мафію і шукає сенс життя десь між Bitcoin і фільмом *Interstellar*.\n\n"
        "Оберіть себе зі списку смішних імен нижче 👇",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


# ---------------------------
# ВИБІР ІМЕНІ
# ---------------------------
async def choose_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global already_drawn

    query = update.callback_query
    await query.answer()

    name = query.data.replace("choose_", "")
    user_id = query.from_user.id

    # Записуємо вибір
    registered_users[user_id] = name

    await query.edit_message_text(
        f"🚀 *Вітаю, {name}!* Твоє космічне ім'я збережено!\n\n"
        "Тепер чекаємо на інших учасників з нашої родини "
        "галактики Чумацького Шляху… 🌌",
        parse_mode="Markdown"
    )

    # Якщо всі вибралися — повідомити організатора
    if len(registered_users) == len(FUNNY_NAMES):
        await context.bot.send_message(
            ORGANIZER_ID,
            "🛎 *Всі учасники зареєструвалися!*\n\n"
            "Настав момент, коли доля, випадковість і Jagermeister "
            "зливаються в одному акті — *натисни /draw щоб запустити рулетку!*",
            parse_mode="Markdown"
        )


# ---------------------------
# РУЛЕТКА
# ---------------------------
async def draw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global already_drawn, matched_pairs

    if update.effective_user.id != ORGANIZER_ID:
        await update.message.reply_text("🚫 Тільки Верховний Організатор може запускати рулетку.")
        return

    if len(registered_users) < len(FUNNY_NAMES):
        await update.message.reply_text("⏳ Ще не всі вибрали свої смішні імена!")
        return

    # Стартуємо нову рулетку
    already_drawn = True
    matched_pairs = {}

    names = list(registered_users.values())
    shuffled = names.copy()

    # Гарантовано різні отримувачі
    while True:
        random.shuffle(shuffled)
        if all(a != b for a, b in zip(names, shuffled)):
            break

    # Формуємо пари
    for giver, receiver in zip(names, shuffled):
        matched_pairs[giver] = receiver

    # Розсилка всім
    for uid, funny_name in registered_users.items():
        await context.bot.send_message(
            uid,
            f"🎁 *Космічна Рулетка подарунків завершена!*\n\n"
            f"Ти, *{funny_name}*, даруєш подарунок герою:\n\n"
            f"✨ **{matched_pairs[funny_name]}** ✨\n\n"
            "Пам’ятай: Всесвіт стежить за тобою 👁",
            parse_mode="Markdown"
        )

    await update.message.reply_text("🌠 Розподіл успішно завершено! Всесвіт аплодує стоячи.")


# ---------------------------
# RESET
# ---------------------------
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global registered_users, matched_pairs, already_drawn
    if update.effective_user.id != ORGANIZER_ID:
        await update.message.reply_text("Тільки Бог Розподілу (ти) може робити reset.")
        return

    registered_users = {}
    matched_pairs = {}
    already_drawn = False

    await update.message.reply_text(
        "🔄 *Космічний цикл перезапущено!*\n\n"
        "Учасники можуть почати реєстрацію заново.\n"
        "Bitcoin зросте. Сенс життя знайдеться. Все буде добре.",
        parse_mode="Markdown"
    )


# ---------------------------
# MAIN
# ---------------------------
def main():
    app = ApplicationBuilder().token("8450052650:AAF-40XOduhQ6HVIC-b2l8-SZp0CzH7G6Ko").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("draw", draw))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CallbackQueryHandler(choose_name))

    app.run_polling()


if __name__ == "__main__":
    main()
