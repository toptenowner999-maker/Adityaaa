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

# Unbuffered logs
sys.stdout.reconfigure(line_buffering=True)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# APK URL
APK_URL = "https://raw.githubusercontent.com/toptenowner999-maker/Adityaaa/0259af13e130b88a64706d70ff872ba1c86bc3d2/ADITYA%20NUMBER%20PANEL.apk"

USERS_FILE = "users.json"

DM_LINK = "https://yaarwin.org/#/register?invitationCode=67827139232"

VIP_BUTTON = InlineKeyboardMarkup([
    [InlineKeyboardButton("REGISTER LINK ❤️✨", url=DM_LINK)]
])

APK_CACHE = None


def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return []


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def add_user(user, users):
    if not any(u["id"] == user.id for u in users):
        users.append({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "joined_at": datetime.now().isoformat()
        })
        save_users(users)


def fetch_apk_at_startup():
    global APK_CACHE

    try:
        print("Downloading APK...")

        response = requests.get(APK_URL, timeout=120)
        response.raise_for_status()

        APK_CACHE = response.content

        print(f"APK cached successfully ({len(APK_CACHE)} bytes)")

    except Exception as e:
        print(f"APK download failed: {e}")
        APK_CACHE = None


async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.chat_join_request.from_user

    print(f"New join request from {user.id}")

    # Request stays pending
    # No auto approve

    users = load_users()
    add_user(user, users)

    for attempt in range(3):

        try:

            # Welcome DM
            await context.bot.send_message(
                chat_id=user.id,
                text="🚀🔥 WELCOME TO YAARWIN PREMIUM BOT 🔥🚀",
                reply_markup=VIP_BUTTON
            )

            # Send APK
            if APK_CACHE:

                apk_file = BytesIO(APK_CACHE)
                apk_file.name = "ADITYA_NUMBER_PANEL.apk"

                await context.bot.send_document(
                    chat_id=user.id,
                    document=apk_file,
                    filename="ADITYA_NUMBER_PANEL.apk",
                    caption=(
                        "✅ 100% NUMBER PANEL 💥\n\n"
                        "REGISTER LINK:\n"
                        "https://yaarwin.org/#/register?invitationCode=67827139232\n\n"
                        "FOR HELP : @ADDI_XO"
                    ),
                    reply_markup=VIP_BUTTON
                )

                print(f"APK sent to {user.id}")

            else:
                print("APK cache empty")

            break

        except RetryAfter as e:

            print(f"Rate limited: waiting {e.retry_after}s")
            await asyncio.sleep(e.retry_after)

        except (NetworkError, TimedOut) as e:

            print(f"Network error: {e}")

            if attempt < 2:
                await asyncio.sleep(5)

        except Exception as e:

            print(f"Error for {user.id}: {e}")
            break


def main():

    if not BOT_TOKEN:
        print("BOT_TOKEN missing")
        return

    print(f"[{datetime.now()}] Starting bot...")

    fetch_apk_at_startup()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(ChatJoinRequestHandler(join_request))

    print(f"[{datetime.now()}] Bot running...")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["chat_join_request"]
    )


if __name__ == "__main__":

    while True:

        try:
            main()

        except KeyboardInterrupt:
            print("Bot stopped")
            break

        except Exception as e:

            print(f"Crashed: {e}")

            import time
            time.sleep(10)
