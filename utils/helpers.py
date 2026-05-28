from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from services.user_service import get_user_by_telegram_id

def registered_only(func):
    """
    Decorator to restrict access to registered Medical Representatives only.
    If the user is not registered, it prompts them to run /start.
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        # Determine user ID depending on message or callback
        user = update.effective_user
        if not user:
            return

        telegram_id = str(user.id)
        db_user = get_user_by_telegram_id(telegram_id)
        
        if not db_user:
            msg = (
                "⚠️ *Access Denied.*\n\n"
                "You are not registered in the system yet.\n"
                "Please type /start to complete your profile registration."
            )
            if update.message:
                await update.message.reply_text(msg, parse_mode="Markdown")
            elif update.callback_query:
                await update.callback_query.answer(text="Registration required.", show_alert=True)
                await update.callback_query.message.reply_text(msg, parse_mode="Markdown")
            return
        
        # Pass the verified db_user to the context for easy access down the line
        context.user_data['db_user'] = db_user
        return await func(update, context, *args, **kwargs)
        
    return wrapper
