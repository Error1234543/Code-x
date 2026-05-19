
# bot.py
# Koyeb Deploy Ready Telegram Bot

import os
import json
from flask import Flask
from threading import Thread

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo
)

# ==========================================
# KEEP ALIVE SERVER FOR KOYEB HEALTH CHECK
# ==========================================

app = Flask('')

@app.route('/')
def home():
    return "Bot Is Running Successfully!"

def run_web():
    app.run(host='0.0.0.0', port=8000)

Thread(target=run_web).start()

# ==========================================
# BOT CONFIG
# ==========================================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client(
    "WebsiteHubBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ==========================================
# LOAD JSON DATA
# ==========================================

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

FORCE_CHANNELS = data["force_channels"]
WEBSITES = data["websites"]
CHANNELS = data["channels"]

# ==========================================
# CHECK FORCE JOIN
# ==========================================

async def is_joined(user_id):

    try:

        for ch in FORCE_CHANNELS:

            member = await bot.get_chat_member(
                ch["id"],
                user_id
            )

            if member.status in ["left", "kicked"]:
                return False

        return True

    except:
        return False

# ==========================================
# START COMMAND
# ==========================================

@bot.on_message(filters.command("start"))
async def start_command(client, message):

    user_id = message.from_user.id

    joined = await is_joined(user_id)

    # ==========================
    # FORCE JOIN PAGE
    # ==========================

    if not joined:

        buttons = []

        for ch in FORCE_CHANNELS:

            buttons.append([
                InlineKeyboardButton(
                    ch["name"],
                    url=ch["link"]
                )
            ])

        buttons.append([
            InlineKeyboardButton(
                "✅ VERIFY JOIN",
                callback_data="verify_join"
            )
        ])

        await message.reply_text(
            text="""
✨ Welcome To Our Educational Hub ✨

📚 Here You Will Get:

• Test Websites
• Study Materials
• Practice Platforms
• Educational Updates
• All Official Channels

⚡ First Join All Channels Then Click Verify.
            """,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        return

    # ==========================
    # MAIN HOME PAGE
    # ==========================

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🌐 OUR WEBSITES",
                callback_data="websites"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 OUR ALL CHANNELS",
                callback_data="channels"
            )
        ]
    ])

    await message.reply_text(
        text="""
🚀 Welcome To Our Main System

📚 Access:
• Test Websites
• Materials
• Practice Systems
• All Channels

⚡ Everything Organized In One Place.
        """,
        reply_markup=keyboard
    )

# ==========================================
# VERIFY BUTTON
# ==========================================

@bot.on_callback_query(filters.regex("verify_join"))
async def verify_join(client, callback_query):

    user_id = callback_query.from_user.id

    joined = await is_joined(user_id)

    if not joined:

        await callback_query.answer(
            "❌ First Join All Channels",
            show_alert=True
        )

        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🌐 OUR WEBSITES",
                callback_data="websites"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 OUR ALL CHANNELS",
                callback_data="channels"
            )
        ]
    ])

    await callback_query.message.edit_text(
        text="""
✅ Verification Successful

🚀 Welcome To Main System
        """,
        reply_markup=keyboard
    )

# ==========================================
# WEBSITES
# ==========================================

@bot.on_callback_query(filters.regex("websites"))
async def websites(client, callback_query):

    buttons = []

    for site in WEBSITES:

        buttons.append([
            InlineKeyboardButton(
                site["name"],
                web_app=WebAppInfo(site["link"])
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            "🔙 BACK",
            callback_data="back_home"
        )
    ])

    await callback_query.message.edit_text(
        text="""
🌐 OUR WEBSITES

⚡ Click Any Website Below.
        """,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ==========================================
# CHANNELS
# ==========================================

@bot.on_callback_query(filters.regex("channels"))
async def channels(client, callback_query):

    buttons = []

    for ch in CHANNELS:

        buttons.append([
            InlineKeyboardButton(
                ch["name"],
                url=ch["link"]
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            "🔙 BACK",
            callback_data="back_home"
        )
    ])

    await callback_query.message.edit_text(
        text="""
📢 OUR ALL CHANNELS

⚡ Join All Channels Below.
        """,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ==========================================
# BACK BUTTON
# ==========================================

@bot.on_callback_query(filters.regex("back_home"))
async def back_home(client, callback_query):

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🌐 OUR WEBSITES",
                callback_data="websites"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 OUR ALL CHANNELS",
                callback_data="channels"
            )
        ]
    ])

    await callback_query.message.edit_text(
        text="""
🏠 Main Menu

⚡ Select Any Option Below.
        """,
        reply_markup=keyboard
    )

# ==========================================
# START BOT
# ==========================================

print("Bot Running Successfully...")
bot.run()