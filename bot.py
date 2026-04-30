import asyncio
import os
import logging
from flask import Flask
from threading import Thread
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from aiogram.filters import Command

API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ---------------- FLASK ----------------
app = Flask(__name__)

@app.route("/")
def home():
    return "JET X BOT is LIVE 🚀"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# ---------------- BATCHES ----------------
BATCHES = {
    "power": {
        "name": "🔥 POWER 6.0 DROPPER RE NEET BATCH",
        "price": 250,
        "desc": """📚 HD Lectures Available (800+ All Subjects)
📚 Weekly Test Available
📚 Mock Test Available
📚 PYQ PDFs Available
📚 Class Notes PDF Available""",
        "channel_id": -1003714582096
    },
    "neet": {
        "name": "🎓 NEET Dropper Batch by NS",
        "price": 100,
        "desc": """📚 HD Lectures Available
📚 Weekly Mock Test
📚 Handwritten Notes
📚 Class Notes Included""",
        "channel_id": -1002703950742
    }
}

# ---------------- START ----------------
@dp.message(Command("start"))
async def start(msg: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Buy Courses", callback_data="courses")],
        [InlineKeyboardButton(text="📩 Admin Contact", url="https://t.me/Jatxchatbot")]
    ])

    await msg.answer(
        "💡📝 *Welcome to JET X BOT*\n\n"
        "🔥 *Top Faculty Lectures Available* 🔥\n\n"
        "📚 India ke best teachers ke high-quality lectures ek hi jagah par!\n"
        "🎯 Perfect for NEET / JEE aspirants\n\n"
        "✨ *What you’ll get:*\n"
        "✔️ Full syllabus coverage\n"
        "✔️ Concept clarity + short tricks\n"
        "✔️ HD quality lectures\n"
        "✔️ Regular updates\n"
        "✔️ Notes + Practice support\n\n"
        "🚀 Apni preparation next level par le jao\n"
        "📈 Top rankers jaisa content ab easily access karo\n\n"
        "💰 Affordable price me premium content",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# ---------------- SHOW COURSES ----------------
@dp.callback_query(F.data == "courses")
async def courses(cb: types.CallbackQuery):
    kb = [
        [InlineKeyboardButton(text=v["name"], callback_data=f"info_{k}")]
        for k, v in BATCHES.items()
    ]
    kb.append([InlineKeyboardButton(text="📩 Admin Contact", url="https://t.me/Jatxchatbot")])

    await cb.message.edit_text(
        "📚 *Select your batch:*",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown"
    )

# ---------------- INFO ----------------
@dp.callback_query(F.data.startswith("info_"))
async def info(cb: types.CallbackQuery):
    key = cb.data.split("_")[1]
    data = BATCHES[key]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Buy Now", callback_data=f"buy_{key}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="courses")]
    ])

    await cb.message.edit_text(
        f"🔥 *{data['name']}*\n\n"
        f"{data['desc']}\n\n"
        f"💰 *Price:* {data['price']} ⭐",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# ---------------- BUY ----------------
@dp.callback_query(F.data.startswith("buy_"))
async def buy(cb: types.CallbackQuery):
    key = cb.data.split("_")[1]
    data = BATCHES[key]

    await bot.send_invoice(
        chat_id=cb.from_user.id,
        title=data["name"],
        description=data["desc"],
        payload=f"pay_{key}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Stars", amount=data["price"])]
    )

# ---------------- PAYMENT SUCCESS ----------------
@dp.message(F.successful_payment)
async def paid(msg: types.Message):
    payload = msg.successful_payment.invoice_payload
    key = payload.split("_")[1]

    data = BATCHES[key]

    expire_time = int((datetime.now() + timedelta(minutes=5)).timestamp())

    link = await bot.create_chat_invite_link(
        chat_id=data["channel_id"],
        member_limit=1,
        expire_date=expire_time
    )

    await msg.answer(
        f"✅ *Payment Successful!*\n\n"
        f"🔗 Join your batch:\n{link.invite_link}\n\n"
        f"⚠️ Link 5 min me expire ho jayega",
        parse_mode="Markdown"
    )

# ---------------- MAIN ----------------
async def main():
    Thread(target=run_flask).start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())