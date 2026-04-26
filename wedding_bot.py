import asyncio
import json
import os
import logging
import re
from datetime import datetime, date
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import (
    Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIG ===
BOT_TOKEN = os.getenv("TOKEN")
ADMIN_ID = 7948989650

# === DATA FILES ===
USERS_FILE = "data/users.json"
ORDERS_FILE = "data/orders.json"
PACKAGES_FILE = "data/packages.json"

os.makedirs("data", exist_ok=True)

# === DEFAULT PACKAGES ===
DEFAULT_PACKAGES = {
    "1": {"name_uz": "1-Paket", "name_ru": "Пакет 1", "name_en": "Package 1",
          "desc_uz": "1 kun | 1 ta kamera", "desc_ru": "1 день | 1 камера", "desc_en": "1 day | 1 camera",
          "price": "700,000 so'm"},
    "2": {"name_uz": "2-Paket", "name_ru": "Пакет 2", "name_en": "Package 2",
          "desc_uz": "2 kun | 1 ta kamera", "desc_ru": "2 дня | 1 камера", "desc_en": "2 days | 1 camera",
          "price": "1,400,000 so'm"},
    "3": {"name_uz": "3-Paket", "name_ru": "Пакет 3", "name_en": "Package 3",
          "desc_uz": "2 kun | 1-kun 1 ta, 2-kun 2 ta kamera", "desc_ru": "2 дня | 1-й день 1 камера, 2-й день 2 камеры", "desc_en": "2 days | Day 1: 1 cam, Day 2: 2 cams",
          "price": "2,000,000 so'm"},
    "4": {"name_uz": "4-Paket (VIP)", "name_ru": "Пакет 4 (VIP)", "name_en": "Package 4 (VIP)",
          "desc_uz": "2 kun | 1-kun 1 ta, 2-kun 2 ta kamera + 1 ta kran kamera",
          "desc_ru": "2 дня | 1-й день 1 камера, 2-й день 2 камеры + кран-камера",
          "desc_en": "2 days | Day 1: 1 cam, Day 2: 2 cams + crane cam",
          "price": "300$"},
}

def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_users(): return load_json(USERS_FILE, {})
def save_users(u): save_json(USERS_FILE, u)
def get_orders(): return load_json(ORDERS_FILE, [])
def save_orders(o): save_json(ORDERS_FILE, o)
def get_packages(): return load_json(PACKAGES_FILE, DEFAULT_PACKAGES)
def save_packages(p): save_json(PACKAGES_FILE, p)

if not os.path.exists(PACKAGES_FILE):
    save_packages(DEFAULT_PACKAGES)

# === STATES ===
class UserStates(StatesGroup):
    waiting_phone = State()
    waiting_package = State()
    waiting_date = State()
    waiting_ceremony = State()
    waiting_location = State()
    confirm_order = State()
    waiting_message_to_admin = State()

class AdminStates(StatesGroup):
    edit_package_select = State()
    edit_package_field = State()
    broadcast_message = State()
    chat_select_user = State()
    chat_write = State()
    reply_to_user = State()

# === TEXTS ===
TEXTS = {
    "uz": {
        "welcome": "🎬 Sadaf Media Video Studiyasiga xush kelibsiz!\n\nMen sizga zakaz berish jarayonida yordam beraman.",
        "ask_phone": "📱 Davom etish uchun telefon raqamingizni yuboring:",
        "send_phone_btn": "📱 Telefon raqam yuborish",
        "contact_admin": "👨‍💼 Admin bilan aloqa",
        "choose_package": "📦 Paketni tanlang:",
        "choose_ceremony": "🎉 Marosim turini tanlang:",
        "ask_date": "📅 To'y sanasini kiriting (KK.OO.YYYY formatda):\nMasalan: 25.06.2025",
        "date_error": "❌ Sana noto'g'ri yoki o'tib ketgan. Iltimos, to'g'ri sana kiriting (masalan: 25.06.2026)",
        "ask_location": "📍 Manzilni matn ko'rinishida yozing yoki 📎 lokatsiya yuboring:",
        "confirm_title": "✅ Ma'lumotlarni tasdiqlaysizmi?",
        "send_yes": "✅ Ha, yuboraman",
        "send_no": "❌ Yo'q, yubormayman",
        "order_sent": "🎉 Zakazingiz qabul qilindi! Admin tez orada siz bilan bog'lanadi.",
        "msg_to_admin": "💬 Adminga xabar yozing:",
        "msg_sent": "✅ Xabaringiz adminga yuborildi!",
        "ceremonies": ["💍 Nikoh", "🥂 Banket", "🎊 Xatna", "👶 Chaqaloq", "🕌 Umra/Haj", "🎂 Tug'ilgan kun"],
        "lang_saved": "✅ Til saqlandi: O'zbek tili",
        "main_menu": "🏠 Asosiy menyu",
        "new_order": "📋 Yangi zakaz",
        "change_lang": "🌐 Tilni o'zgartirish",
    },
    "uzc": {
        "welcome": "🎬 Садаф Медиа Видео Студиясига хуш келибсиз!\n\nМен сизга заказ бериш жараёнида ёрдам бераман.",
        "ask_phone": "📱 Давом этиш учун телефон рақамингизни юборинг:",
        "send_phone_btn": "📱 Телефон рақам юбориш",
        "contact_admin": "👨‍💼 Админ билан алоқа",
        "choose_package": "📦 Пакетни танланг:",
        "choose_ceremony": "🎉 Маросим турини танланг:",
        "ask_date": "📅 Тўй санасини киритинг (КК.ОО.YYYY форматда):\nМасалан: 25.06.2025",
        "date_error": "❌ Сана нотўғри ёки ўтиб кетган. Тўғри сана киритинг (масалан: 25.06.2026)",
        "ask_location": "📍 Манзилни матн кўринишида ёзинг ёки 📎 локация юборинг:",
        "confirm_title": "✅ Маълумотларни тасдиқлайсизми?",
        "send_yes": "✅ Ха, юбораман",
        "send_no": "❌ Йўқ, юборманам",
        "order_sent": "🎉 Заказингиз қабул қилинди! Админ тез орада сиз билан боғланади.",
        "msg_to_admin": "💬 Админга хабар ёзинг:",
        "msg_sent": "✅ Хабарингиз админга юборилди!",
        "ceremonies": ["💍 Никоҳ", "🥂 Банкет", "🎊 Хатна", "👶 Чақалоқ", "🕌 Умра/Ҳаж", "🎂 Туғилган кун"],
        "lang_saved": "✅ Тил сақланди: Ўзбек тили (кирилл)",
        "main_menu": "🏠 Асосий меню",
        "new_order": "📋 Янги заказ",
        "change_lang": "🌐 Тилни ўзгартириш",
    },
    "ru": {
        "welcome": "🎬 Добро пожаловать в Sadaf Media Video Studio!\n\nЯ помогу вам оформить заказ.",
        "ask_phone": "📱 Отправьте ваш номер телефона для продолжения:",
        "send_phone_btn": "📱 Отправить номер телефона",
        "contact_admin": "👨‍💼 Связаться с администратором",
        "choose_package": "📦 Выберите пакет:",
        "choose_ceremony": "🎉 Выберите тип мероприятия:",
        "ask_date": "📅 Введите дату торжества (в формате ДД.ММ.ГГГГ):\nНапример: 25.06.2025",
        "date_error": "❌ Дата неверна или уже прошла. Введите правильную дату (например: 25.06.2026)",
        "ask_location": "📍 Напишите адрес текстом или отправьте 📎 геолокацию:",
        "confirm_title": "✅ Подтвердите отправку данных:",
        "send_yes": "✅ Да, отправить",
        "send_no": "❌ Нет, не отправлять",
        "order_sent": "🎉 Ваш заказ принят! Администратор свяжется с вами в ближайшее время.",
        "msg_to_admin": "💬 Напишите сообщение администратору:",
        "msg_sent": "✅ Ваше сообщение отправлено администратору!",
        "ceremonies": ["💍 Никах", "🥂 Банкет", "🎊 Обрезание", "👶 Новорождённый", "🕌 Умра/Хадж", "🎂 День рождения"],
        "lang_saved": "✅ Язык сохранён: Русский",
        "main_menu": "🏠 Главное меню",
        "new_order": "📋 Новый заказ",
        "change_lang": "🌐 Изменить язык",
    },
    "en": {
        "welcome": "🎬 Welcome to Sadaf Media Video Studio!\n\nI'll help you place an order.",
        "ask_phone": "📱 Please send your phone number to continue:",
        "send_phone_btn": "📱 Send Phone Number",
        "contact_admin": "👨‍💼 Contact Admin",
        "choose_package": "📦 Choose a package:",
        "choose_ceremony": "🎉 Select ceremony type:",
        "ask_date": "📅 Enter the event date (DD.MM.YYYY format):\nExample: 25.06.2025",
        "date_error": "❌ Invalid or past date. Please enter a valid date (e.g. 25.06.2026)",
        "ask_location": "📍 Type your address or send 📎 your location:",
        "confirm_title": "✅ Confirm your details:",
        "send_yes": "✅ Yes, submit",
        "send_no": "❌ No, cancel",
        "order_sent": "🎉 Your order has been received! Admin will contact you shortly.",
        "msg_to_admin": "💬 Write your message to admin:",
        "msg_sent": "✅ Your message has been sent to admin!",
        "ceremonies": ["💍 Wedding", "🥂 Banquet", "🎊 Circumcision", "👶 Baby", "🕌 Umrah/Hajj", "🎂 Birthday"],
        "lang_saved": "✅ Language saved: English",
        "main_menu": "🏠 Main Menu",
        "new_order": "📋 New Order",
        "change_lang": "🌐 Change Language",
    },
}

def t(lang, key):
    return TEXTS.get(lang, TEXTS["uz"]).get(key, key)

def get_user_lang(user_id):
    users = get_users()
    return users.get(str(user_id), {}).get("lang", None)

def set_user_lang(user_id, lang, name=None, username=None):
    users = get_users()
    uid = str(user_id)
    if uid not in users:
        users[uid] = {}
    users[uid]["lang"] = lang
    if name: users[uid]["name"] = name
    if username: users[uid]["username"] = username
    save_users(users)

def get_user_phone(user_id):
    return get_users().get(str(user_id), {}).get("phone", None)

def set_user_phone(user_id, phone):
    users = get_users()
    uid = str(user_id)
    if uid not in users:
        users[uid] = {}
    users[uid]["phone"] = phone
    save_users(users)

# === KEYBOARDS ===
def lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
         InlineKeyboardButton(text="🇺🇿 Ўзбек", callback_data="lang_uzc")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
         InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
    ])

def phone_keyboard(lang):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "send_phone_btn"), request_contact=True)],
            [KeyboardButton(text=t(lang, "contact_admin"))],
        ],
        resize_keyboard=True
    )

def main_menu_keyboard(lang):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "new_order"))],
            [KeyboardButton(text=t(lang, "contact_admin")), KeyboardButton(text=t(lang, "change_lang"))],
        ],
        resize_keyboard=True
    )

def packages_keyboard(lang):
    pkgs = get_packages()
    buttons = []
    for pid, pkg in pkgs.items():
        name = pkg.get(f"name_{lang}", pkg.get("name_uz", f"Paket {pid}"))
        desc = pkg.get(f"desc_{lang}", pkg.get("desc_uz", ""))
        price = pkg.get("price", "")
        buttons.append([InlineKeyboardButton(
            text=f"{name} | {price}\n{desc}",
            callback_data=f"pkg_{pid}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def ceremony_keyboard(lang):
    ceremonies = t(lang, "ceremonies")
    buttons = []
    row = []
    for i, c in enumerate(ceremonies):
        row.append(InlineKeyboardButton(text=c, callback_data=f"cer_{i}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def confirm_keyboard(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "send_yes"), callback_data="confirm_yes"),
         InlineKeyboardButton(text=t(lang, "send_no"), callback_data="confirm_no")],
    ])

# === ROUTER ===
router = Router()

# ==================== START ====================
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id

    if user_id == ADMIN_ID:
        await message.answer("👑 Admin paneliga xush kelibsiz!", reply_markup=admin_menu())
        return

    lang = get_user_lang(user_id)
    if lang:
        name = message.from_user.first_name or "Do'st"
        phone = get_user_phone(user_id)
        if phone:
            await message.answer(
                f"👋 Xush kelibsiz, {name}!\n\n" + t(lang, "welcome"),
                reply_markup=main_menu_keyboard(lang)
            )
        else:
            await message.answer(t(lang, "ask_phone"), reply_markup=phone_keyboard(lang))
            await state.set_state(UserStates.waiting_phone)
    else:
        await message.answer(
            "🌐 Tilni tanlang / Выберите язык / Choose language:",
            reply_markup=lang_keyboard()
        )

# ==================== LANGUAGE ====================
@router.callback_query(F.data.startswith("lang_"))
async def choose_lang(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_", 1)[1]
    user_id = callback.from_user.id
    name = callback.from_user.first_name or "Do'st"
    username = callback.from_user.username

    set_user_lang(user_id, lang, name, username)
    await callback.message.delete()

    phone = get_user_phone(user_id)
    if phone:
        await callback.message.answer(
            t(lang, "lang_saved") + f"\n\n👋 {name}!\n" + t(lang, "welcome"),
            reply_markup=main_menu_keyboard(lang)
        )
    else:
        await callback.message.answer(
            t(lang, "lang_saved") + f"\n\n👋 {name}!\n\n" + t(lang, "ask_phone"),
            reply_markup=phone_keyboard(lang)
        )
        await state.set_state(UserStates.waiting_phone)
    await callback.answer()

# ==================== PHONE ====================
@router.message(UserStates.waiting_phone, F.contact)
async def got_phone(message: Message, state: FSMContext):
    lang = get_user_lang(message.from_user.id)
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone
    set_user_phone(message.from_user.id, phone)
    await state.clear()
    name = message.from_user.first_name or "Do'st"
    await message.answer(
        f"✅ {phone}\n\n👋 {name}, " + t(lang, "welcome"),
        reply_markup=main_menu_keyboard(lang)
    )

@router.message(UserStates.waiting_phone)
async def phone_text_fallback(message: Message, state: FSMContext):
    lang = get_user_lang(message.from_user.id)
    await message.answer(t(lang, "ask_phone"), reply_markup=phone_keyboard(lang))

# ==================== MAIN MENU ====================
@router.message(F.text)
async def handle_text(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id == ADMIN_ID:
        await handle_admin_text(message, state)
        return

    lang = get_user_lang(user_id)
    if not lang:
        await message.answer("🌐 Tilni tanlang:", reply_markup=lang_keyboard())
        return

    txt = message.text

    if txt == t(lang, "new_order"):
        phone = get_user_phone(user_id)
        if not phone:
            await message.answer(t(lang, "ask_phone"), reply_markup=phone_keyboard(lang))
            await state.set_state(UserStates.waiting_phone)
            return
        await state.clear()
        await message.answer(t(lang, "choose_package"), reply_markup=packages_keyboard(lang))

    elif txt == t(lang, "contact_admin"):
        await message.answer(t(lang, "msg_to_admin"), reply_markup=ReplyKeyboardRemove())
        await state.set_state(UserStates.waiting_message_to_admin)

    elif txt == t(lang, "change_lang"):
        await message.answer("🌐 Tilni tanlang / Выберите язык / Choose language:", reply_markup=lang_keyboard())

    elif txt == t(lang, "send_phone_btn"):
        await message.answer(t(lang, "ask_phone"), reply_markup=phone_keyboard(lang))
        await state.set_state(UserStates.waiting_phone)

# ==================== ORDER FLOW ====================
@router.callback_query(F.data.startswith("pkg_"))
async def choose_package(callback: CallbackQuery, state: FSMContext):
    lang = get_user_lang(callback.from_user.id)
    pkg_id = callback.data.split("_")[1]
    pkgs = get_packages()
    pkg = pkgs.get(pkg_id, {})
    name = pkg.get(f"name_{lang}", pkg.get("name_uz", f"Paket {pkg_id}"))
    price = pkg.get("price", "")
    await state.update_data(package_id=pkg_id, package_name=name, package_price=price)
    await callback.message.edit_text(
        t(lang, "choose_ceremony"),
        reply_markup=ceremony_keyboard(lang)
    )
    await state.set_state(UserStates.waiting_ceremony)
    await callback.answer()

@router.callback_query(UserStates.waiting_ceremony, F.data.startswith("cer_"))
async def choose_ceremony(callback: CallbackQuery, state: FSMContext):
    lang = get_user_lang(callback.from_user.id)
    idx = int(callback.data.split("_")[1])
    ceremonies = t(lang, "ceremonies")
    ceremony = ceremonies[idx]
    await state.update_data(ceremony=ceremony)
    await callback.message.edit_text(t(lang, "ask_date"))
    await state.set_state(UserStates.waiting_date)
    await callback.answer()

# ==================== BUG FIX 1: SANA ====================
@router.message(UserStates.waiting_date)
async def got_date(message: Message, state: FSMContext):
    lang = get_user_lang(message.from_user.id)
    txt = message.text.strip()

    event_date = None

    # DD.MM.YYYY yoki D.M.YYYY — barcha platformalarda ishlaydigan regex usuli
    m = re.match(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})$", txt)
    if m:
        try:
            event_date = date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            pass

    # DD/MM/YYYY
    if event_date is None:
        try:
            event_date = datetime.strptime(txt, "%d/%m/%Y").date()
        except ValueError:
            pass

    # YYYY-MM-DD
    if event_date is None:
        try:
            event_date = datetime.strptime(txt, "%Y-%m-%d").date()
        except ValueError:
            pass

    if event_date is None:
        await message.answer(t(lang, "date_error"))
        return

    if event_date < date.today():
        await message.answer(t(lang, "date_error"))
        return

    # Sanani standart formatda saqlash
    formatted_date = event_date.strftime("%d.%m.%Y")
    await state.update_data(event_date=formatted_date)
    await message.answer(t(lang, "ask_location"), reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserStates.waiting_location)

# ==================== BUG FIX 2: LOCATION ====================
@router.message(UserStates.waiting_location, F.location)
async def got_location_geo(message: Message, state: FSMContext):
    """Foydalanuvchi GPS lokatsiya yuborganida"""
    lang = get_user_lang(message.from_user.id)
    lat = message.location.latitude
    lon = message.location.longitude
    await state.update_data(
        location_lat=lat,
        location_lon=lon,
        location_text=f"📍 {lat}, {lon}"
    )
    await show_confirm(message, state, lang)

@router.message(UserStates.waiting_location)
async def got_location_text(message: Message, state: FSMContext):
    """Foydalanuvchi manzilni matn ko'rinishida yozganida — show_confirm ga o'tadi"""
    lang = get_user_lang(message.from_user.id)
    await state.update_data(
        location_lat=None,
        location_lon=None,
        location_text=message.text
    )
    await show_confirm(message, state, lang)

# ==================== CONFIRM ====================
async def show_confirm(message: Message, state: FSMContext, lang: str):
    data = await state.get_data()
    users = get_users()
    uid = str(message.from_user.id)
    name = users.get(uid, {}).get("name", message.from_user.first_name or "?")
    phone = get_user_phone(message.from_user.id)

    text = (
        f"━━━━━━━━━━━━━━━━\n"
        f"👤 {name}\n"
        f"📱 {phone}\n"
        f"📦 {data.get('package_name')} — {data.get('package_price')}\n"
        f"🎉 {data.get('ceremony')}\n"
        f"📅 {data.get('event_date')}\n"
        f"📍 {data.get('location_text', '?')}\n"
        f"━━━━━━━━━━━━━━━━"
    )
    await message.answer(t(lang, "confirm_title") + "\n\n" + text, reply_markup=confirm_keyboard(lang))
    await state.set_state(UserStates.confirm_order)

@router.callback_query(UserStates.confirm_order, F.data == "confirm_yes")
async def confirm_yes(callback: CallbackQuery, state: FSMContext):
    lang = get_user_lang(callback.from_user.id)
    data = await state.get_data()
    users = get_users()
    uid = str(callback.from_user.id)
    name = users.get(uid, {}).get("name", callback.from_user.first_name or "?")
    phone = get_user_phone(callback.from_user.id)

    order = {
        "id": len(get_orders()) + 1,
        "user_id": callback.from_user.id,
        "name": name,
        "phone": phone,
        "package": f"{data.get('package_name')} — {data.get('package_price')}",
        "ceremony": data.get("ceremony"),
        "date": data.get("event_date"),
        "location": data.get("location_text"),
        "lat": data.get("location_lat"),
        "lon": data.get("location_lon"),
        "created_at": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "lang": lang,
    }

    orders = get_orders()
    orders.append(order)
    save_orders(orders)

    bot = callback.bot
    admin_text = (
        f"🆕 YANGI ZAKAZ #{order['id']}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"👤 Ism: {name}\n"
        f"📱 Tel: {phone}\n"
        f"🆔 User ID: {callback.from_user.id}\n"
        f"📦 Paket: {data.get('package_name')} — {data.get('package_price')}\n"
        f"🎉 Marosim: {data.get('ceremony')}\n"
        f"📅 Sana: {data.get('event_date')}\n"
        f"📍 Lokatsiya: {data.get('location_text')}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💬 /reply_{callback.from_user.id} — javob berish"
    )
    await bot.send_message(ADMIN_ID, admin_text)

    # GPS lokatsiya bo'lsa alohida yuborish
    if data.get("location_lat"):
        await bot.send_location(ADMIN_ID, latitude=data["location_lat"], longitude=data["location_lon"])

    await callback.message.edit_text(t(lang, "order_sent"))
    await state.clear()
    await callback.message.answer(t(lang, "main_menu"), reply_markup=main_menu_keyboard(lang))
    await callback.answer()

@router.callback_query(UserStates.confirm_order, F.data == "confirm_no")
async def confirm_no(callback: CallbackQuery, state: FSMContext):
    lang = get_user_lang(callback.from_user.id)
    await state.clear()
    await callback.message.edit_text("❌ Zakaz bekor qilindi.")
    await callback.message.answer(t(lang, "main_menu"), reply_markup=main_menu_keyboard(lang))
    await callback.answer()

# ==================== MSG TO ADMIN ====================
@router.message(UserStates.waiting_message_to_admin)
async def msg_to_admin(message: Message, state: FSMContext):
    lang = get_user_lang(message.from_user.id)
    users = get_users()
    uid = str(message.from_user.id)
    name = users.get(uid, {}).get("name", message.from_user.first_name or "?")
    phone = get_user_phone(message.from_user.id)

    await message.bot.send_message(
        ADMIN_ID,
        f"💬 XABAR\n"
        f"👤 {name} | 📱 {phone}\n"
        f"🆔 ID: {message.from_user.id}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"{message.text}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💬 /reply_{message.from_user.id}"
    )
    await message.answer(t(lang, "msg_sent"), reply_markup=main_menu_keyboard(lang))
    await state.clear()

# ==================== ADMIN REPLY ====================
@router.message(F.text.startswith("/reply_"))
async def admin_reply_command(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        target_id = int(message.text.split("_")[1])
        await state.update_data(reply_target=target_id)
        await state.set_state(AdminStates.reply_to_user)
        await message.answer(f"✏️ {target_id} ga javob yozing:")
    except Exception:
        await message.answer("❌ Xato format.")

@router.message(AdminStates.reply_to_user)
async def admin_send_reply(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    target_id = data.get("reply_target")
    try:
        await message.bot.send_message(target_id, f"👨‍💼 Admin:\n\n{message.text}")
        await message.answer("✅ Xabar yuborildi!")
    except Exception:
        await message.answer("❌ Xabar yuborib bo'lmadi.")
    await state.clear()
    await message.answer("Admin panel:", reply_markup=admin_menu())

# ==================== ADMIN PANEL ====================
def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Paket narxlari"), KeyboardButton(text="📋 Zakazlar")],
            [KeyboardButton(text="💬 Chat"), KeyboardButton(text="📢 Broadcast")],
        ],
        resize_keyboard=True
    )

async def handle_admin_text(message: Message, state: FSMContext):
    txt = message.text

    if txt == "📦 Paket narxlari":
        await show_packages_admin(message)
    elif txt == "📋 Zakazlar":
        await show_orders_admin(message)
    elif txt == "💬 Chat":
        await show_users_for_chat(message, state)
    elif txt == "📢 Broadcast":
        await message.answer("📢 Barcha foydalanuvchilarga yuboriladigan xabarni yozing:")
        await state.set_state(AdminStates.broadcast_message)

async def show_packages_admin(message: Message):
    pkgs = get_packages()
    text = "📦 Paketlar narxlari:\n\n"
    buttons = []
    for pid, pkg in pkgs.items():
        text += f"<b>{pkg.get('name_uz')}</b> — {pkg.get('price')}\n{pkg.get('desc_uz')}\n\n"
        buttons.append([InlineKeyboardButton(
            text=f"✏️ {pkg.get('name_uz')} tahrirlash",
            callback_data=f"editpkg_{pid}"
        )])
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("editpkg_"))
async def edit_package_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    pkg_id = callback.data.split("_")[1]
    await state.update_data(edit_pkg_id=pkg_id)
    pkgs = get_packages()
    pkg = pkgs.get(pkg_id, {})
    await callback.message.answer(
        f"📦 {pkg.get('name_uz')}\nHozirgi narx: {pkg.get('price')}\n\nYangi narxni kiriting:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_edit")]
        ])
    )
    await state.set_state(AdminStates.edit_package_field)
    await callback.answer()

@router.callback_query(F.data == "cancel_edit")
async def cancel_edit(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Bekor qilindi.")
    await callback.answer()

@router.message(AdminStates.edit_package_field)
async def edit_package_save(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    pkg_id = data.get("edit_pkg_id")
    pkgs = get_packages()
    if pkg_id in pkgs:
        pkgs[pkg_id]["price"] = message.text.strip()
        save_packages(pkgs)
        await message.answer(f"✅ {pkgs[pkg_id]['name_uz']} narxi yangilandi: {message.text.strip()}")
    else:
        await message.answer("❌ Paket topilmadi.")
    await state.clear()
    await message.answer("Admin panel:", reply_markup=admin_menu())

async def show_orders_admin(message: Message):
    orders = get_orders()
    if not orders:
        await message.answer("📋 Zakazlar yo'q.")
        return
    for order in orders[-20:]:
        text = (
            f"🆔 Zakaz #{order['id']} | {order['created_at']}\n"
            f"👤 {order['name']} | 📱 {order['phone']}\n"
            f"📦 {order['package']}\n"
            f"🎉 {order['ceremony']} | 📅 {order['date']}\n"
            f"📍 {order['location']}\n"
            f"💬 /reply_{order['user_id']}"
        )
        await message.answer(text)

async def show_users_for_chat(message: Message, state: FSMContext):
    users = get_users()
    if not users:
        await message.answer("👤 Foydalanuvchilar yo'q.")
        return
    buttons = []
    for uid, info in users.items():
        name = info.get("name", "Noma'lum")
        phone = info.get("phone", "?")
        buttons.append([InlineKeyboardButton(
            text=f"👤 {name} | {phone}",
            callback_data=f"chat_user_{uid}"
        )])
    await message.answer("👥 Foydalanuvchini tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await state.set_state(AdminStates.chat_select_user)

@router.callback_query(AdminStates.chat_select_user, F.data.startswith("chat_user_"))
async def chat_user_selected(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    uid = callback.data.split("_")[2]
    await state.update_data(chat_target=int(uid))
    await state.set_state(AdminStates.chat_write)
    await callback.message.answer(f"✏️ {uid} ga xabar yozing:")
    await callback.answer()

@router.message(AdminStates.chat_write)
async def admin_chat_send(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    target = data.get("chat_target")
    try:
        await message.bot.send_message(target, f"👨‍💼 Admin:\n\n{message.text}")
        await message.answer("✅ Xabar yuborildi!")
    except Exception:
        await message.answer("❌ Yuborib bo'lmadi.")
    await state.clear()
    await message.answer("Admin panel:", reply_markup=admin_menu())

@router.message(AdminStates.broadcast_message)
async def do_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    users = get_users()
    success = 0
    failed = 0
    for uid in users:
        try:
            await message.bot.send_message(int(uid), f"📢 Sadaf Media:\n\n{message.text}")
            success += 1
        except Exception:
            failed += 1
    await message.answer(f"📢 Broadcast tugadi!\n✅ Yuborildi: {success}\n❌ Yuborilmadi: {failed}")
    await state.clear()
    await message.answer("Admin panel:", reply_markup=admin_menu())

# ==================== MAIN ====================
async def main():
    from aiogram.client.default import DefaultBotProperties
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    logger.info("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
