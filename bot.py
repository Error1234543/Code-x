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
    "neet": {
        "name": "🎓 NEET 2025 Dropper / NEET Batch",
        "price": 100,
        "desc": """✅ HD Lectures Available
✅ Weekly Mock Test
✅ Handwritten Notes
✅ Class Notes Included""",
        "channel_id": -1002703950742
    },
    "physics": {
        "name": "🎓 PHYSICS 5.0",
        "price": 100,
        "desc": "📚 167 Lectures Available (HD Quality)",
        "channel_id": -1002648606297
    },
    "fire": {
        "name": "🔥 Physics 4.0",
        "price": 100,
        "desc": "✅ HD Lectures Available",
        "channel_id": -1002492489194
    },
    "pcb": {
        "name": "🎓 STD 12 PCB BOARD",
        "price": 100,
        "desc": """📦 FULL BATCH DOWNLOAD
📚 417 Lectures Available""",
        "channel_id": -1003053248183
    }
}

# ---------------- START ----------------
@dp.message(Command("start"))
async def start(msg: types.Message):
    kb = [
        [InlineKeyboardButton(text=v["name"], callback_data=f"info_{k}")]
        for k, v in BATCHES.items()
    ]

    await msg.answer(
        "👋 *Welcome to JET X BOT*\n\n"
        "💰 Fixed Price: 100 ⭐\n\n"
        "📚 Select your batch:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown"
    )

# ---------------- INFO ----------------
@dp.callback_query(F.data.startswith("info_"))
async def info(cb: types.CallbackQuery):
    key = cb.data.split("_")[1]
    data = BATCHES[key]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Buy Now (100 ⭐)", callback_data=f"buy_{key}")],
        [InlineKeyboardButton(text="💰 Custom Payment", callback_data="custom_pay")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back")]
    ])

    await cb.message.edit_text(
        f"🔥 *{data['name']}*\n\n"
        f"{data['desc']}\n\n"
        f"💰 Price: {data['price']} ⭐",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# ---------------- CUSTOM PAYMENT MENU ----------------
@dp.callback_query(F.data == "custom_pay")
async def custom_pay(cb: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="25 ⭐", callback_data="pay_25")],
        [InlineKeyboardButton(text="50 ⭐", callback_data="pay_50")],
        [InlineKeyboardButton(text="75 ⭐", callback_data="pay_75")],
        [InlineKeyboardButton(text="100 ⭐", callback_data="pay_100")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back")]
    ])

    await cb.message.edit_text(
        "💰 *Custom Payment Choose karo:*",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# ---------------- PAYMENT (CUSTOM + BATCH) ----------------
@dp.callback_query(F.data.startswith("pay_"))
async def pay(cb: types.CallbackQuery):
    stars = int(cb.data.split("_")[1])

    await bot.send_invoice(
        chat_id=cb.from_user.id,
        title="JET X PAYMENT",
        description="Course Access",
        payload=f"custom_{stars}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Stars", amount=stars)]
    )

# ---------------- BACK ----------------
@dp.callback_query(F.data == "back")
async def back(cb: types.CallbackQuery):
    kb = [
        [InlineKeyboardButton(text=v["name"], callback_data=f"info_{k}")]
        for k, v in BATCHES.items()
    ]

    await cb.message.edit_text(
        "📚 Choose your batch:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
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

    # CUSTOM PAYMENT
    if "custom_" in payload:
        await msg.answer("✅ Custom Payment Successful 🎉")
        return

    key = payload.split("_")[1]
    data = BATCHES[key]

    expire_time = int((datetime.now() + timedelta(minutes=5)).timestamp())

    link = await bot.create_chat_invite_link(
        chat_id=data["channel_id"],
        member_limit=1,
        expire_date=expire_time
    )

    await msg.answer(
        f"✅ Payment Successful!\n\n"
        f"🔗 Join Link:\n{link.invite_link}\n\n"
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