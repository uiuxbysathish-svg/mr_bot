from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from services.doctor_service import get_doctors_by_user_id, get_doctor_by_id
from services.visit_service import create_visit_entry
from utils.helpers import registered_only

# Conversation State
VISIT_DOCTOR = 0

@registered_only
async def visit_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Starts the visit logging flow. Presents a list of registered doctors.
    """
    user_id = str(update.effective_user.id)
    doctors = get_doctors_by_user_id(user_id)
    
    if not doctors:
        await update.message.reply_text(
            "⚠️ *No doctors registered yet.*\n\n"
            "Please register at least one doctor using /adddoctor before logging visits.",
            parse_mode="Markdown"
        )
        return ConversationHandler.END
        
    keyboard = []
    for doc in doctors:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{doc['doctor_name']} ({doc['speciality']})",
                callback_data=f"logvis_{doc['id']}"
            )
        ])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📝 *Record Doctor Visit*\n\n"
        "Select the doctor you visited today:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return VISIT_DOCTOR

async def receive_visit_doctor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Logs the doctor visit in the database."""
    query = update.callback_query
    await query.answer()
    
    doctor_id = int(query.data.replace("logvis_", ""))
    doc_details = get_doctor_by_id(doctor_id)
    
    if not doc_details:
        await query.edit_message_text("❌ Selected doctor could not be found.")
        return ConversationHandler.END
        
    user_id = str(update.effective_user.id)
    
    # Save call/visit
    success = create_visit_entry(user_id, doctor_id)
    
    if success:
        import datetime
        date_str = datetime.datetime.now().strftime("%d/%m/%Y")
        await query.edit_message_text(
            text=(
                f"Doctor Visit Logged Successfully ✅\n\n"
                f"👨⚕️ Visited: {doc_details['doctor_name']}\n"
                f"🏥 Hospital: {doc_details['hospital']}\n"
                f"📅 Date: {date_str}"
            ),
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_text("❌ Failed to record visit or visit already recorded for today.")
        
    return ConversationHandler.END

async def cancel_visit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the visit flow."""
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text("❌ Visit logging cancelled.")
    else:
        await update.message.reply_text("❌ Visit logging cancelled.")
    return ConversationHandler.END

def get_visit_handler() -> ConversationHandler:
    """Returns the visit ConversationHandler structure."""
    return ConversationHandler(
        entry_points=[CommandHandler("visit", visit_start)],
        states={
            VISIT_DOCTOR: [CallbackQueryHandler(receive_visit_doctor, pattern="^logvis_")],
        },
        fallbacks=[CommandHandler("cancel", cancel_visit)],
    )
