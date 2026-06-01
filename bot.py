import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from database import Database
from vplink_api import VPLinkAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── Config from environment ───────────────────────────────────────────────────
BOT_TOKEN       = os.getenv("BOT_TOKEN")
VPLINK_API_KEY  = os.getenv("VPLINK_API_KEY")
CHANNEL_1_ID    = os.getenv("CHANNEL_1_ID")   # e.g. -1001234567890
CHANNEL_2_ID    = os.getenv("CHANNEL_2_ID")
CHANNEL_1_NAME  = os.getenv("CHANNEL_1_NAME", "NEET Batch 1")
CHANNEL_2_NAME  = os.getenv("CHANNEL_2_NAME", "NEET Batch 2")
ACCESS_HOURS    = int(os.getenv("ACCESS_HOURS", "19"))

db      = Database()
vplink  = VPLinkAPI(VPLINK_API_KEY)

# ─── /start handler ────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.ensure_user(user.id, user.username or user.first_name)

    welcome_text = (
        f"👋 *Welcome {user.first_name}!*\n\n"
        f"🎓 Aap neeche diye buttons se apne batch ka *19-hour access link* generate kar sakte ho.\n\n"
        f"⚠️ *Important:*\n"
        f"• Link sirf *2 minute* valid rahega\n"
        f"• Ek link se sirf *1 user* join kar sakta hai\n"
        f"• *19 hours* baad access automatically remove ho jayega\n"
        f"• Dobara access ke liye naya link generate karna hoga"
    )

    keyboard = [
        [InlineKeyboardButton(f"🔗 {CHANNEL_1_NAME} – Link Generate Karo", callback_data="gen_ch1")],
        [InlineKeyboardButton(f"🔗 {CHANNEL_2_NAME} – Link Generate Karo", callback_data="gen_ch2")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)


# ─── Button callback handler ───────────────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user    = query.from_user
    data    = query.data

    if data == "gen_ch1":
        channel_id   = CHANNEL_1_ID
        channel_name = CHANNEL_1_NAME
    elif data == "gen_ch2":
        channel_id   = CHANNEL_2_ID
        channel_name = CHANNEL_2_NAME
    else:
        return

    # Check if user already has active access
    active = db.get_active_access(user.id, channel_id)
    if active:
        remaining = active["expires_at"] - datetime.now()
        hours_left = int(remaining.total_seconds() // 3600)
        mins_left  = int((remaining.total_seconds() % 3600) // 60)
        await query.edit_message_text(
            f"⏳ *Aapka access already active hai!*\n\n"
            f"📌 Channel: *{channel_name}*\n"
            f"⏱ Remaining: *{hours_left}h {mins_left}m*\n\n"
            f"19 hours baad aap dobara link generate kar sakte ho.",
            parse_mode="Markdown"
        )
        return

    # Generate invite link via Telegram Bot API (1 user, 2 min expiry)
    await query.edit_message_text("⏳ *Link generate ho raha hai... thoda wait karo*", parse_mode="Markdown")

    try:
        expire_time = datetime.now() + timedelta(minutes=2)
        invite = await context.bot.create_chat_invite_link(
            chat_id=int(channel_id),
            expire_date=expire_time,
            member_limit=1,
            name=f"Access-{user.id}"
        )

        # Generate a VPLink short URL wrapping the invite link
        short_url = await vplink.shorten(invite.invite_link)

        # Save access record
        access_expires = datetime.now() + timedelta(hours=ACCESS_HOURS)
        db.create_access(user.id, channel_id, channel_name, invite.invite_link, access_expires)

        await query.edit_message_text(
            f"✅ *Link Ready!*\n\n"
            f"📌 Batch: *{channel_name}*\n\n"
            f"🔗 *Apna Access Link:*\n`{short_url}`\n\n"
            f"⚠️ Ye link sirf *2 minute* valid hai aur sirf *aap* join kar sakte ho.\n"
            f"🕐 *19 hours* baad access automatically remove ho jayega.",
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Link generation error for user {user.id}: {e}")
        await query.edit_message_text(
            "❌ *Kuch gadbad ho gayi!* Thodi der baad try karo ya admin se contact karo.",
            parse_mode="Markdown"
        )


# ─── Auto-remove expired users ─────────────────────────────────────────────────
async def remove_expired_users(app: Application):
    expired = db.get_expired_accesses()
    for record in expired:
        user_id    = record["user_id"]
        channel_id = record["channel_id"]
        try:
            await app.bot.ban_chat_member(chat_id=int(channel_id), user_id=user_id)
            await app.bot.unban_chat_member(chat_id=int(channel_id), user_id=user_id)  # unban so they can rejoin later
            db.mark_access_removed(record["id"])
            logger.info(f"Removed user {user_id} from {channel_id}")

            # Notify user
            try:
                await app.bot.send_message(
                    chat_id=user_id,
                    text=(
                        f"⏰ *19 hours ka access expire ho gaya!*\n\n"
                        f"📌 Channel: *{record['channel_name']}*\n\n"
                        f"🔄 Naya access lene ke liye /start karo aur link generate karo."
                    ),
                    parse_mode="Markdown"
                )
            except Exception:
                pass  # User might have blocked bot

        except Exception as e:
            logger.error(f"Failed to remove user {user_id}: {e}")


# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Scheduler – check every 5 minutes for expired users
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        remove_expired_users,
        "interval",
        minutes=5,
        args=[app],
        next_run_time=datetime.now()
    )
    scheduler.start()

    logger.info("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
