# bot.py
# Telegram Website + Temporary Channel Access Bot
# Koyeb Ready

import os
import json
import time
from threading import Thread
from flask import Flask

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo
)

# ==========================================
# FLASK HEALTH CHECK
# ==========================================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Running Successfully"

def run_web():
    app.run(host="0.0.0.0", port=8000)

Thread(target=run_web).start()

# ==========================================
# BOT CONFIG
# ==========================================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client(
    "MiniAppBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ==========================================
# LOAD JSON DATA
# ==========================================

with open("data.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)

FORCE_CHANNELS = DATA["force_channels"]
WEBSITES = DATA["websites"]
CHANNELS = DATA["channels"]

# ==========================================
# FORCE JOIN CHECK
# ==========================================

async def check_join(user_id):

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
async def start(client, message):

    joined = await check_join(message.from_user.id)

    # ======================================
    # FORCE JOIN PAGE
    # ======================================

    if not joined:

        buttons = []

        for ch in FORCE_CHANNELS:

            buttons.append([
                InlineKeyboardButton(
                    ch["name"],
                    url=ch["join_link"]
                )
            ])

        buttons.append([
            InlineKeyboardButton(
                "✅ VERIFY JOIN",
                callback_data="verify_join"
            )
        ])

        await message.reply_text(
            """
✨ Welcome To Our Educational Hub ✨

📚 Here You Will Get:

• Test Websites
• Study Materials
• Practice Systems
• Official Channels

⚡ First Join All Channels Then Click Verify.
            """,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        return

    # ======================================
    # MAIN MENU
    # ======================================

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🌐 OUR WEBSITES",
                callback_data="websites"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 OUR CHANNELS",
                callback_data="channels"
            )
        ]
    ])

    await message.reply_text(
        """
🚀 Welcome To Main System

📚 Access:
• Test Websites
• Study Materials
• Official Channels

⚡ Everything Organized In One Place.
        """,
        reply_markup=keyboard
    )

# ==========================================
# VERIFY JOIN
# ==========================================

@bot.on_callback_query(filters.regex("^verify_join$"))
async def verify_join(client, callback_query):

    joined = await check_join(callback_query.from_user.id)

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
                "📢 OUR CHANNELS",
                callback_data="channels"
            )
        ]
    ])

    await callback_query.message.edit_text(
        """
✅ Verification Successful

🚀 Welcome To Main System
        """,
        reply_markup=keyboard
    )

# ==========================================
# WEBSITES
# ==========================================

@bot.on_callback_query(filters.regex("^websites$"))
async def websites(client, callback_query):

    buttons = []

    for site in WEBSITES:

        buttons.append([
            InlineKeyboardButton(
                text=site["name"],
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
        "🌐 OUR WEBSITES\n\nSelect Any Website 👇",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ==========================================
# CHANNELS
# ==========================================

@bot.on_callback_query(filters.regex("^channels$"))
async def channels(client, callback_query):

    buttons = []

    for ch in CHANNELS:

        buttons.append([
            InlineKeyboardButton(
                ch["name"],
                callback_data=f"channel_{ch['id']}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            "🔙 BACK",
            callback_data="back_home"
        )
    ])

    await callback_query.message.edit_text(
        "📢 OUR CHANNELS\n\nSelect Any Channel 👇",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ==========================================
# GENERATE TEMP CHANNEL LINK
# ==========================================

@bot.on_callback_query(filters.regex("^channel_"))
async def channel_access(client, callback_query):

    channel_id = int(
        callback_query.data.replace("channel_", "")
    )

    selected = None

    for ch in CHANNELS:

        if ch["id"] == channel_id:
            selected = ch
            break

    if not selected:
        return

    try:

        invite = await bot.create_chat_invite_link(
            chat_id=selected["id"],
            expire_date=int(time.time()) + 60,
            member_limit=1
        )

        await callback_query.message.reply_text(
            f"""
🔐 Temporary Access Link Generated

⚡ This link expires automatically in 1 minute.

{invite.invite_link}
            """
        )

    except Exception as e:

        await callback_query.message.reply_text(
            f"❌ Error:\n{e}"
        )

# ==========================================
# BACK BUTTON
# ==========================================

@bot.on_callback_query(filters.regex("^back_home$"))
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
                "📢 OUR CHANNELS",
                callback_data="channels"
            )
        ]
    ])

    await callback_query.message.edit_text(
        "🏠 Main Menu",
        reply_markup=keyboard
    )

# ==========================================
# RUN BOT
# ==========================================

print("Bot Running Successfully...")
bot.run()