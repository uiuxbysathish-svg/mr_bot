from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from services.doctor_service import get_doctors_by_user_id, get_doctor_by_id
from services.pob_service import create_pob_entry
from services.message_formatter import format_single_pob
from utils.validators import validate_order_value, validate_non_empty
from utils.helpers import registered_only

# Conversation states
POB_DOCTOR, POB_PRODUCT, POB_QTY, POB_VALUE = range(4)

@registered_only
async def pob_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Initiates the POB booking flow. Lists available doctors for selection.
    """
    user_id = str(update.effective_user.id)
    doctors = get_doctors_by_user_id(user_id)
    
    if not doctors:
        await update.message.reply_text(
            "⚠️ *No doctors registered yet.*\n\n"
            "You must register at least one doctor before booking POB orders.\n"
            "Please use the /adddoctor command to add doctors.",
            parse_mode="Markdown"
        )
        return ConversationHandler.END
        
    # Build inline buttons for doctor selection
    keyboard = []
    for doc in doctors:
        # Callback data stores the doctor ID
        keyboard.append([
            InlineKeyboardButton(
                text=f"{doc['doctor_name']} ({doc['speciality']})",
                callback_data=f"pobdoc_{doc['id']}"
            )
        ])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🏥 *Book POB Order*\n\n"
        "Select a doctor from the list below:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return POB_DOCTOR

async def receive_doctor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives selected doctor ID via inline click, asks for product name."""
    query = update.callback_query
    await query.answer()
    
    doctor_id = int(query.data.replace("pobdoc_", ""))
    doc_details = get_doctor_by_id(doctor_id)
    
    if not doc_details:
        await query.edit_message_text("❌ Selected doctor profile could not be found. Try /pob again.")
        return ConversationHandler.END
        
    context.user_data['pob_doctor_id'] = doctor_id
    context.user_data['pob_doctor_name'] = doc_details['doctor_name']
    
    await query.edit_message_text(
        text=f"Doctor: *{doc_details['doctor_name']}* ✅\n\n"
             f"Please enter the *Product Name*:\n"
             f"_(e.g., Zerapod CV, Orthoclav, Paracetamol)_",
        parse_mode="Markdown"
    )
    return POB_PRODUCT

async def receive_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives product name, asks for quantity."""
    product = update.message.text.strip()
    is_valid, error_msg = validate_non_empty(product, "Product Name")
    
    if not is_valid:
        await update.message.reply_text(f"⚠️ {error_msg}")
        return POB_PRODUCT
        
    context.user_data['pob_product'] = product
    await update.message.reply_text(
        f"Product: *{product}* ✅\n\n"
        f"Enter the *Quantity*:\n"
        f"_(e.g., 30 Strips, 10 Boxes, 50 Bottles)_"
    )
    return POB_QTY

async def receive_qty(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives quantity, asks for order value."""
    qty = update.message.text.strip()
    is_valid, error_msg = validate_non_empty(qty, "Quantity")
    
    if not is_valid:
        await update.message.reply_text(f"⚠️ {error_msg}")
        return POB_QTY
        
    context.user_data['pob_qty'] = qty
    await update.message.reply_text(
        f"Quantity: *{qty}* ✅\n\n"
        f"Enter the *Order Value* (numbers only, in ₹):\n"
        f"_(e.g., 12500)_"
    )
    return POB_VALUE

async def receive_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives order value, saves the POB entry, and returns WhatsApp copyable receipt."""
    value_text = update.message.text.strip()
    is_valid, result = validate_order_value(value_text)
    
    if not is_valid:
        # result is the error message
        await update.message.reply_text(f"⚠️ {result}")
        return POB_VALUE
        
    order_value = result
    user_id = str(update.effective_user.id)
    
    doctor_id = context.user_data.get('pob_doctor_id')
    doctor_name = context.user_data.get('pob_doctor_name')
    product = context.user_data.get('pob_product')
    qty = context.user_data.get('pob_qty')
    
    success = create_pob_entry(
        user_id=user_id,
        doctor_id=doctor_id,
        product_name=product,
        quantity=qty,
        order_value=order_value
    )
    
    if success:
        # Generate WhatsApp optimized message
        wa_message = format_single_pob(
            doctor_name=doctor_name,
            product_name=product,
            quantity=qty,
            order_value=order_value
        )
        
        # We present the user with a confirmation, and then a copyable version
        await update.message.reply_text("POB Saved Successfully ✅")
        
        # Send copyable block
        await update.message.reply_text(
            "👇 Copyable POB Receipt (Tap text inside the block to copy):\n\n"
            f"`{wa_message}`",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "❌ An error occurred while saving the POB order to the database."
        )
        
    # Clean workspace context
    context.user_data.pop('pob_doctor_id', None)
    context.user_data.pop('pob_doctor_name', None)
    context.user_data.pop('pob_product', None)
    context.user_data.pop('pob_qty', None)
    
    return ConversationHandler.END

async def cancel_pob(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the POB flow."""
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text("❌ POB entry cancelled.")
    else:
        await update.message.reply_text("❌ POB entry cancelled.")
    return ConversationHandler.END

def get_pob_handler() -> ConversationHandler:
    """Returns the POB ConversationHandler structure."""
    return ConversationHandler(
        entry_points=[CommandHandler("pob", pob_start)],
        states={
            POB_DOCTOR: [CallbackQueryHandler(receive_doctor, pattern="^pobdoc_")],
            POB_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_product)],
            POB_QTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_qty)],
            POB_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_value)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_pob),
            # In case they select a doctor click but click cancel or issue command
            CallbackQueryHandler(cancel_pob, pattern="^cancel_pob$")
        ],
    )
