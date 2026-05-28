from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from services.user_service import get_user_by_telegram_id, create_user

# Conversation states
REG_NAME, REG_EMP_CODE, REG_HQ, REG_DIVISION = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Initial point for /start command.
    Checks user registry or starts registration flow.
    """
    user = update.effective_user
    telegram_id = str(user.id)
    
    db_user = get_user_by_telegram_id(telegram_id)
    
    if db_user:
        mr_name = db_user['mr_name']
        await update.message.reply_text(
            f"Welcome back, *{mr_name}* ✅\n\n"
            "You are already registered in the system.\n\n"
            "Here are the available commands:\n"
            "🏥 /adddoctor - Add a new doctor to your territory\n"
            "📝 /visit - Record a doctor call/visit today\n"
            "💊 /pob - Book a Product Order Booking (auto-logs visit)\n"
            "📅 /todaywork - Today's call report & POB list\n"
            "📈 /monthwork - Monthly calls summary & doctor coverage %\n"
            "📋 /todaysummary - Copy-pasteable Daily Call Report (DCR) block\n"
            "📅 /todaypob - Today's POB value and product breakdown\n"
            "📈 /monthpob - Monthly POB values & aggregates\n"
            "🏆 /topdoctors - View top sales contributing doctors\n"
            "⏰ /reminders - Manage daily alarms & scheduled revisits\n"
            "❓ /help - View beginner-friendly usage guide",
            parse_mode="Markdown"
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "👋 Welcome to the *MR Assistant Bot*!\n\n"
        "To get started, let's set up your profile.\n"
        "Please enter your *Full Name*:"
    )
    return REG_NAME

async def register_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives MR Name, asks for Employee Code."""
    name = update.message.text.strip()
    if not name:
        await update.message.reply_text("Name cannot be empty. Please enter your name:")
        return REG_NAME
        
    context.user_data['reg_name'] = name
    await update.message.reply_text(
        f"Thank you, {name}!\n\n"
        "Now, please enter your *Employee Code*:"
    )
    return REG_EMP_CODE

async def register_emp_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives Employee Code, asks for HQ."""
    emp_code = update.message.text.strip()
    if not emp_code:
        await update.message.reply_text("Employee Code cannot be empty. Please enter your code:")
        return REG_EMP_CODE
        
    context.user_data['reg_emp_code'] = emp_code
    await update.message.reply_text(
        "Got it!\n\n"
        "What is your headquarter (*HQ*) location?\n"
        "_(e.g., Coimbatore, Bangalore, Mumbai)_"
    )
    return REG_HQ

async def register_hq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives HQ, asks for Division."""
    hq = update.message.text.strip()
    if not hq:
        await update.message.reply_text("HQ location cannot be empty. Please enter your HQ:")
        return REG_HQ
        
    context.user_data['reg_hq'] = hq
    await update.message.reply_text(
        "Perfect!\n\n"
        "Finally, what is your *Division*?\n"
        "_(e.g., Ortho Division, Cardio Division, General Medicine)_"
    )
    return REG_DIVISION

async def register_division(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives Division, stores all values in the database, and ends registration."""
    division = update.message.text.strip()
    if not division:
        await update.message.reply_text("Division cannot be empty. Please enter your Division:")
        return REG_DIVISION
        
    user = update.effective_user
    telegram_id = str(user.id)
    
    mr_name = context.user_data.get('reg_name')
    emp_code = context.user_data.get('reg_emp_code')
    hq = context.user_data.get('reg_hq')
    
    success = create_user(
        telegram_id=telegram_id,
        mr_name=mr_name,
        employee_code=emp_code,
        hq=hq,
        division=division
    )
    
    if success:
        await update.message.reply_text(
            "Registration Completed Successfully ✅\n\n"
            f"👤 *Profile Details:*\n"
            f"• *Name:* {mr_name}\n"
            f"• *Emp Code:* {emp_code}\n"
            f"• *HQ:* {hq}\n"
            f"• *Division:* {division}\n\n"
            "You are all set! Use /adddoctor to register doctors or /pob to record sales booking.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "❌ An error occurred during database registration. Please try again with /start."
        )
        
    # Clear temp cache keys
    context.user_data.pop('reg_name', None)
    context.user_data.pop('reg_emp_code', None)
    context.user_data.pop('reg_hq', None)
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the registration flow."""
    await update.message.reply_text(
        "❌ Registration cancelled. You can type /start when you are ready to complete registration."
    )
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Displays the bot user manual and help guide.
    """
    await update.message.reply_text(
        "❓ *MR Assistant Bot - Help Guide*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "This bot acts as a smart pocket CRM for Pharmaceutical Medical Representatives (MRs).\n\n"
        "*Available Commands:*\n"
        "🏁 /start - Register your profile or display greeting\n"
        "🏥 /adddoctor - Add a new doctor (Name, Specialty, Hospital)\n"
        "📝 /visit - Record a doctor visit/call today\n"
        "💊 /pob - Book a Product Order Booking (POB)\n"
        "📅 /todaywork - Detailed report of doctor calls and bookings logged today\n"
        "📈 /monthwork - Monthly summary of calls and doctor coverage rate %\n"
        "📋 /todaysummary - Monospace Daily Call Report (DCR) ready-to-forward\n"
        "📅 /todaypob - Today's total sales booked and product breakdown\n"
        "📈 /monthpob - Monthly sales totals & averages\n"
        "🏆 /topdoctors - View top sales contributing doctors\n"
        "⏰ /reminders - Manage daily alarms & scheduled revisits\n"
        "📅 /setrevisit - Schedule a reminder to revisit a doctor\n"
        "❌ /cancel - Abort any active conversational form\n\n"
        "*Pro Tips:*\n"
        "• First add doctors using `/adddoctor`.\n"
        "• Tap the code block in the `/pob` receipt message on your phone to copy it instantly. You can then forward it to stockists or WhatsApp groups easily.",
        parse_mode="Markdown"
    )

def get_registration_handler() -> ConversationHandler:
    """Returns the registration ConversationHandler structure."""
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            REG_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_name)],
            REG_EMP_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_emp_code)],
            REG_HQ: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_hq)],
            REG_DIVISION: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_division)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

