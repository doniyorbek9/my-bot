#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, json, logging
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler,
    ContextTypes, filters
)

# ═════════ CONFIG ═════════
BOT_TOKEN   = os.getenv("TOKEN")
ADMIN_ID    = 7948989650

PRICES_FILE = "prices.json"
ORDERS_FILE = "orders.json"
USERS_FILE  = "users.json"

logging.basicConfig(level=logging.INFO)

# ═════════ STATES ═════════
S_LANG, S_CONTACT, S_ADMIN_MSG, S_PKG, S_DATE, S_EVENT, S_LOC, S_ADDR, S_ADMIN = range(9)

# ═════════ DEFAULT PRICES ═════════
DEFAULT_PRICES = {
    "p1": {"label": "1️⃣ 700 000 so'm", "desc": "1 kamera"},
    "p2": {"label": "2️⃣ 1 400 000 so'm", "desc": "2 kun"},
    "p3": {"label": "3️⃣ 2 000 000 so'm", "desc": "2 kamera"},
    "p4": {"label": "4️⃣ VIP 300$", "desc": "Kran + premium"},
}

# ═════════ JSON HELPERS ═════════
def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    if file == PRICES_FILE:
        save_json(file, DEFAULT_PRICES)
        return DEFAULT_PRICES
    return []

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ═════════ START ═════════
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(
            "👨‍💼 ADMIN PANEL",
            reply_markup=ReplyKeyboardMarkup([
                ["📋 Zakazlar", "✏️ Narxlar"]
            ], resize_keyboard=True)
        )
        return S_ADMIN

    await update.message.reply_text(
        "📱 Telefon raqamingizni yuboring:",
        reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("📞 Yuborish", request_contact=True)]
        ], resize_keyboard=True)
    )
    return S_CONTACT

# ═════════ CONTACT ═════════
async def got_contact(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    prices = load_json(PRICES_FILE)

    btns = []
    for k, p in prices.items():
        btns.append([
            InlineKeyboardButton(
                f"{p.get('label','Paket')}\n📹 {p.get('desc','')}",
                callback_data=f"PK:{k}"
            )
        ])

    await update.message.reply_text(
        "📦 Paket tanlang:",
        reply_markup=InlineKeyboardMarkup(btns)
    )
    return S_PKG

# ═════════ PACKAGE ═════════
async def pkg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    key = q.data.split(":")[1]
    prices = load_json(PRICES_FILE)

    p = prices.get(key, {"label":"Paket", "desc":""})

    ctx.user_data["package"] = p["label"]

    await q.message.reply_text(
        f"✅ Tanlandi: {p['label']}\n📅 Sana yozing:"
    )
    return S_DATE

# ═════════ DATE ═════════
async def date(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["date"] = update.message.text
    await update.message.reply_text("🎊 Tadbir turi:")
    return S_EVENT

# ═════════ EVENT ═════════
async def event(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["event"] = update.message.text
    await update.message.reply_text(
        "📍 Lokatsiya yuboring:",
        reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("📍 Send location", request_location=True)]
        ], resize_keyboard=True)
    )
    return S_LOC

# ═════════ LOCATION ═════════
async def loc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["lat"] = update.message.location.latitude
    ctx.user_data["lon"] = update.message.location.longitude

    await update.message.reply_text("🏠 Manzil yozing:")
    return S_ADDR

# ═════════ ADDRESS + SAVE ORDER ═════════
async def addr(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    d = ctx.user_data

    order = {
        "name": update.effective_user.full_name,
        "package": d.get("package"),
        "date": d.get("date"),
        "event": d.get("event"),
        "address": update.message.text,
        "lat": d.get("lat"),
        "lon": d.get("lon"),
    }

    orders = load_json(ORDERS_FILE)
    orders.append(order)
    save_json(ORDERS_FILE, orders)

    await update.message.reply_text("✅ Zakaz qabul qilindi!")
    return ConversationHandler.END

# ═════════ ADMIN ═════════
async def admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "📋 Zakazlar":
        orders = load_json(ORDERS_FILE)

        for i, o in enumerate(orders):
            await update.message.reply_text(
                f"#{i+1}\n{o['name']}\n{o['package']}\n{o['date']}\n{o['event']}"
            )

    return S_ADMIN

# ═════════ ERROR HANDLER ═════════
async def error(update: object, ctx: ContextTypes.DEFAULT_TYPE):
    logging.error("ERROR: %s", ctx.error)

# ═════════ MAIN ═════════
def main():
    if not BOT_TOKEN:
        print("TOKEN yo‘q!")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            S_CONTACT: [MessageHandler(filters.CONTACT, got_contact)],
            S_PKG: [CallbackQueryHandler(pkg, pattern="^PK:")],
            S_DATE: [MessageHandler(filters.TEXT, date)],
            S_EVENT: [MessageHandler(filters.TEXT, event)],
            S_LOC: [MessageHandler(filters.LOCATION, loc)],
            S_ADDR: [MessageHandler(filters.TEXT, addr)],
            S_ADMIN: [MessageHandler(filters.TEXT, admin)],
        },
        fallbacks=[],
        per_message=True   # 🔥 FIX CALLBACK BUG
    )

    app.add_handler(conv)
    app.add_error_handler(error)

    print("BOT RUNNING...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
