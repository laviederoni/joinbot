import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading

# --- 🔒 VARIABLES D'ENVIRONNEMENT ---
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Défini sur Railway
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # Défini sur Railway

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# --- 🌐 Flask pour garder le bot en ligne ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot LEAK2TECH actif 🚀"

def run_web():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

# --- 📦 Base simple en mémoire (à remplacer par une DB si besoin) ---
referrals = {}
balances = {}

# --- 🔹 Commande /start ---
@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.full_name

    # Récupérer le parrain (si lien referral)
    referrer_id = None
    if message.get_args():
        try:
            referrer_id = int(message.get_args())
        except ValueError:
            pass

    if referrer_id and referrer_id != user_id:
        referrals[user_id] = referrer_id
        balances[referrer_id] = balances.get(referrer_id, 0) + 1

        # 🔔 Notifier le parrain
        try:
            await bot.send_message(
                referrer_id,
                f"💸 Une personne a rejoint le bot grâce à ton lien !\n"
                f"1€ a été ajouté à ton solde.\n\n"
                f"👥 Parrainages : {list(referrals.values()).count(referrer_id)}\n"
                f"💰 Solde total : {balances[referrer_id]}€",
                reply_markup=get_referral_keyboard()
            )
        except:
            pass

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

# --- 🔹 Bouton "Parrainage" ---
@dp.callback_query(lambda c: c.data == "referral")
async def show_referral_menu(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    ref_link = f"https://t.me/joinleak2techbot?start={user_id}"

    text = (
        "💰 *Programme de Parrainage*\n\n"
        "Partage ton lien dans des groupes, sur tes réseaux, ou ton canal "
        "et gagne 1€ par personne qui rejoint le bot grâce à toi !\n\n"
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

# --- 🔹 Bouton "Retour" ---
@dp.callback_query(lambda c: c.data == "back_home")
async def back_to_home(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📲 Rejoindre le canal", url="https://t.me/+9O6qGVz4OOM1NTZk")],
        [InlineKeyboardButton(text="🤝 Parrainage", callback_data="referral")]
    ])
    await callback_query.message.edit_text(
        f"Bienvenue sur LEAK2️⃣TECH📂, {callback_query.from_user.full_name} !\n\n"
        f"Rejoins le canal ci-dessous 👇",
        reply_markup=keyboard
    )

# --- 🚀 Lancement ---
if __name__ == '__main__':
    threading.Thread(target=run_web).start()
    executor.start_polling(dp, skip_updates=True)
