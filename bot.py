import asyncio
import os
import logging
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import LabeledPrice, PreCheckoutQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command

# --- RENDER KE LIYE WEB SERVER (Bot ko on rakhne ke liye) ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is Running!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

# --- CONFIGURATION ---
API_TOKEN = 'YAHAN_BOT_TOKEN_DALO' # BotFather se lo

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- BATCHES SETUP (Yahan apni details bharein) ---
# Tip: ID wahi rakhein jo link generate karni hai
BATCHES = {
    "yakeen_2025": {
        "name": "Yakeen 2025 (NEET)",
        "price": 165, # Approx ₹300
        "desc": "Full PCB lectures + Notes",
        "channel_id": -100123456789  # Asli Channel ID yahan dalein
    },
    "avengers_batch": {
        "name": "JEE Avengers",
        "price": 110, # Approx ₹200
        "desc": "Maths Special with PYQs",
        "channel_id": -100987654321  # Dusre channel ki ID
    }
}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    buttons = []
    for b_id, b_info in BATCHES.items():
        buttons.append([InlineKeyboardButton(text=f"📚 {b_info['name']}", callback_query_data=f"info_{b_id}")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("👋 *Welcome to our Platform!*\n\nNiche diye gaye batches par tap karein details dekhne ke liye:", reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("info_"))
async def batch_info(callback: types.CallbackQuery):
    b_id = callback.data.split("_")
    info = BATCHES[b_id]
    text = f"🔥 *{info['name']}*\n\n📝 *Details:* {info['desc']}\n💰 *Price:* ₹{int(info['price']*1.8)} (via Stars)"
    buy_btn = [[InlineKeyboardButton(text="💳 Buy Now", callback_query_data=f"buy_{b_id}")]]
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buy_btn), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("buy_"))
async def send_payment(callback: types.CallbackQuery):
    b_id = callback.data.split("_")
    info = BATCHES[b_id]
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=info["name"],
        description=f"Payment for {info['name']}",
        payload=f"pay_{b_id}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Stars", amount=info["price"])]
    )

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message(F.successful_payment)
async def on_success(message: types.Message):
    payload = message.successful_payment.invoice_payload
    b_id = payload.split("_")
    target_channel = BATCHES[b_id]["channel_id"]

    # 5 min expiry, 1 person limit link
    invite_link = await bot.create_chat_invite_link(
        chat_id=target_channel,
        member_limit=1,
        expire_date=int(asyncio.get_event_loop().time()) + 300
    )

    await message.answer(f"✅ *Payment Successful!*\n\nYe raha aapka access link (5 min mein expire ho jayega):\n\n🔗 {invite_link.invite_link}", parse_mode="Markdown")

async def main():
    Thread(target=run_web).start() # Web server chalu karein
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
