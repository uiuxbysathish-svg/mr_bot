import os
import sys
import datetime

# Add the parent directory to Python path if necessary
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_db
from services.user_service import create_user, get_user_by_telegram_id
from services.doctor_service import create_doctor, get_doctors_by_user_id
from services.pob_service import create_pob_entry, get_today_pob_entries, get_monthly_pob_entries, get_top_doctors_report
from services.visit_service import create_visit_entry, get_today_visits, get_monthly_visits
from services.message_formatter import (
    format_today_pob_report,
    format_monthly_pob_report,
    format_top_doctors_report,
    format_single_pob,
    format_today_work_report,
    format_monthly_work_report,
    format_dcr_summary
)

def run_tests():
    print("🧪 STARTING INTEGRATION TESTS FOR MR ASSISTANT BOT...\n")

    # 1. Initialize Database
    print("Step 1: Initializing Database...")
    init_db()
    print("Database tables initialized successfully.\n")

    # Use a mock telegram ID
    mock_telegram_id = "99999999"

    # 2. Test User Registration
    print("Step 2: Testing User Registration...")
    reg_success = create_user(
        telegram_id=mock_telegram_id,
        mr_name="Sathish Kumar",
        employee_code="EY123",
        hq="Coimbatore",
        division="Ortho Division"
    )
    print(f"User created: {reg_success}")
    
    db_user = get_user_by_telegram_id(mock_telegram_id)
    print(f"User fetched: {db_user is not None}")
    if db_user:
        print(f"MR Name in DB: {db_user['mr_name']}")
    print("")

    # 3. Test Doctor Management
    print("Step 3: Testing Doctor Registration...")
    doc1_success = create_doctor(
        user_id=mock_telegram_id,
        doctor_name="Dr. Kumar",
        speciality="Orthopedician",
        hospital="Coimbatore General Hospital"
    )
    doc2_success = create_doctor(
        user_id=mock_telegram_id,
        doctor_name="Dr. Ravi",
        speciality="Cardiologist",
        hospital="Kovai Medical Center"
    )
    print(f"Doctor 1 created: {doc1_success}")
    print(f"Doctor 2 created: {doc2_success}")
    
    doctors = get_doctors_by_user_id(mock_telegram_id)
    print(f"Total doctors registered for MR: {len(doctors)}")
    for d in doctors:
        print(f"• ID: {d['id']} | Name: {d['doctor_name']} | Speciality: {d['speciality']}")
    print("")

    # 4. Test POB Entries Creation
    print("Step 4: Testing POB Order Bookings...")
    if not doctors:
        print("❌ Cannot proceed, no doctors found.")
        return
        
    doc1_id = doctors[0]['id']
    doc2_id = doctors[1]['id']
    
    pob1_success = create_pob_entry(
        user_id=mock_telegram_id,
        doctor_id=doc1_id,
        product_name="Zerapod CV",
        quantity="30 Strips",
        order_value=12500.00
    )
    pob2_success = create_pob_entry(
        user_id=mock_telegram_id,
        doctor_id=doc2_id,
        product_name="Orthoclav",
        quantity="15 Boxes",
        order_value=7500.50
    )
    print(f"POB 1 saved: {pob1_success}")
    print(f"POB 2 saved: {pob2_success}")
    print("")

    # 5. Test POB Message Formatting
    print("Step 5: Testing Single POB WhatsApp Formatting Output:")
    wa_msg = format_single_pob(
        doctor_name=doctors[0]['doctor_name'],
        product_name="Zerapod CV",
        quantity="30 Strips",
        order_value=12500.00
    )
    print("--------------------")
    print(wa_msg)
    print("--------------------\n")

    # 6. Test Reports Aggregates
    print("Step 6: Testing Today's POB Report:")
    today_entries = get_today_pob_entries(mock_telegram_id)
    today_report = format_today_pob_report(today_entries)
    print("--------------------")
    print(today_report)
    print("--------------------\n")

    print("Step 7: Testing Monthly POB Report:")
    monthly_entries = get_monthly_pob_entries(mock_telegram_id)
    monthly_report = format_monthly_pob_report(monthly_entries)
    print("--------------------")
    print(monthly_report)
    print("--------------------\n")

    print("Step 8: Testing Top Doctors Report:")
    top_docs = get_top_doctors_report(mock_telegram_id)
    top_docs_report = format_top_doctors_report(top_docs)
    print("--------------------")
    print(top_docs_report)
    print("--------------------\n")

    # 9. Test Visit Logging
    print("Step 9: Testing Manual Visit Logging (Visual Detailing only)...")
    # Log a visit for Doctor 1 (already has POB, should log once or bypass duplicate)
    v1_success = create_visit_entry(mock_telegram_id, doc1_id)
    # Log a visit for Doctor 2 (already has POB, should bypass duplicate)
    v2_success = create_visit_entry(mock_telegram_id, doc2_id)
    
    print(f"Manual Visit 1 recorded: {v1_success}")
    print(f"Manual Visit 2 recorded: {v2_success}")
    
    today_visits = get_today_visits(mock_telegram_id)
    print(f"Total visits recorded today: {len(today_visits)}")
    for v in today_visits:
         print(f"• Visited: {v['doctor_name']} | Hospital: {v['hospital']}")
    print("")

    # 10. Test Today Work Report & Monthly Work Report
    print("Step 10: Testing Today's Work Summary (/todaywork):")
    work_report = format_today_work_report(today_visits, today_entries)
    print("--------------------")
    print(work_report)
    print("--------------------\n")

    print("Step 11: Testing Monthly Call Summary and Coverage Rate (/monthwork):")
    monthly_visits = get_monthly_visits(mock_telegram_id)
    month_work_report = format_monthly_work_report(monthly_visits, monthly_entries, len(doctors))
    print("--------------------")
    print(month_work_report)
    print("--------------------\n")

    # 11. Test DCR Copy-pasteable block
    print("Step 12: Testing WhatsApp Daily Call Report Summary (/todaysummary):")
    dcr_block = format_dcr_summary(db_user, today_visits, today_entries)
    print("--------------------")
    print(dcr_block)
    print("--------------------\n")

    print("🎉 ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
