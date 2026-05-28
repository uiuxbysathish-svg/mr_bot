import datetime
import pandas as pd

def format_currency(value):
    """Formats numeric value to currency notation with commas, e.g., ₹12,500."""
    try:
        val = float(value)
        return f"₹{val:,.2f}".replace(".00", "")  # removes cents if whole number
    except (ValueError, TypeError):
        return f"₹{value}"

def clean_doctor_name(name):
    """Ensures the doctor name has exactly one 'Dr.' prefix."""
    if not name:
        return ""
    name_str = str(name).strip()
    lower_name = name_str.lower()
    if lower_name.startswith("dr."):
        name_str = name_str[3:].strip()
    elif lower_name.startswith("dr "):
        name_str = name_str[2:].strip()
    return f"Dr. {name_str}"

def format_single_pob(doctor_name, product_name, quantity, order_value, entry_date=None):
    """
    Generates a WhatsApp-optimised copy-pasteable single POB order message.
    """
    formatted_val = format_currency(order_value)
    cleaned_doc = clean_doctor_name(doctor_name)
    return (
        f"🏥 POB ORDER FROM {cleaned_doc}\n\n"
        f"{product_name}  {quantity}\n\n"
        f"Order Value: {formatted_val}"
    )

def format_today_pob_report(entries):
    """
    Formats the summary report of all POB entries logged today.
    """
    if not entries:
        return "⚠️ *No POB orders booked today yet.* Use /pob to book an order."

    total_value = sum(entry['order_value'] for entry in entries)
    
    # Detailed line items
    items_list = []
    for idx, entry in enumerate(entries, 1):
        val_str = format_currency(entry['order_value'])
        cleaned_doc = clean_doctor_name(entry['doctor_name'])
        items_list.append(f"{idx}. *{cleaned_doc}* - {entry['product_name']} ({entry['quantity']}) - {val_str}")
    
    details_text = "\n".join(items_list)

    # Product-wise summary using Pandas
    df = pd.DataFrame(entries)
    # Group by product name and sum order value
    product_summary = df.groupby('product_name').agg(
        total_val=('order_value', 'sum'),
        count=('id', 'count')
    ).reset_index()

    prod_list = []
    for _, row in product_summary.iterrows():
        val_str = format_currency(row['total_val'])
        prod_list.append(f"• {row['product_name']}: {val_str} ({row['count']} orders)")
    
    prod_summary_text = "\n".join(prod_list)

    today_str = datetime.datetime.now().strftime("%d %b %Y")

    return (
        f"📅 *POB Daily Report - {today_str}*\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 *Total POB Value:* {format_currency(total_value)}\n"
        f"📦 *Total Bookings:* {len(entries)}\n\n"
        f"🔍 *Order Details:*\n"
        f"{details_text}\n\n"
        f"📊 *Product-wise Breakdown:*\n"
        f"{prod_summary_text}\n\n"
        f"💡 _Tip: You can forward individual orders to stockists using WhatsApp._"
    )

def format_monthly_pob_report(entries):
    """
    Formats the summary report of all POB entries logged in the current month.
    """
    if not entries:
        return "⚠️ No POB orders booked this month yet."

    total_value = sum(entry['order_value'] for entry in entries)
    df = pd.DataFrame(entries)
    
    # Doctor-wise top contributors
    doctor_contrib = df.groupby('doctor_name')['order_value'].sum().reset_index()
    doctor_contrib = doctor_contrib.sort_values(by='order_value', ascending=False).head(2)
    
    doc_contrib_list = []
    for idx, row in enumerate(doctor_contrib.itertuples(), 1):
        cleaned_doc = clean_doctor_name(row.doctor_name)
        doc_contrib_list.append(f"{idx}. {cleaned_doc} - {format_currency(row.order_value)}")
    doc_contrib_text = "\n".join(doc_contrib_list)

    month_str = datetime.datetime.now().strftime("%B %Y")

    return (
        f"📈 POB Monthly Report - {month_str}\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Total Monthly Value: {format_currency(total_value)}\n"
        f"📦 Total Orders booked: {len(entries)}\n\n"
        f"🏥 Top Doctors contributing this month:\n"
        f"{doc_contrib_text}"
    )

def format_top_doctors_report(top_docs):
    """
    Formats the highest order-generating doctors report.
    """
    if not top_docs:
        return "⚠️ *No POB booking data available to compute top doctors.*"

    rank_list = []
    for idx, doc in enumerate(top_docs, 1):
        val_str = format_currency(doc['total_value'])
        cleaned_doc = clean_doctor_name(doc['doctor_name'])
        rank_list.append(
            f"{idx}. *{cleaned_doc}* ({doc['speciality']})\n"
            f"   🏥 {doc['hospital']}\n"
            f"   💰 Total Sales: {val_str} | 📦 Orders: {doc['total_orders']}\n"
        )
    
    details_text = "\n".join(rank_list)
    
    return (
        f"🏆 *Top Order-Generating Doctors*\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"{details_text}"
    )

def format_today_work_report(visits, pob_entries):
    """
    Formats the detailed summary of visits and order bookings logged today.
    """
    today_str = datetime.datetime.now().strftime("%d %b %Y")
    if not visits:
        return (
            f"📅 *Today's Work Report - {today_str}*\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"⚠️ *No doctor visits logged today yet.*\n"
            f"Use /visit to record doctor visits or /pob to book orders."
        )

    total_pob_value = sum(p['order_value'] for p in pob_entries)
    
    # Map doctor visits to POB bookings for detailed logging
    # Create a quick dict of pob details by doctor ID
    pob_map = {}
    for p in pob_entries:
        doc_id = p['doctor_id']
        if doc_id not in pob_map:
            pob_map[doc_id] = []
        pob_map[doc_id].append(p)

    visit_details = []
    for idx, v in enumerate(visits, 1):
        cleaned_doc = clean_doctor_name(v['doctor_name'])
        doc_text = f"• *{cleaned_doc}* ({v['speciality']}) - {v['hospital']}"
        
        doc_id = v['doctor_id']
        if doc_id in pob_map:
            pob_details_list = []
            for p in pob_map[doc_id]:
                val_str = format_currency(p['order_value'])
                pob_details_list.append(f"  ↳ 💊 POB: {p['product_name']} ({p['quantity']}) - {val_str} ✅")
            pob_text = "\n".join(pob_details_list)
            visit_details.append(f"{doc_text}\n{pob_text}")
        else:
            visit_details.append(f"{doc_text}\n  ↳ 📝 Detailing Only | No POB")

    visit_details_text = "\n\n".join(visit_details)

    return (
        f"📅 *Today's Work Report - {today_str}*\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 *Total Doctor Calls:* {len(visits)}\n"
        f"💰 *Total POB Value:* {format_currency(total_pob_value)}\n\n"
        f"👨‍⚕️ *Visit Activity:*\n"
        f"{visit_details_text}"
    )

def format_monthly_work_report(visits, pob_entries, total_registered_docs):
    """
    Formats the monthly DCR analytics and doctor coverage reports.
    """
    month_str = datetime.datetime.now().strftime("%B %Y")
    if not visits:
        return (
            f"📈 *Monthly Work Report - {month_str}*\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"⚠️ *No work logged this month yet.*"
        )

    total_pob_value = sum(p['order_value'] for p in pob_entries)
    
    # Unique doctor coverage rate
    visited_doc_ids = set(v['doctor_id'] for v in visits)
    unique_visited_count = len(visited_doc_ids)
    
    coverage_pct = 0.0
    if total_registered_docs > 0:
        coverage_pct = (unique_visited_count / total_registered_docs) * 100

    return (
        f"📈 *Monthly Work Report - {month_str}*\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 *Total Calls Logged:* {len(visits)} visits\n"
        f"💊 *Total POB Bookings:* {len(pob_entries)} orders\n"
        f"💰 *Cumulative Monthly POB:* {format_currency(total_pob_value)}\n\n"
        f"🎯 *Doctor Coverage Rate:* {coverage_pct:.1f}%\n"
        f"   _(Visited {unique_visited_count} out of {total_registered_docs} registered doctors)_"
    )

def format_dcr_summary(user_profile, visits, pob_entries):
    """
    Generates a clean copyable text string representing the Daily Call Report (DCR).
    Suitable for pasting to managers or WhatsApp groups.
    """
    bo_name = user_profile.get('mr_name', 'Unknown')
    hq_name = user_profile.get('hq', 'N/A')
    division_name = user_profile.get('division', 'N/A')

    if not visits:
        return (
            f"🏥 *DAILY CALL REPORT (DCR)*\n\n"
            f"👤 * BO Name :* {bo_name}\n"
            f"📍 *HQ:* {hq_name}\n"
            f"📁 *Division:* {division_name}\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"⚠️ No visits logged today."
        )

    # Map POB amounts to doctors
    pob_totals_by_doc = {}
    for p in pob_entries:
        doc_id = p['doctor_id']
        pob_totals_by_doc[doc_id] = pob_totals_by_doc.get(doc_id, 0.0) + p['order_value']

    visit_lines = []
    for idx, v in enumerate(visits, 1):
        cleaned_doc = clean_doctor_name(v['doctor_name'])
        doc_id = v['doctor_id']
        pob_val = pob_totals_by_doc.get(doc_id, 0.0)
        formatted_pob = format_currency(pob_val)
        visit_lines.append(f"{idx}. {cleaned_doc} ({v['speciality']}) - {v['hospital']} [POB: {formatted_pob}]")

    visits_section = "\n".join(visit_lines)
    total_pob_value = sum(p['order_value'] for p in pob_entries)
    formatted_total_pob = format_currency(total_pob_value)

    return (
        f"🏥 *DAILY CALL REPORT (DCR)*\n\n"
        f"👤 * BO Name :* {bo_name}\n"
        f"📍 *HQ:* {hq_name}\n"
        f"📁 *Division:* {division_name}\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"👨⚕️ *Doctors Visited Today:*\n"
        f"{visits_section}\n\n"
        f"💰 *Total POB Value:* {formatted_total_pob}\n\n"
        f"✅ DCR Generated Successfully."
    )

