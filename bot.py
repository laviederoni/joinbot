import os
import json
import threading
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

# --- 🔒 VARIABLES D'ENVIRONNEMENT ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# --- 🌐 Flask pour garder le bot en ligne ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot LEAK2TECH actif 🚀"

def run_web():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

# --- 📁 Gestion des fichiers JSON persistants ---
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": [], "referrals": {}, "balances": {}}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# --- 🧠 Fonctions utilitaires ---
def get_user_count():
    return len(data["users"])

# --- 🔹 Commande /start ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.full_name

    if user_id not in data["users"]:
        data["users"].append(user_id)
        save_data()

    # Gestion du parrainage
    referrer_id = None
    if message.get_args():
        try:
            referrer_id = int(message.get_args())
        except ValueError:
            pass

    if referrer_id and referrer_id != user_id:
        data["referrals"][str(user_id)] = referrer_id
        data["balances"][str(referrer_id)] = data["balances"].get(str(referrer_id), 0) + 1
        save_data()

        # 🔔 Notifier le parrain
        try:
            await bot.send_message(
                referrer_id,
                f"💸 Une personne a rejoint grâce à ton lien !\n"
                f"1€ ajouté à ton solde.\n\n"
                f"👥 Parrainages : {list(data['referrals'].values()).count(referrer_id)}\n"
                f"💰 Solde : {data['balances'].get(str(referrer_id), 0)}€"
            )
        except Exception as e:
            print(f"Erreur notif parrain : {e}")

    # Message d'accueil
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📲 Rejoindre le canal", url="https://t.me/+9O6qGVz4OOM1NTZk")],
        [InlineKeyboardButton(text="🤝 Parrainage", callback_data="referral")]
    ])

    await message.answer(
        f"Bienvenue sur LEAK2️⃣TECH📂, {username} !\n\n"
        f"Rejoins le canal ci-dessous 👇",
        reply_markup=keyboard
    )

# --- 🔹 Menu Parrainage ---
@dp.callback_query_handler(lambda c: c.data == "referral")
async def referral_menu(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    ref_link = f"https://t.me/joinleak2techbot?start={user_id}"

    text = (
        "💰 *Programme de Parrainage*\n\n"
        "Partage ton lien et gagne 1€ par personne qui rejoint grâce à toi !\n\n"
        f"🔗 Ton lien : `{ref_link}`\n\n"
        f"👥 Parrainages : {list(data['referrals'].values()).count(user_id)}\n"
        f"💰 Solde : {data['balances'].get(str(user_id), 0)}€\n\n"
        "Pour retirer ton solde, contacte : @leaker2tech"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Retour", callback_data="back_home")]
    ])

    await callback_query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

# --- 🔹 Retour accueil ---
@dp.callback_query_handler(lambda c: c.data == "back_home")
async def back_home(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📲 Rejoindre le canal", url="https://t.me/+9O6qGVz4OOM1NTZk")],
        [InlineKeyboardButton(text="🤝 Parrainage", callback_data="referral")]
    ])
    await callback_query.message.edit_text(
        f"Bienvenue sur LEAK2️⃣TECH📂, {callback_query.from_user.full_name} !\n\n"
        f"Rejoins le canal ci-dessous 👇",
        reply_markup=keyboard
    )

# --- 🧨 Commande admin /broadcast ---
@dp.message_handler(commands=['broadcast'])
async def broadcast(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return

    text = msg.text.replace("/broadcast", "").strip()
    if not text:
        await msg.reply("⚠️ Utilisation : /broadcast [message]")
        return

    sent = 0
    for uid in data["users"]:
        try:
            await bot.send_message(uid, text)
            sent += 1
            await asyncio.sleep(0.5)  # anti-flood
        except Exception as e:
            print(f"Erreur envoi à {uid}: {e}")

    await msg.reply(f"✅ Message envoyé à {sent} utilisateurs.")

# --- 📊 Commande admin /stats ---
@dp.message_handler(commands=['stats'])
async def stats(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return
    total = len(data["users"])
    await msg.reply(f"📈 Utilisateurs : {total}\n💸 Soldes gérés : {len(data['balances'])}")

# --- 🚀 Lancement ---
if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    while True:
        try:
            executor.start_polling(dp, skip_updates=True)
        except Exception as e:
            print(f"Bot crashé : {e}")
            asyncio.sleep(5)