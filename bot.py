import os
import threading
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

# === 🔒 VARIABLES D'ENVIRONNEMENT ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# === 🌐 Flask (garde le bot en ligne sur Render) ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot LEAK2TECH actif sur Render"

def run_web():
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# === 📦 Bases simples ===
referrals = {}
balances = {}
users = set()

# === 🔹 /start ===
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.full_name

    users.add(user_id)

    referrer_id = None
    if message.get_args():
        try:
            referrer_id = int(message.get_args())
        except ValueError:
            pass

    if referrer_id and referrer_id != user_id:
        referrals[user_id] = referrer_id
        balances[referrer_id] = balances.get(referrer_id, 0) + 1

        try:
            await bot.send_message(
                referrer_id,
                f"💸 Une personne a rejoint le bot via ton lien !\n"
                f"1€ ajouté à ton solde 💰\n\n"
                f"👥 Parrainages : {list(referrals.values()).count(referrer_id)}\n"
                f"💰 Solde total : {balances[referrer_id]}€",
                reply_markup=get_referral_keyboard()
            )
        except:
            pass

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📲 Rejoindre le canal", url="https://t.me/+9O6qGVz4OOM1NTZk")],
        [InlineKeyboardButton(text="🤝 Parrainage", callback_data="referral")]
    ])

    await message.answer(
        f"Bienvenue sur *LEAK2️⃣TECH📂*, {username} !\n\n"
        f"Rejoins le canal ci-dessous 👇",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# === 🔹 Menu Parrainage ===
@dp.callback_query_handler(lambda c: c.data == "referral")
async def show_referral_menu(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    ref_link = f"https://t.me/joinleak2techbot?start={user_id}"

    text = (
        "💰 *Programme de Parrainage*\n\n"
        "Partage ton lien et gagne **1€** par personne qui rejoint le bot grâce à toi !\n\n"
        f"🔗 Ton lien : `{ref_link}`\n\n"
        f"👥 Parrainages : {list(referrals.values()).count(user_id)}\n"
        f"💰 Solde : {balances.get(user_id, 0)}€\n\n"
        "Pour retirer ton solde, contacte : @leaker2tech"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Retour", callback_data="back_home")]
    ])

    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# === 🔹 Bouton Retour ===
@dp.callback_query_handler(lambda c: c.data == "back_home")
async def back_to_home(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📲 Rejoindre le canal", url="https://t.me/+9O6qGVz4OOM1NTZk")],
        [InlineKeyboardButton(text="🤝 Parrainage", callback_data="referral")]
    ])
    await callback_query.message.edit_text(
        f"Bienvenue sur *LEAK2️⃣TECH📂*, {callback_query.from_user.full_name} !\n\n"
        f"Rejoins le canal ci-dessous 👇",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# === 🔹 Génère le clavier ===
def get_referral_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📲 Rejoindre le canal", url="https://t.me/+9O6qGVz4OOM1NTZk")],
        [InlineKeyboardButton(text="🤝 Mon lien de parrainage", callback_data="referral")]
    ])

# === 👑 Commande admin : /stats ===
@dp.message_handler(commands=['stats'])
async def stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("🚫 Tu n'es pas autorisé à voir ces stats.")

    total_users = len(users)
    total_referrals = len(referrals)
    total_balance = sum(balances.values())

    await message.reply(
        f"📊 *Statistiques du Bot*\n\n"
        f"👥 Utilisateurs : {total_users}\n"
        f"🔗 Parrainages : {total_referrals}\n"
        f"💰 Total distribué : {total_balance}€",
        parse_mode="Markdown"
    )

# === 👑 Commande admin : /broadcast ===
@dp.message_handler(commands=['broadcast'])
async def broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("🚫 Tu n'es pas autorisé à envoyer des messages globaux.")

    text = message.text.replace("/broadcast", "").strip()
    if not text:
        return await message.reply("📝 Utilisation : `/broadcast ton_message`", parse_mode="Markdown")

    count = 0
    for uid in list(users):
        try:
            await bot.send_message(uid, text)
            count += 1
        except:
            pass

    await message.reply(f"✅ Message envoyé à {count} utilisateurs.")

# === 🚀 Lancement ===
if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    executor.start_polling(dp, skip_updates=True)