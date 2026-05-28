import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from database import get_db_connection
from services.doctor_service import get_doctors_by_user_id, get_doctor_by_id
from utils.helpers import registered_only

# Conversation states for setting a reminder
REM_DOC, REM_DAYS = range(2)

def init_reminders_table():
    """Dynamically creates the reminders table if it does not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        doctor_id INTEGER NOT NULL,
        reminder_date TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(telegram_id) ON DELETE CASCADE,
        FOREIGN KEY(doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
    );
    """)
    conn.commit()
    conn.close()

# Initialize the table
init_reminders_table()

# Helper DB services for Reminders
def add_revisit_reminder(user_id, doctor_id, days):
    """Saves a revisit reminder in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    success = False
    
    now = datetime.datetime.now()
    rem_date = (now + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    created_at = now.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cursor.execute(
            """
            INSERT INTO reminders (user_id, doctor_id, reminder_date, status, created_at)
            VALUES (?, ?, ?, 'pending', ?)
            """,
            (str(user_id), doctor_id, rem_date, created_at)
        )
        conn.commit()
        success = True
    except Exception as e:
        print(f"Error saving reminder: {e}")
    finally:
        conn.close()
    return success, rem_date

def get_pending_reminders(user_id):
    """Retrieves all pending reminders for the user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT r.*, d.doctor_name, d.hospital
        FROM reminders r
        JOIN doctors d ON r.doctor_id = d.id
        WHERE r.user_id = ? AND r.status = 'pending'
        ORDER BY r.reminder_date ASC
        """,
        (str(user_id),)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Command Handlers & Conversation functions
@registered_only
async def reminders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the main reminders dashboard."""
    user_id = str(update.effective_user.id)
    pending = get_pending_reminders(user_id)
    
    # Format pending list
    if pending:
        items = []
        for r in pending:
            # Parse date for presentation
            dt = datetime.datetime.strptime(r['reminder_date'], "%Y-%m-%d")
            formatted_date = dt.strftime("%d %b %Y")
            items.append(f"• *Dr. {r['doctor_name']}* ({r['hospital']}) - Revisit on {formatted_date}")
        revisit_list_text = "\n".join(items)
    else:
        revisit_list_text = "No pending doctor revisit reminders."

    keyboard = [
        [
            InlineKeyboardButton("📅 Schedule Revisit", callback_data="rem_schedule"),
            InlineKeyboardButton("🔔 Setup Daily Alarm", callback_data="rem_daily")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"⏰ *Reminders Dashboard*\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"*Doctor Revisit Schedule:*\n"
        f"{revisit_list_text}\n\n"
        f"Choose an option below to configure reminders:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_dashboard_clicks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles clicks from the reminders dashboard inline buttons."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(update.effective_user.id)
    
    if query.data == "rem_schedule":
        # Redirect user to type Command or start conversation
        await query.edit_message_text(
            "To schedule a doctor revisit reminder, type:\n"
            "*/setrevisit*\n\n"
            "This will start the scheduling helper.",
            parse_mode="Markdown"
        )
    elif query.data == "rem_daily":
        # Toggle / setup daily evening POB reminder
        job_name = f"daily_pob_{user_id}"
        current_jobs = context.job_queue.get_jobs_by_name(job_name) if context.job_queue else []
        
        if current_jobs:
            # Cancel job
            for job in current_jobs:
                job.schedule_removal()
            await query.edit_message_text(
                "🔕 *Daily POB submission reminder has been turned OFF.*",
                parse_mode="Markdown"
            )
        else:
            if not context.job_queue:
                await query.edit_message_text(
                    "⚠️ JobQueue is not initialized on this bot instance. Cannot set daily alarm."
                )
                return
                
            # Schedule daily at 20:00 (8:00 PM) local time
            # For demonstration, setting a daily job at 20:00
            target_time = datetime.time(hour=20, minute=0, second=0)
            
            async def daily_reminder_job(job_context):
                await job_context.bot.send_message(
                    chat_id=job_context.job.chat_id,
                    text="⏰ *Daily POB Reminder*\n\n"
                         "Did you visit any doctors today? Don't forget to record your Product Order Bookings (POBs).\n\n"
                         "Type /pob to log an order now.",
                    parse_mode="Markdown"
                )
                
            context.job_queue.run_daily(
                daily_reminder_job,
                time=target_time,
                name=job_name,
                chat_id=update.effective_chat.id
            )
            
            await query.edit_message_text(
                "🔔 *Daily POB submission reminder has been set for 8:00 PM daily.* ✅",
                parse_mode="Markdown"
            )

# Revisit Conversation Flow
@registered_only
async def setrevisit_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the doctor revisit scheduling flow."""
    user_id = str(update.effective_user.id)
    doctors = get_doctors_by_user_id(user_id)
    
    if not doctors:
        await update.message.reply_text(
            "⚠️ *No doctors registered yet.*\n\nPlease use /adddoctor first.",
            parse_mode="Markdown"
        )
        return ConversationHandler.END
        
    keyboard = []
    for doc in doctors:
        keyboard.append([
            InlineKeyboardButton(
                text=f"Dr. {doc['doctor_name']} ({doc['speciality']})",
                callback_data=f"remdoc_{doc['id']}"
            )
        ])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📅 *Set Doctor Revisit Reminder*\n\n"
        "Select a doctor from the list:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return REM_DOC

async def receive_rem_doctor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives selected doctor for reminder, asks for time interval."""
    query = update.callback_query
    await query.answer()
    
    doctor_id = int(query.data.replace("remdoc_", ""))
    doc_details = get_doctor_by_id(doctor_id)
    
    if not doc_details:
        await query.edit_message_text("❌ Selected doctor could not be found.")
        return ConversationHandler.END
        
    context.user_data['rem_doctor_id'] = doctor_id
    context.user_data['rem_doctor_name'] = doc_details['doctor_name']
    
    # Preset intervals: 3 days, 7 days, 14 days, 30 days
    keyboard = [
        [
            InlineKeyboardButton("3 Days", callback_data="remdays_3"),
            InlineKeyboardButton("7 Days", callback_data="remdays_7")
        ],
        [
            InlineKeyboardButton("14 Days (2 Weeks)", callback_data="remdays_14"),
            InlineKeyboardButton("30 Days (1 Month)", callback_data="remdays_30")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=f"Doctor: *{doc_details['doctor_name']}* ✅\n\n"
             f"Select when you would like to revisit this doctor:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return REM_DAYS

async def receive_rem_days(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Calculates revisit date, stores reminder and notifies user."""
    query = update.callback_query
    await query.answer()
    
    days = int(query.data.replace("remdays_", ""))
    user_id = str(update.effective_user.id)
    doctor_id = context.user_data.get('rem_doctor_id')
    doctor_name = context.user_data.get('rem_doctor_name')
    
    success, rem_date = add_revisit_reminder(user_id, doctor_id, days)
    
    if success:
        dt = datetime.datetime.strptime(rem_date, "%Y-%m-%d")
        formatted_date = dt.strftime("%d %b %Y")
        
        await query.edit_message_text(
            text=f"✅ *Revisit Scheduled!*\n\n"
                 f"We will remind you to visit *Dr. {doctor_name}* on *{formatted_date}* ({days} days from now).",
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_text("❌ Failed to schedule reminder in database.")
        
    # Clear cache
    context.user_data.pop('rem_doctor_id', None)
    context.user_data.pop('rem_doctor_name', None)
    
    return ConversationHandler.END

async def cancel_rem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the reminder configuration."""
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text("❌ Reminder setting cancelled.")
    else:
        await update.message.reply_text("❌ Reminder setting cancelled.")
    return ConversationHandler.END

def get_reminder_handlers():
    """Returns reminder command handlers and conversation handlers."""
    revisit_conv = ConversationHandler(
        entry_points=[CommandHandler("setrevisit", setrevisit_start)],
        states={
            REM_DOC: [CallbackQueryHandler(receive_rem_doctor, pattern="^remdoc_")],
            REM_DAYS: [CallbackQueryHandler(receive_rem_days, pattern="^remdays_")],
        },
        fallbacks=[CommandHandler("cancel", cancel_rem)]
    )
    
    return [
        CommandHandler("reminders", reminders_menu),
        CallbackQueryHandler(handle_dashboard_clicks, pattern="^rem_"),
        revisit_conv
    ]
