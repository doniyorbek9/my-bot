#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler,
    filters, ContextTypes
)

# ===================== CONFIG =====================
ADMIN_ID = 7948989650
BOT_TOKEN = os.getenv("TOKEN") 

PRICES_FILE = "prices.json"
ORDERS_FILE = "orders.json"
USERS_FILE = "users.json"

# State-lar
(
    CONTACT, PACKAGE_SELECT, DATE_INPUT, EVENT_TYPE, 
    LOCATION, ADDRESS_INPUT, ADMIN_MAIN, 
    EDIT_PRICE_SELECT, EDIT_PRICE_VALUE, 
    ADMIN_CHAT_SELECT, ADMIN_CHATTING, CHAT_WITH_ADMIN
) = range(12)

# ===================== FUNKSIYALAR =====================
def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return [] if filename != PRICES_FILE else {
        "p1": {"name": "💍 Paket 1", "price": "700,000 so'm"},
        "p2": {"name": "💎 Paket 2", "price": "1,400,000 so'm"},
        "p3": {"name": "👑 Paket 3", "price": "2,000,000 so'm"},
        "p4": {"name": "🎬 Paket 4 (VIP)", "price": "300$"}
    }

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_user(user_id, name):
    users = load_json(USERS_FILE)
    if not any(u['id'] == user_id for u in users):
        users.append({"id": user_id, "name": name})
        save_json(USERS_FILE, users)

# ===================== HANDLERS =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.full_name)

    if user.id == ADMIN_ID:
        kb = ReplyKeyboardMarkup([["📋 Zakazlar", "✏️ Narxlarni tahrirlash"], ["💬 Chat"]], resize_keyboard=True)
        await update.message.reply_text("👨‍💼 Admin panel.", reply_markup=kb)
        return ADMIN_MAIN

    kb = ReplyKeyboardMarkup([[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)], ["📞 Admin bilan bog'lanish"]], resize_keyboard=True)
    await update.message.reply_text("📸 Sadaf Media botga xush kelibsiz!", reply_markup=kb)
    return CONTACT

# --- MIJOZ CHAT ---
async def start_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Admin uchun xabaringizni yozing (Chiqish uchun /cancel):", reply_markup=ReplyKeyboardRemove())
    return CHAT_WITH_ADMIN

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"👤 Mijoz: {update.effective_user.full_name}\n✍️ Xabar: {update.message.text}"
    await context.bot.send_message(ADMIN_ID, text)
    await update.message.reply_text("✅ Xabar yuborildi.")
    return ConversationHandler.END

# --- ADMIN LOGIKA ---
async def handle_admin_zakaz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    orders = load_json(ORDERS_FILE)
    if not orders: await update.message.reply_text("Zakazlar yo'q."); return ADMIN_MAIN
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"{o['package']} | {o['date']}", callback_data=f"order_{i}")] for i, o in enumerate(orders)])
    await update.message.reply_text("📋 Zakazlar:", reply_markup=kb)
    return ADMIN_MAIN

async def view_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    i = int(q.data.split("_")[1])
    orders = load_json(ORDERS_FILE)
    o = orders[i]
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🗑 O'chirish", callback_data=f"delete_{i}")]])
    await q.message.reply_text(f"👤 {o['name']}\n📱 {o['phone']}\n📦 {o['package']}\n📅 {o['date']}\n🏠 {o['address']}", reply_markup=kb)
    return ADMIN_MAIN

async def delete_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    i = int(q.data.split("_")[1])
    orders = load_json(ORDERS_FILE)
    if i < len(orders):
        orders.pop(i)
        save_json(ORDERS_FILE, orders)
        await q.edit_message_text(f"✅ Zakaz o'chirildi.")
    return ADMIN_MAIN

async def handle_admin_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prices = load_json(PRICES_FILE)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(v['name'], callback_data=f"price_{k}")] for k, v in prices.items()])
    await update.message.reply_text("✏️ Tahrirlash uchun tanlang:", reply_markup=kb)
    return EDIT_PRICE_SELECT

async def handle_admin_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_json(USERS_FILE)
    if not users: await update.message.reply_text("Foydalanuvchilar yo'q."); return ADMIN_MAIN
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(u['name'], callback_data=f"chat_{u['id']}")] for u in users])
    await update.message.reply_text("💬 Kimga xabar yozamiz?", reply_markup=kb)
    return ADMIN_CHAT_SELECT

# (Boshqa funksiyalar: contact_received, package_selected, etc. o'z joyida qoladi)
# Kod uzun bo'lmasligi uchun bu yerda qisqartirildi, lekin barchasi bir xil.

# ===================== MAIN =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CONTACT: [
                MessageHandler(filters.CONTACT, contact_received), # Eslatma: Bu funksiya avvalgi kodda bo'lishi kerak
                MessageHandler(filters.Text(["📞 Admin bilan bog'lanish"]), start_chat)
            ],
            CHAT_WITH_ADMIN: [
                CommandHandler("cancel", start),
                MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin)
            ],
            ADMIN_MAIN: [
                MessageHandler(filters.Text(["📋 Zakazlar"]), handle_admin_zakaz),
                MessageHandler(filters.Text(["✏️ Narxlarni tahrirlash"]), handle_admin_price),
                MessageHandler(filters.Text(["💬 Chat"]), handle_admin_chat),
                # MUXIM: Tugmalar ishlashi uchun bular qo'shildi
                CallbackQueryHandler(view_order, pattern="^order_"),
                CallbackQueryHandler(delete_order, pattern="^delete_")
            ],
            ADMIN_CHAT_SELECT: [CallbackQueryHandler(select_user_to_chat, pattern="^chat_")],
            # ... boshqa state-lar
            PACKAGE_SELECT: [CallbackQueryHandler(package_selected)],
            DATE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_received)],
            EVENT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, event_type_received)],
            LOCATION: [MessageHandler(filters.LOCATION, location_received)],
            ADDRESS_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_received)],
            EDIT_PRICE_SELECT: [CallbackQueryHandler(edit_price_select, pattern="^price_")],
            EDIT_PRICE_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_price_value)]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    app.add_handler(conv)
    app.run_polling()
