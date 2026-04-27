import asyncio
import os
import logging
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import LabeledPrice, PreCheckoutQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

# --- RENDER WEB SERVER ---
app = Flask('')
@app.route('/')
def home(): return "JET X BOT is Online!"
def run_web(): app.run(host='0.0.0.0', port=8080)

# --- CONFIGURATION ---
API_TOKEN = os.getenv('BOT_TOKEN') 
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- BATCHES DATABASE ---
BATCHES = {
    "neet_2025": {
        "name": "🎓 NEET 2025 Dropper Batch",
        "price": 110,
        "desc": "✅ HD Lectures Available\n✅ Weekly Mock Tests\n✅ Handwriting & Class Notes",
        "channel_id": -1002703950742
    },
    "physics_5.0": {
        "name": "🎓 PHYSICS 5.0",
        "price": 110, 
        "desc": "✅ 167 HD Quality Lectures\n✅ Complete Physics Mastery",
        "channel_id": -1002648606297
    },
    "fire_physics": {
        "name": "🎓 Fire Physics 4.0",
        "price": 110,
        "desc": "✅ HD Lectures Available\n✅ Special Fire Physics Content",
        "channel_id": -1002492489194
    },
    "std_12_pcb": {
        "name": "🎓 STD 12 PCB BOARD",
        "price": 110,
        "desc": "✅ Full Batch Download\n✅ 417 Lectures Available\n✅ Complete Board Prep",
        "channel_id": -1003053248183
    }
}

# 1. Start Command: Fixed Inline Keyboard Logic
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    
    for b_id, info in BATCHES.items():
        # Har batch ke liye ek naya button row
        builder.row(InlineKeyboardButton(
            text=info['name'], 
            callback_query_data=f"info_{b_id}")
        )
    
    await message.answer(
        "👋 *Welcome to JET X PLATFORM!*\n\nNiche diye gaye batches mein se kisi ek par tap karein details dekhne ke liye:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

# 2. Detail View & Buy Now
@dp.callback_query(F.data.startswith("info_"))
async def show_details(callback: types.CallbackQuery):
    b_id = callback.data.split("_")
    info = BATCHES[b_id]
    
    detail_text = (
        f"🔥 *{info['name']}*\n\n"
        f"📝 *Details:*\n{info['desc']}\n\n"
        f"💰 *Price:* ₹199 (Pay via Stars)"
    )
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💳 Buy Now", callback_query_data=f"buy_{b_id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Back to List", callback_query_data="back_to_list"))
    
    await callback.message.edit_text(
        detail_text, 
        reply_markup=builder.as_markup(), 
        parse_mode="Markdown"
    )

# 3. Back to List
@dp.callback_query(F.data == "back_to_list")
async def back_to_list(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    for b_id, info in BATCHES.items():
        builder.row(InlineKeyboardButton(text=info['name'], callback_query_data=f"info_{b_id}"))
    
    await callback.message.edit_text(
        "👋 Choose your batch:",
        reply_markup=builder.as_markup()
    )

# 4. Invoice
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

# 5. Pre-checkout & Success
@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message(F.successful_payment)
async def on_success(message: types.Message):
    payload = message.successful_payment.invoice_payload
    b_id = payload.split("_")
    target_channel = BATCHES[b_id]["channel_id"]

    invite_link = await bot.create_chat_invite_link(
        chat_id=target_channel,
        member_limit=1,
        expire_date=int(asyncio.get_event_loop().time()) + 300
    )

    await message.answer(
        f"✅ *Payment Successful!*\n\n🔗 [CLICK TO JOIN BATCH]({invite_link.invite_link})\n\n(Link 5 min mein expire ho jayega)",
        parse_mode="Markdown"
    )

async def main():
    Thread(target=run_web).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
