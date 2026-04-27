import asyncio
import os
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from aiogram.filters import Command

API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ---------------- ALL BATCHES ----------------
BATCHES = {
    "neet_2025": {
        "name": "🎓 NEET 2025 Dropper Batch",
        "price": 110,
        "desc": "HD Lectures + Weekly Tests + Notes",
        "channel_id": -1002703950742
    },
    "physics_5.0": {
        "name": "🎓 PHYSICS 5.0",
        "price": 110,
        "desc": "167 HD Lectures + Full Physics Mastery",
        "channel_id": -1002648606297
    },
    "fire_physics": {
        "name": "🔥 Fire Physics 4.0",
        "price": 110,
        "desc": "Advanced Physics Crash Course",
        "channel_id": -1002492489194
    },
    "std_12_pcb": {
        "name": "🎓 STD 12 PCB Board",
        "price": 110,
        "desc": "Full Board Course (417 Lectures)",
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
        "🚀 Welcome to JET X BOT\nChoose your batch:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )

# ---------------- INFO ----------------
@dp.callback_query(F.data.startswith("info_"))
async def info(cb: types.CallbackQuery):
    key = cb.data.split("_")[1]
    data = BATCHES[key]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Buy Now", callback_data=f"buy_{key}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back")]
    ])

    await cb.message.edit_text(
        f"🔥 {data['name']}\n\n{data['desc']}\n\n💰 Price: ₹{data['price']}",
        reply_markup=kb
    )

# ---------------- BACK ----------------
@dp.callback_query(F.data == "back")
async def back(cb: types.CallbackQuery):
    kb = [
        [InlineKeyboardButton(text=v["name"], callback_data=f"info_{k}")]
        for k, v in BATCHES.items()
    ]

    await cb.message.edit_text(
        "🚀 Choose Batch:",
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

# ---------------- PAYMENT ----------------
@dp.message(F.successful_payment)
async def paid(msg: types.Message):
    await msg.answer("✅ Payment Success! Access will be given soon.")

# ---------------- MAIN ----------------
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())