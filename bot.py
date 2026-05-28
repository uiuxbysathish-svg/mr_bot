import sys
from telegram.ext import ApplicationBuilder, CommandHandler
from config import TELEGRAM_BOT_TOKEN
from database import init_db

# Import Handlers
from handlers.start_handler import get_registration_handler, help_command
from handlers.doctor_handler import get_doctor_handler
from handlers.pob_handler import get_pob_handler
from handlers.visit_handler import get_visit_handler
from handlers.report_handler import get_report_handlers
from handlers.reminder_handler import get_reminder_handlers

def main():
    # 1. Check if token is configured
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE" or not TELEGRAM_BOT_TOKEN:
        print("⚠️ ERROR: TELEGRAM_BOT_TOKEN is not configured in the .env file!")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("Please follow these steps:")
        print("1. Open the .env file in the project folder.")
        print("2. Replace 'YOUR_TELEGRAM_BOT_TOKEN_HERE' with your real Telegram Bot Token.")
        print("3. Obtain a token from @BotFather on Telegram if you haven't already.")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        sys.exit(1)

    print("🚀 Initializing SQLite database...")
    init_db()
    print("✅ Database tables verified/created successfully.")

    print("🤖 Building Telegram Bot Application...")
    # Build python-telegram-bot application
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # 2. Register Conversation Handlers (Registration, Doctor, POB)
    # Registration Flow (triggered by /start)
    application.add_handler(get_registration_handler())
    
    # Doctor Addition Flow (triggered by /adddoctor)
    application.add_handler(get_doctor_handler())
    
    # POB entry Flow (triggered by /pob)
    application.add_handler(get_pob_handler())
    
    # Doctor visit Flow (triggered by /visit)
    application.add_handler(get_visit_handler())
    
    # 3. Register Command Handlers
    # Help guide Command
    application.add_handler(CommandHandler("help", help_command))
    
    # Reports Command handlers (/todaypob, /monthpob, /topdoctors)
    for handler in get_report_handlers():
        application.add_handler(handler)
        
    # Reminder Command & Callback handlers (/reminders, /setrevisit)
    for handler in get_reminder_handlers():
        application.add_handler(handler)

    import os
    PORT = int(os.environ.get("PORT", "8000"))
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

    if WEBHOOK_URL:
        print(f"📡 Webhook mode: Listening on port {PORT}, URL path 'webhook'...")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path="webhook",
            webhook_url=f"{WEBHOOK_URL}/webhook"
        )
    else:
        print("🔌 Polling mode: Starting long polling...")
        application.run_polling()

if __name__ == "__main__":
    main()
