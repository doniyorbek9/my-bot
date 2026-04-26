import json
import os
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)

# ===== CONFIG =====
TOKEN = os.getenv("TOKEN") # Tokeningizni shu yerga yoki muhit o'zgaruvchisiga joylang
ADMIN_ID = 7948989650 

# ===== FAYLLAR =====
USERS_FILE = "users.json"
ORDERS_FILE = "orders.json"

def load(file, default):
    if not os.path.exists(file): return default
    with open(file, "r", encoding="utf-8") as f: return json.load(f)

def save(file, data):
    with open(file, "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)

users = load(USERS_FILE, {})
orders = load(ORDERS_FILE, [])

# ===== STATES =====
LANG, PHONE, PACKAGE, DATE, EVENT, LOCATION, CONFIRM, BROADCAST_STATE = range(8)

# ===== FUNKSIYALAR =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [["O'zbek", "English"], ["Русский"]]
    await update.message.reply_text("Tilni tanlang:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
    return LANG

async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    users[uid] = {"name": update.effective_user.first_name, "lang": update.message.text}
    save(USERS_FILE, users)
    btn = [[KeyboardButton("📞 Raqam yuborish", request_contact=True)]]
    await update.message.reply_text("Raqamingizni yuboring:", reply_markup=ReplyKeyboardMarkup(btn, resize_keyboard=True))
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.contact:
        await update.message.reply_text("❌ Iltimos, tugma orqali raqamingizni yuboring.")
        return PHONE
    context.user_data["phone"] = update.message.contact.phone_number
    kb = [["1-Paket", "2-Paket"], ["3-Paket", "4-Paket"]]
    await update.message.reply_text("Paketni tanlang:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
    return PACKAGE

async def choose_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["package"] = update.message.text
    await update.message.reply_text("To‘y sanasini kiriting (YYYY-MM-DD):", reply_markup=ReplyKeyboardRemove())
    return DATE

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        datetime.strptime(update.message.text, "%Y-%m-%d")
        context.user_data["date"] = update.message.text
        kb = [["Nikoh", "Banket"], ["Xatna", "Tug'ilgan kun"]]
        await update.message.reply_text("Marosim turini tanlang:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        return EVENT
    except:
        await update.message.reply_text("❌ Xato format. Iltimos, YYYY-MM-DD ko'rinishida yozing.")
        return DATE

async def get_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["event"] = update.message.text
    kb = [[KeyboardButton("📍 Lokatsiya yuborish", request_location=True)]]
    await update.message.reply_text("Lokatsiyangizni yuboring:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
    return LOCATION

async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.location:
        await update.message.reply_text("❌ Iltimos, lokatsiyani tugma orqali yuboring.")
        return LOCATION
    context.user_data["location"] = (update.message.location.latitude, update.message.location.longitude)
    await update.message.reply_text("Ma'lumotlar to'g'rimi? (Ha/Yo'q)", reply_markup=ReplyKeyboardMarkup([["Ha"], ["Yo'q"]], resize_keyboard=True))
    return CONFIRM

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != "Ha":
        await update.message.reply_text("Bekor qilindi.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    # Buyurtmani saqlash
    order = {**context.user_data, "user_id": update.effective_user.id, "name": update.effective_user.first_name}
    orders.append(order)
    save(ORDERS_FILE, orders)
    
    await context.bot.send_message(ADMIN_ID, f"Yangi buyurtma!\n👤 {order['name']}\n📞 {order['phone']}\n📦 {order['package']}\n📅 {order['date']}")
    await context.bot.send_location(ADMIN_ID, *order["location"])
    
    await update.message.reply_text("✅ Buyurtma qabul qilindi!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Jarayon bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# ===== ADMIN =====
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text("Admin panel. Buyruqlar: /broadcast, /orders")

async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    for o in orders:
        await update.message.reply_text(f"👤 {o['name']}: {o['package']} - {o['date']}")

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text("Tarqatiladigan xabarni yuboring:")
    return BROADCAST_STATE

async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for uid in users:
        try: await context.bot.send_message(uid, update.message.text)
        except: pass
    await update.message.reply_text("✅ Xabar barchaga yuborildi.")
    return ConversationHandler.END

# ===== MAIN =====
def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_lang)],
            PHONE: [MessageHandler(filters.CONTACT, get_phone)],
            PACKAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_package)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_date)],
            EVENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_event)],
            LOCATION: [MessageHandler(filters.LOCATION, get_location)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    broadcast_conv = ConversationHandler(
        entry_points=[CommandHandler("broadcast", broadcast_start)],
        states={BROADCAST_STATE: [MessageHandler(filters.TEXT, send_broadcast)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv)
    app.add_handler(broadcast_conv)
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("orders", show_orders))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
