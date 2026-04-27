import asyncio
import os
import logging
from flask import Flask, request
from threading import Thread

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command

# ---------------- CONFIG ----------------
API_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_URL = f"{BASE_URL}/webhook"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ---------------- FLASK ----------------
app = Flask(__name__)

@app.route("/")
def home():
    return "JET X BOT is LIVE 🚀"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = types.Update(**data)

        asyncio.run(dp.feed_update(bot, update))
        return "OK"
    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return "ERROR", 500

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# ---------------- BATCHES ----------------
BATCHES = {
    "neet_2025": {
        "name": "🎓 NEET 2025 Batch",
        "price": 110,
        "desc": "HD Lectures + Notes",
        "channel_id": -1002703950742
    },
    "physics_5": {
        "name": "🎓 Physics 5.0",
        "price": 110,
        "desc": "Complete Physics Course",
        "channel_id": -1002648606297
    }
}

# ---------------- START ----------------
@dp.message(Command("start"))
async def start(message: types.Message):
    buttons = [
        [InlineKeyboardButton(text=i["name"], callback_data=f"info_{k}")]
        for k, i in BATCHES.items()
    ]

    await message.answer(
        "👋 Welcome to JET X BOT",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

# ---------------- INFO ----------------
@dp.callback_query(F.data.startswith("info_"))
async def info(callback: types.CallbackQuery):
    b_id = callback.data.split("_", 1)[1]
    data = BATCHES[b_id]

    text = f"🔥 {data['name']}\n\n{data['desc']}\n\n💰 Price: ₹{data['price']}"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Buy Now", callback_data=f"buy_{b_id}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back")]
    ])

    await callback.message.edit_text(text, reply_markup=kb)

# ---------------- BACK ----------------
@dp.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery):
    buttons = [
        [InlineKeyboardButton(text=i["name"], callback_data=f"info_{k}")]
        for k, i in BATCHES.items()
    ]

    await callback.message.edit_text(
        "👋 Choose Batch:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

# ---------------- BUY ----------------
@dp.callback_query(F.data.startswith("buy_"))
async def buy(callback: types.CallbackQuery):
    b_id = callback.data.split("_", 1)[1]
    data = BATCHES[b_id]

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=data["name"],
        description=data["desc"],
        payload=f"pay_{b_id}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Stars", amount=data["price"])]
    )

# ---------------- PAYMENT SUCCESS ----------------
@dp.message(F.successful_payment)
async def success(message: types.Message):
    payload = message.successful_payment.invoice_payload
    b_id = payload.split("_", 1)[1]

    channel_id = BATCHES[b_id]["channel_id"]

    invite = await bot.create_chat_invite_link(
        chat_id=channel_id,
        member_limit=1
    )

    await message.answer(f"✅ Paid!\nJoin here: {invite.invite_link}")

# ---------------- STARTUP ----------------
async def on_start():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)

async def main():
    Thread(target=run_flask).start()
    await on_start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())