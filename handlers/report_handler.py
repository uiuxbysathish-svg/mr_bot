from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from services.pob_service import (
    get_today_pob_entries,
    get_monthly_pob_entries,
    get_top_doctors_report
)
from services.visit_service import (
    get_today_visits,
    get_monthly_visits
)
from services.doctor_service import get_doctors_by_user_id
from services.message_formatter import (
    format_today_pob_report,
    format_monthly_pob_report,
    format_top_doctors_report,
    format_today_work_report,
    format_monthly_work_report,
    format_dcr_summary
)
from utils.helpers import registered_only

@registered_only
async def today_pob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fetches and displays today's POB booking report.
    """
    user_id = str(update.effective_user.id)
    entries = get_today_pob_entries(user_id)
    report_text = format_today_pob_report(entries)
    
    await update.message.reply_text(report_text, parse_mode="Markdown")

@registered_only
async def month_pob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fetches and displays the current month's POB aggregate report.
    """
    user_id = str(update.effective_user.id)
    entries = get_monthly_pob_entries(user_id)
    report_text = format_monthly_pob_report(entries)
    
    await update.message.reply_text(report_text, parse_mode="Markdown")

@registered_only
async def top_doctors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fetches and displays the top order-generating doctors for this MR.
    """
    user_id = str(update.effective_user.id)
    top_docs = get_top_doctors_report(user_id)
    report_text = format_top_doctors_report(top_docs)
    
    await update.message.reply_text(report_text, parse_mode="Markdown")

@registered_only
async def today_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Displays the summary of doctor visits and POB bookings completed today.
    """
    user_id = str(update.effective_user.id)
    visits = get_today_visits(user_id)
    pob_entries = get_today_pob_entries(user_id)
    
    report_text = format_today_work_report(visits, pob_entries)
    await update.message.reply_text(report_text, parse_mode="Markdown")

@registered_only
async def month_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Displays monthly call averages, POB totals, and doctor coverage rate metrics.
    """
    user_id = str(update.effective_user.id)
    visits = get_monthly_visits(user_id)
    pob_entries = get_monthly_pob_entries(user_id)
    
    doctors = get_doctors_by_user_id(user_id)
    total_registered_docs = len(doctors)
    
    report_text = format_monthly_work_report(visits, pob_entries, total_registered_docs)
    await update.message.reply_text(report_text, parse_mode="Markdown")

@registered_only
async def today_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Formats the Daily Call Report (DCR) ready-to-forward message.
    Outputs as a monospace block to support copy-on-tap on mobile.
    """
    user_id = str(update.effective_user.id)
    db_user = context.user_data.get('db_user', {})
    
    visits = get_today_visits(user_id)
    pob_entries = get_today_pob_entries(user_id)
    
    dcr_text = format_dcr_summary(db_user, visits, pob_entries)
    
    await update.message.reply_text(
        "👇 Monospace DCR Summary (Tap inside the block to copy):\n\n"
        f"`{dcr_text}`",
        parse_mode="Markdown"
    )

def get_report_handlers():
    """Returns report command handlers list."""
    return [
        CommandHandler("todaypob", today_pob),
        CommandHandler("monthpob", month_pob),
        CommandHandler("topdoctors", top_doctors),
        CommandHandler("todaywork", today_work),
        CommandHandler("monthwork", month_work),
        CommandHandler("todaysummary", today_summary)
    ]

