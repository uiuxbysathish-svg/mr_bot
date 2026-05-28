from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from services.doctor_service import create_doctor
from utils.helpers import registered_only

# Conversation states
DOC_NAME, DOC_SPECIALITY, DOC_HOSPITAL = range(3)

@registered_only
async def add_doctor_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Starts the doctor addition flow.
    """
    await update.message.reply_text(
        "🏥 *Add New Doctor Profile*\n\n"
        "Please enter the *Doctor's Name*:\n"
        "_(e.g., Dr. Kumar or Dr. Priya Sharma)_"
    )
    return DOC_NAME

async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives doctor name, asks for speciality with inline choices."""
    name = update.message.text.strip()
    if not name:
        await update.message.reply_text("Name cannot be empty. Please enter the doctor's name:")
        return DOC_NAME
        
    # Ensure it starts with Dr. if not already there, for professional formatting
    if not name.lower().startswith("dr.") and not name.lower().startswith("dr "):
        name = "Dr. " + name
        
    context.user_data['doc_name'] = name
    
    # Inline buttons for quick selection
    keyboard = [
        [
            InlineKeyboardButton("General Physician", callback_data="spec_General Physician"),
            InlineKeyboardButton("Orthopedician", callback_data="spec_Orthopedician")
        ],
        [
            InlineKeyboardButton("Cardiologist", callback_data="spec_Cardiologist"),
            InlineKeyboardButton("Pediatrician", callback_data="spec_Pediatrician")
        ],
        [
            InlineKeyboardButton("Gynecologist", callback_data="spec_Gynecologist"),
            InlineKeyboardButton("Dermatologist", callback_data="spec_Dermatologist")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Selected Name: *{name}*\n\n"
        "Select the doctor's *Speciality* using buttons below, or type a custom one:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return DOC_SPECIALITY

async def receive_speciality_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives speciality via Inline Keyboard click, asks for Hospital."""
    query = update.callback_query
    await query.answer()
    
    # Extract specialty from callback data (remove "spec_" prefix)
    speciality = query.data.replace("spec_", "")
    context.user_data['doc_speciality'] = speciality
    
    # Edit the text to reflect selection and prompt for next step
    await query.edit_message_text(
        text=f"Selected Speciality: *{speciality}* ✅\n\n"
             f"Now, enter the *Hospital / Clinic Name*:",
        parse_mode="Markdown"
    )
    return DOC_HOSPITAL

async def receive_speciality_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives custom speciality via text message, asks for Hospital."""
    speciality = update.message.text.strip()
    if not speciality:
        await update.message.reply_text("Speciality cannot be empty. Please select or type one:")
        return DOC_SPECIALITY
        
    context.user_data['doc_speciality'] = speciality
    await update.message.reply_text(
        f"Selected Speciality: *{speciality}* ✅\n\n"
        f"Now, enter the *Hospital / Clinic Name*:",
        parse_mode="Markdown"
    )
    return DOC_HOSPITAL

async def receive_hospital(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives hospital name, saves doctor to database."""
    hospital = update.message.text.strip()
    if not hospital:
        await update.message.reply_text("Hospital cannot be empty. Please enter the hospital / clinic name:")
        return DOC_HOSPITAL
        
    user = update.effective_user
    user_id = str(user.id)
    
    doc_name = context.user_data.get('doc_name')
    doc_speciality = context.user_data.get('doc_speciality')
    
    success = create_doctor(
        user_id=user_id,
        doctor_name=doc_name,
        speciality=doc_speciality,
        hospital=hospital
    )
    
    if success:
        await update.message.reply_text(
            "Doctor Added Successfully ✅\n\n"
            f"👨‍⚕️ *Profile:*\n"
            f"• *Name:* {doc_name}\n"
            f"• *Speciality:* {doc_speciality}\n"
            f"• *Hospital:* {hospital}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "❌ An error occurred while adding the doctor to the database."
        )
        
    # Clean cache
    context.user_data.pop('doc_name', None)
    context.user_data.pop('doc_speciality', None)
    
    return ConversationHandler.END

async def cancel_doctor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the doctor flow."""
    # Check if this was cancelled from callback query or normal message
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text("❌ Doctor creation cancelled.")
    else:
        await update.message.reply_text("❌ Doctor creation cancelled.")
    return ConversationHandler.END

def get_doctor_handler() -> ConversationHandler:
    """Returns the doctor ConversationHandler structure."""
    return ConversationHandler(
        entry_points=[CommandHandler("adddoctor", add_doctor_start)],
        states={
            DOC_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
            DOC_SPECIALITY: [
                CallbackQueryHandler(receive_speciality_cb, pattern="^spec_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_speciality_text)
            ],
            DOC_HOSPITAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_hospital)],
        },
        fallbacks=[CommandHandler("cancel", cancel_doctor)],
    )
