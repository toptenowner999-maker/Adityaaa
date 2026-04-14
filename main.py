from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, ChatJoinRequestHandler
from telegram.error import NetworkError, TimedOut, RetryAfter
import json
import os
import sys
import asyncio
import requests
from io import BytesIO
from datetime import datetime

# Force unbuffered output so logs show instantly
sys.stdout.reconfigure(line_buffering=True)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
APK_URL = os.environ.get("APK_URL")

USERS_FILE = "users.json"

DM_LINK = "https://www.jaiclub31.com/#/register?invitationCode=56175405050"
VIP_BUTTON = InlineKeyboardMarkup([
    [InlineKeyboardButton("REGISTER LINK ❤️✨", url=DM_LINK)]
])

APK_CACHE = None


def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return []


def save_users(users):
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
    except IOError as e:
        print(f"Error saving users: {e}")


def add_user(user, users):
    if not any(u["id"] == user.id for u in users):
        users.append({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "joined_at": datetime.now().isoformat()
        })
        save_users(users)
    return users


def fetch_apk_at_startup():
    global APK_CACHE
    if not APK_URL:
        print("WARNING: APK_URL not set — APK will not be sent.")
        return
    try:
        print(f"Downloading APK from GitHub...")
        response = requests.get(APK_URL, timeout=120)
        response.raise_for_status()
        APK_CACHE = response.content
        print(f"APK cached successfully ({len(APK_CACHE)} bytes)")
    except Exception as e:
        print(f"Failed to download APK: {e}")
        APK_CACHE = None


async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    chat_id = update.chat_join_request.chat.id

    for attempt in range(3):
        try:
            await context.bot.approve_chat_join_request(chat_id, user.id)
            print(f"Approved: {user.id} (@{user.username})")

            users = load_users()
            add_user(user, users)

            await context.bot.send_message(
                chat_id=user.id,
                text="🚀🔥 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗝𝗔𝗜 𝗖𝗟𝗨𝗕 💎 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗕𝗢𝗧 🔥",
                reply_markup=VIP_BUTTON
            )

            if APK_CACHE:
                apk_file = BytesIO(APK_CACHE)
                apk_file.name = "JAIWIN PREMIUM.APK"
                await context.bot.send_document(
                    chat_id=user.id,
                    document=apk_file,
                    filename="JAIWIN PREMIUM.APK",
                    caption=(
                        "✅ 100% NUMBER HACK 💥\n\n"
                        "( ONLY FOR PREMIUM USERS ⚡️ )\n"
                        "( 100% LOSS RECOVER GUARANTEE ⚡️ )\n\n"
                        "REGISTER LINK - https://www.jaiclub31.com/#/register?invitationCode=56175405050\n"
                        "FOR HELP @ADDI_XO"
                    ),
                    reply_markup=VIP_BUTTON
                )
                print(f"APK sent to: {user.id}")
            else:
                print(f"APK cache empty, not sent to: {user.id}")

            break

        except RetryAfter as e:
            print(f"Rate limited, waiting {e.retry_after}s...")
            await asyncio.sleep(e.retry_after)
        except (NetworkError, TimedOut) as e:
            print(f"Network error attempt {attempt + 1}/3: {e}")
            if attempt < 2:
                await asyncio.sleep(5)
        except Exception as e:
            print(f"Error for {user.id}: {e}")
            break


def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN not set")
        import time
        time.sleep(30)
        return

    print(f"[{datetime.now()}] Starting bot...")
    fetch_apk_at_startup()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(join_request))

    print(f"[{datetime.now()}] Bot running (polling)...")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["chat_join_request"]
    )


if name == "main":
    main()
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("Bot stopped.")
            break
        except Exception as e:
            print(f"[{datetime.now()}] Crashed: {e}")
            print("Restarting in 10s...")
            import time
            time.sleep(10)
