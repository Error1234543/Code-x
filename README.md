# 🤖 NEET Access Bot – Setup Guide

## Files
```
bot.py          → Main bot (commands, buttons, auto-remove)
database.py     → SQLite database (users & access tracking)
vplink_api.py   → vplink.in URL shortener integration
requirements.txt
render.yaml     → Render.com deployment config
.env.example    → Environment variables template
```

---

## Step 1 – Bot Token lao (@BotFather se)
1. Telegram pe `/newbot` @BotFather ko bhejo
2. Bot ka naam aur username do
3. Token copy karo → `BOT_TOKEN`

---

## Step 2 – Bot ko Channel Admin banao
Dono channels me bot ko **Admin** banao aur ye permissions do:
- ✅ Invite Users via Link
- ✅ Remove Members
- ✅ Ban Users

---

## Step 3 – Channel IDs lao
1. Koi bhi message apne channel se forward karo [@userinfobot](https://t.me/userinfobot) ko
2. Woh Channel ID dega (negative number jaise `-1001234567890`)

---

## Step 4 – VPLink API Key
1. [https://vplink.in](https://vplink.in) pe login karo
2. API section me apna token copy karo → `VPLINK_API_KEY`

---

## Step 5 – Render pe Deploy

### Option A – GitHub se (Recommended)
1. Saari files GitHub repo me push karo
2. [render.com](https://render.com) pe jaao → New → Blueprint
3. Apna repo connect karo
4. Environment variables set karo (Dashboard → Environment):
   - `BOT_TOKEN`
   - `VPLINK_API_KEY`
   - `CHANNEL_1_ID`
   - `CHANNEL_2_ID`

### Option B – Manual
1. Render pe New → Background Worker
2. Build command: `pip install -r requirements.txt`
3. Start command: `python bot.py`
4. Env vars add karo

---

## Bot Flow (User Experience)

```
User: /start
Bot:  Welcome message + 2 buttons

User: [NEET Batch 1 – Link Generate Karo] tap karta hai
Bot:  "Link generate ho raha hai..."
      → Telegram invite link create (2 min expiry, 1 member)
      → VPLink se shorten
      → User ko link bheja

      19 hours baad:
      → Bot user ko channel se remove karta hai (auto)
      → User ko notification bhejta hai
      → User phir /start se naya link le sakta hai
```

---

## Local Testing
```bash
cp .env.example .env
# .env file me apni values bharo

pip install -r requirements.txt
python bot.py
```
