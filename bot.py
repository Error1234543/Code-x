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
WEBHOOK_PATH = "/webhook"
BASE_URL = os.getenv("RENDER_EXTERNAL_URL")  # Render auto provides
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ---------------- FLASK SERVER ----------------
app = Flask(__name__)

@app.route("/")
def home():
    return "JET X BOT is Online!"

# Telegram webhook endpoint
@app.route(WEBHOOK_PATH, methods=["POST"])
async def telegram_webhook():
    update = types.Update(**request.json)
    await dp.feed_update(bot, update)
    return "OK"

def run_web():
    app.run(host="0.0.0.0", port=8080)

# ---------------- DATABASE ----------------
BATCHES = {
    "neet_2025": {
        "name": "🎓 NEET 2025 Dropper Batch",
        "price": 110,
        "desc": "HD Lectures + Mock Tests",
        "channel_id": -1002703950742
    },
    "physics_5.0": {
        "name": "🎓 PHYSICS 5.0",
        "price": 110,
        "desc": "167 HD Lectures",
        "channel_id": -1002648606297
    }
}

# ---------------- START ----------------
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
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
async def show_details(callback: types.CallbackQuery):
    b_id = callback.data.split("_", 1)[1]
    info = BATCHES[b_id]

    text = f"🔥 {info['name']}\n\n{info['desc']}\n\n💰 Price: ₹{info['price']}"

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
        "👋 Choose batch:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

# ---------------- PAYMENT ----------------
@dp.callback_query(F.data.startswith("buy_"))
async def buy(callback: types.CallbackQuery):
    b_id = callback.data.split("_", 1)[1]
    info = BATCHES[b_id]

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=info["name"],
        description=info["desc"],
        payload=f"pay_{b_id}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Stars", amount=info["price"])]
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

    await message.answer(
        f"✅ Payment Done!\nJoin: {invite.invite_link}"
    )

# ---------------- STARTUP ----------------
async def on_start():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)

async def main():
    Thread(target=run_web).start()
    await on_start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())