import asyncio
import os
import logging
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import LabeledPrice, PreCheckoutQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command

# --- RENDER WEB SERVER (Keeping Bot Alive) ---
app = Flask('')
@app.route('/')
def home():
    return "JET X BOT is Online!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

# --- BOT CONFIGURATION ---
API_TOKEN = '8459827002:AAF1eJmt9y5gQRRWlqRkWbcdDwTK6kSvWjU' # @BotFather se apna token yahan dalein
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- BATCHES DATABASE ---
BATCHES = {
    "neet_2025": {
        "name": "NEET 2025 Dropper Batch",
        "price": 110, # Approx ₹199-200
        "desc": "✅ HD Lectures Available\n✅ Weekly Mock Tests\n✅ Handwriting Notes\n✅ Class Notes Included",
        "channel_id": -1002703950742
    },
    "physics_5.0": {
        "name": "PHYSICS 5.0",
        "price": 110, 
        "desc": "✅ 167 HD Quality Lectures\n✅ Complete Physics Mastery",
        "channel_id": -1002648606297
    },
    "fire_physics": {
        "name": "Fire Physics 4.0",
        "price": 110,
        "desc": "✅ HD Lectures Available\n✅ Special Fire Physics Content",
        "channel_id": -1002492489194
    },
    "std_12_pcb": {
        "name": "STD 12 PCB BOARD",
        "price": 110,
        "desc": "✅ Full Batch Download\n✅ 417 Lectures Available\n✅ Complete Board Prep",
        "channel_id": -1003053248183
    }
}

# 1. Start Command UI
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    buttons = []
    for b_id, b_info in BATCHES.items():
        buttons.append([InlineKeyboardButton(text=f"🎓 {b_info['name']}", callback_query_data=f"info_{b_id}")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    welcome_text = (
        "👋 *Welcome to JET X PLATFORM!*\n\n"
        "Niche diye gaye batches mein se apna manpasand batch chunein aur details dekhein."
    )
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")

# 2. Detail View & Buy Button
@dp.callback_query(F.data.startswith("info_"))
async def batch_info(callback: types.CallbackQuery):
    b_id = callback.data.split("_")
    info = BATCHES[b_id]
    
    detail_text = (
        f"🔥 *Batch:* {info['name']}\n\n"
        f"📝 *Details:*\n{info['desc']}\n\n"
        f"💰 *Price:* ₹199 (Pay via Stars)"
    )
    
    kb = [
        [InlineKeyboardButton(text="💳 Buy Now & Join", callback_query_data=f"buy_{b_id}")],
        [InlineKeyboardButton(text="⬅️ Back to Batches", callback_query_data="back_home")]
    ]
    
    await callback.message.edit_text(detail_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")

# 3. Back to Start
@dp.callback_query(F.data == "back_home")
async def back_home(callback: types.CallbackQuery):
    buttons = []
    for b_id, b_info in BATCHES.items():
        buttons.append([InlineKeyboardButton(text=f"🎓 {b_info['name']}", callback_query_data=f"info_{b_id}")])
    
    await callback.message.edit_text("👋 Welcome! Chose your batch:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# 4. Stars Invoice
@dp.callback_query(F.data.startswith("buy_"))
async def send_payment(callback: types.CallbackQuery):
    b_id = callback.data.split("_")
    info = BATCHES[b_id]
    
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=info["name"],
        description=f"Immediate access to {info['name']}",
        payload=f"pay_{b_id}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Stars", amount=info["price"])]
    )

# 5. Payment Validation
@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

# 6. Success & Auto-Link Generation
@dp.message(F.successful_payment)
async def on_success(message: types.Message):
    payload = message.successful_payment.invoice_payload
    b_id = payload.split("_")
    target_channel = BATCHES[b_id]["channel_id"]

    # 1 member limit, 5 min expiry link
    invite_link = await bot.create_chat_invite_link(
        chat_id=target_channel,
        member_limit=1,
        expire_date=int(asyncio.get_event_loop().time()) + 300
    )

    success_msg = (
        "✅ *Payment Successful!*\n\n"
        "Aapka access link niche diya gaya hai. Dhayan rahe:\n"
        "1. Ye link *5 minute* mein expire ho jayega.\n"
        "2. Ye sirf *1 person* ke liye hai.\n\n"
        f"🔗 [CLICK TO JOIN BATCH]({invite_link.invite_link})"
    )
    await message.answer(success_msg, parse_mode="Markdown")

async def main():
    Thread(target=run_web).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
