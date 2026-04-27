import asyncio
import os
import logging
from flask import Flask
from threading import Thread

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from aiogram.filters import Command

API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ---------------- FLASK (FOR RENDER PORT FIX) ----------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running 🚀"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# ---------------- BATCHES ----------------
BATCHES = {
    "neet_2025": {
        "name": "🎓 NEET 2025 Dropper Batch",
        "price": 110,
        "desc": "HD Lectures + Tests + Notes",
        "channel_id": -1002703950742
    },
    "physics_5.0": {
        "name": "🎓 PHYSICS 5.0",
        "price": 110,
        "desc": "167 Lectures Full Course",
        "channel_id": -1002648606297
    },
    "fire_physics": {
        "name": "🔥 Fire Physics",
        "price": 110,
        "desc": "Advanced Physics",
        "channel_id": -1002492489194
    },
    "std_12_pcb": {
        "name": "🎓 STD 12 PCB",
        "price": 110,
        "desc": "Full Board Course",
        "channel_id": -1003053248183
    }
}

# ---------------- START ----------------
@dp.message(Command("start"))
async def start(msg: types.Message):
    kb = [[InlineKeyboardButton(text=v["name"], callback_data=f"info_{k})] for k, v in BATCHES.items()]
    await msg.answer("🚀 Select Batch:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

# ---------------- INFO ----------------
@dp.callback_query(F.data.startswith("info_"))
async def info(cb: types.CallbackQuery):
    key = cb.data.split("_")[1]
    data = BATCHES[key]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Buy", callback_data=f"buy_{key}")]
    ])

    await cb.message.edit_text(f"{data['name']}\n\n{data['desc']}", reply_markup=kb)

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

# ---------------- PAYMENT ----------------
@dp.message(F.successful_payment)
async def paid(msg: types.Message):
    await msg.answer("✅ Payment Success!")

# ---------------- MAIN ----------------
async def main():
    Thread(target=run_flask).start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())