#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)

# ===== CONFIG =====
TOKEN = os.getenv("TOKEN")
ADMIN_ID = 7948989650

if not TOKEN:
    raise Exception("TOKEN topilmadi!")

# ===== FILES =====
USERS_FILE = "users.json"
ORDERS_FILE = "orders.json"
PRICES_FILE = "prices.json"

def load(file, default):
    if not os.path.exists(file):
        return default
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

users = load(USERS_FILE, {})
orders = load(ORDERS_FILE, [])
prices = load(PRICES_FILE, {
    "1": "700000 so'm",
    "2": "1 400 000 so'm",
    "3": "2 000 000 so'm",
    "4": "300$"
})

# ===== STATES =====
LANG, PHONE, PACKAGE, DATE, EVENT, LOCATION, CONFIRM = range(7)

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        ["O'zbek", "Uzbek (RU)"],
        ["English", "Русский"]
    ]
    await update.message.reply_text(
        "Tilni tanlang:",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )
    return LANG

# ===== LANGUAGE =====
async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)

    users[uid] = {
        "name": update.effective_user.first_name,
        "lang": update.message.text
    }
    save(USERS_FILE, users)

    btn = [[KeyboardButton("📞 Raqam yuborish", request_contact=True)]]

    await update.message.reply_text(
        f"Salom {update.effective_user.first_name}\nRaqamingizni yuboring:",
        reply_markup=ReplyKeyboardMarkup(btn, resize_keyboard=True)
    )
    return PHONE

# ===== PHONE (FULL FIX) =====
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact

    if not contact:
        await update.message.reply_text("❌ Tugma orqali raqam yuboring")
        return PHONE

    if contact.user_id != update.effective_user.id:
        await update.message.reply_text("❌ Faqat o'zingizni raqamingizni yuboring")
        return PHONE

    phone = contact.phone_number
    context.user_data["phone"] = phone

    kb = [["1-Paket","2-Paket"],["3-Paket","4-Paket"]]

    text = (
        f"1️⃣ 1 kun 1 kamera - {prices['1']}\n"
        f"2️⃣ 2 kun 1 kamera - {prices['2']}\n"
        f"3️⃣ 2 kun (1+2 kamera) - {prices['3']}\n"
        f"4️⃣ VIP - {prices['4']}\n\n"
        "Paket tanlang:"
    )

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )
    return PACKAGE

# ===== PACKAGE =====
async def choose_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["package"] = update.message.text
    await update.message.reply_text(
        "To‘y sanasi (YYYY-MM-DD):",
        reply_markup=ReplyKeyboardRemove()
    )
    return DATE

# ===== DATE =====
async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        d = datetime.strptime(update.message.text, "%Y-%m-%d")
        if d.date() < datetime.now().date():
            await update.message.reply_text("❌ Eski sana mumkin emas")
            return DATE
    except:
        await update.message.reply_text("❌ Format xato (YYYY-MM-DD)")
        return DATE

    context.user_data["date"] = update.message.text

    kb = [["Nikoh","Banket"],["Xatna","Chaqaloq"],["Umra","Tug'ilgan kun"]]

    await update.message.reply_text(
        "Marosim turini tanlang:",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )
    return EVENT

# ===== EVENT =====
async def get_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["event"] = update.message.text

    await update.message.reply_text(
        "📍 Lokatsiya yuboring:",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("Lokatsiya", request_location=True)]],
            resize_keyboard=True
        )
    )
    return LOCATION

# ===== LOCATION =====
async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.location:
        await update.message.reply_text("❌ Tugma orqali lokatsiya yuboring")
        return LOCATION

    loc = update.message.location
    context.user_data["location"] = (loc.latitude, loc.longitude)

    kb = [["Ha"],["Yo‘q"]]
    await update.message.reply_text(
        "Tasdiqlaysizmi?",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )
    return CONFIRM

# ===== CONFIRM =====
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() != "ha":
        await update.message.reply_text("Bekor qilindi")
        return ConversationHandler.END

    user = update.effective_user
    data = context.user_data

    order = {
        "id": user.id,
        "name": user.first_name,
        "phone": data["phone"],
        "package": data["package"],
        "date": data["date"],
        "event": data["event"],
        "location": data["location"]
    }

    orders.append(order)
    save(ORDERS_FILE, orders)

    lat, lon = data["location"]

    await context.bot.send_message(
        ADMIN_ID,
        f"📥 Yangi zakaz!\n\n"
        f"👤 {order['name']}\n"
        f"📞 {order['phone']}\n"
        f"📦 {order['package']}\n"
        f"📅 {order['date']}\n"
        f"🎉 {order['event']}\n"
        f"🆔 {order['id']}"
    )

    await context.bot.send_location(ADMIN_ID, lat, lon)

    await update.message.reply_text("✅ Zakaz yuborildi!")
    return ConversationHandler.END

# ===== ADMIN =====
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    kb = [["📦 Zakazlar"],["📢 Broadcast"]]
    await update.message.reply_text(
        "Admin panel",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )

# ===== ORDERS =====
async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not orders:
        await update.message.reply_text("Zakaz yo‘q")
        return

    for o in orders:
        text = (
            f"👤 {o['name']}\n"
            f"📞 {o['phone']}\n"
            f"📦 {o['package']}\n"
            f"📅 {o['date']}\n"
            f"🎉 {o['event']}\n"
            f"🆔 {o['id']}"
        )
        await update.message.reply_text(text)

# ===== BROADCAST =====
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    context.user_data["broadcast"] = True
    await update.message.reply_text("Xabar yuboring:")

async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("broadcast"):
        return

    for uid in users:
        try:
            await context.bot.send_message(uid, update.message.text)
        except:
            pass

    context.user_data["broadcast"] = False
    await update.message.reply_text("✅ Yuborildi")

# ===== MAIN =====
def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG: [MessageHandler(filters.TEXT, set_lang)],
            PHONE: [MessageHandler(filters.ALL, get_phone)],
            PACKAGE: [MessageHandler(filters.TEXT, choose_package)],
            DATE: [MessageHandler(filters.TEXT, get_date)],
            EVENT: [MessageHandler(filters.TEXT, get_event)],
            LOCATION: [MessageHandler(filters.ALL, get_location)],
            CONFIRM: [MessageHandler(filters.TEXT, confirm)],
        },
        fallbacks=[]
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(MessageHandler(filters.Regex("Zakazlar"), show_orders))
    app.add_handler(MessageHandler(filters.Regex("Broadcast"), broadcast))
    app.add_handler(MessageHandler(filters.TEXT, send_broadcast))

    app.run_polling()

if __name__ == "__main__":
    main()
