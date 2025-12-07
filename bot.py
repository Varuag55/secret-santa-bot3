#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging
import random

# =======================
# 🛠 Налаштування логів
# =======================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# =======================
# 👤 Користувацькі дані
# =======================
participants = {}  # {user_id: {"name": str, "telegram": str}}
admin_id = 123456789  # Вкажи свій Telegram ID тут

# =======================
# 🎨 Кнопки для користувача
# =======================
user_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎁 Хочу знати КОМУ я дарую")],
        [KeyboardButton(text="📜 Правила (простими словами)")],
        [KeyboardButton(text="☎️ Зв’язатися з Організатором")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# =======================
# 🎨 Кнопки для адміністратора
# =======================
admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👀 Хто вже зареєстрований")],
        [KeyboardButton(text="🎰 Запустити КОСМІЧНУ рулетку")],
        [KeyboardButton(text="➕ Додати людину без Telegram")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# =======================
# 🚀 Команди
# =======================
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id == admin_id:
        update.message.reply_text(
            "Привіт, космічний адмін! 👽 Ось твоє меню:",
            reply_markup=admin_keyboard
        )
    else:
        update.message.reply_text(
            "Привіт! 🌟 Ласкаво просимо до анонімного обміну подарунками! 🎁",
            reply_markup=user_keyboard
        )

def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    text = update.message.text

    # =======================
    # Адмін: хто зареєстрований
    # =======================
    if user_id == admin_id:
        if text == "👀 Хто вже зареєстрований":
            if participants:
                msg = "Зареєстровані учасники:\n"
                for p in participants.values():
                    msg += f"- {p['name']} ({p['telegram']})\n"
                update.message.reply_text(msg)
            else:
                update.message.reply_text("Ніхто ще не зареєстрований 😢")
        elif text == "🎰 Запустити КОСМІЧНУ рулетку":
            if len(participants) < 2:
                update.message.reply_text("Потрібно мінімум 2 учасники для рулетки 🪐")
                return
            users = list(participants.keys())
            random.shuffle(users)
            mapping = {}
            for i in range(len(users)):
                giver = users[i]
                receiver = users[(i + 1) % len(users)]
                mapping[giver] = receiver
            msg = "🪐 Рулетка запущена! Всі учасники отримали свій таємний подарунок.\n"
            update.message.reply_text(msg)
            # надсилаємо кожному їхню пару
            for giver_id, receiver_id in mapping.items():
                context.bot.send_message(
                    chat_id=giver_id,
                    text=f"🎁 Твій отримувач: {participants[receiver_id]['name']}"
                )
        elif text == "➕ Додати людину без Telegram":
            update.message.reply_text("Напиши ім'я та контакт (наприклад, Vika, +380123456789)")
    else:
        # =======================
        # Користувачі
        # =======================
        if text == "🎁 Хочу знати КОМУ я дарую":
            update.message.reply_text("Твоє таємне призначення з'явиться після запуску рулетки 🪐")
        elif text == "📜 Правила (простими словами)":
            update.message.reply_text(
                "Прості правила:\n"
                "1. Підтверджуй свою участь\n"
                "2. Підготуй подарунок\n"
                "3. Після запуску рулетки дізнаєшся, кому даруєш 🎁"
            )
        elif text == "☎️ Зв’язатися з Організатором":
            update.message.reply_text("Напиши організатору: @YourTelegramName")
        else:
            # зберігаємо учасника
            if user_id not in participants:
                participants[user_id] = {
                    "name": update.effective_user.first_name,
                    "telegram": update.effective_user.username or "немає"
                }
                update.message.reply_text("Ти зареєстрований! 🌟", reply_markup=user_keyboard)
            else:
                update.message.reply_text("👍")

# =======================
# 🏁 Головна функція
# =======================
def main():
    TOKEN = "8450052650:AAF-40XOduhQ6HVIC-b2l8-SZp0CzH7G6Ko"  # <- Встав свій токен
    updater = Updater(TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
