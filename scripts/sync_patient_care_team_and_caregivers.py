#!/usr/bin/env python3
"""
Synchronize care team (doctor) and caregivers for all patients in unified_care.sqlite3.
Ensures elderly patients are properly bound with their doctor and caregiver emails
so that voice/click requests successfully reach both recipients.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "unified_care.sqlite3"


def sync_database(db_path=DB_PATH):
    print(f"[*] Synchronizing database: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Ensure patients are ACTIVE
    patient_ids = ["patient_001", "patient_002", "patient_test_999"]
    for pid in patient_ids:
        cur.execute("UPDATE patients SET status = 'ACTIVE' WHERE patient_id = ?", (pid,))
        print(f"  [+] Patient {pid}: status set to ACTIVE")

    # 2. Identify primary doctor (clinician)
    doc_row = cur.execute(
        """SELECT c.clinician_id, u.user_id, u.email, u.full_name
           FROM clinicians c JOIN users u ON c.user_id=u.user_id
           WHERE u.email = 'contact-22dad1d8@example.com' OR u.full_name LIKE '%bac sy%'
           ORDER BY c.clinician_id LIMIT 1"""
    ).fetchone()
    if not doc_row:
        # Fallback to any active clinician
        doc_row = cur.execute(
            """SELECT c.clinician_id, u.user_id, u.email, u.full_name
               FROM clinicians c JOIN users u ON c.user_id=u.user_id
               WHERE u.is_active=1 ORDER BY c.clinician_id LIMIT 1"""
        ).fetchone()

    if not doc_row:
        print("  [!] Error: No clinician found in database!")
        conn.close()
        return False

    clinician_id = doc_row["clinician_id"]
    print(f"  [+] Identified doctor: {doc_row['full_name']} ({doc_row['email']}, ID: {clinician_id})")

    # 3. Identify caregivers
    # Primary: nguyen van b (contact-9e2e85e7@example.com)
    cg1_row = cur.execute(
        """SELECT c.caregiver_id, u.user_id, u.email, u.full_name, u.phone
           FROM caregivers c JOIN users u ON c.user_id=u.user_id
           WHERE u.email = 'contact-9e2e85e7@example.com' OR u.full_name LIKE '%nguyen van b%'
           ORDER BY c.caregiver_id LIMIT 1"""
    ).fetchone()

    # Secondary: Hiu Caregiver (contact-927f84f8@example.com)
    cg2_row = cur.execute(
        """SELECT c.caregiver_id, u.user_id, u.email, u.full_name, u.phone
           FROM caregivers c JOIN users u ON c.user_id=u.user_id
           WHERE u.email = 'contact-927f84f8@example.com' OR u.full_name LIKE '%Hiu%'
           ORDER BY c.caregiver_id LIMIT 1"""
    ).fetchone()

    if not cg1_row:
        print("  [!] Error: Primary caregiver not found!")
        conn.close()
        return False

    print(f"  [+] Identified primary caregiver: {cg1_row['full_name']} ({cg1_row['email']}, ID: {cg1_row['caregiver_id']})")
    if cg2_row:
        print(f"  [+] Identified secondary caregiver: {cg2_row['full_name']} ({cg2_row['email']}, ID: {cg2_row['caregiver_id']})")

    # 4. Synchronize care_team for each patient
    valid_from = "2024-01-01T00:00:00+00:00"
    valid_to = "2099-12-31T23:59:59+00:00"

    for pid in patient_ids:
        cur.execute(
            """INSERT INTO care_team (care_team_id, patient_id, clinician_id, role_description, valid_from, valid_to, consent_status, is_active)
               VALUES (?, ?, ?, 'Bác sĩ điều trị phụ trách', ?, ?, 'GRANTED', 1)
               ON CONFLICT(patient_id, clinician_id) DO UPDATE SET
                   role_description = 'Bác sĩ điều trị phụ trách',
                   consent_status = 'GRANTED',
                   is_active = 1,
                   valid_from = excluded.valid_from,
                   valid_to = excluded.valid_to""",
            (f"ct_{pid}_{clinician_id}", pid, clinician_id, valid_from, valid_to)
        )
        print(f"  [+] care_team synced for {pid} -> Doctor {doc_row['full_name']}")

    # 5. Synchronize patient_caregivers for each patient
    for pid in patient_ids:
        # Primary caregiver (cg1)
        cur.execute(
            """INSERT INTO patient_caregivers (patient_caregiver_id, patient_id, caregiver_id, relationship_type,
                                              is_primary, notification_priority, can_edit_schedule, can_view_health,
                                              consent_status, valid_from, valid_to, is_active)
               VALUES (?, ?, ?, 'Con cái', 1, 1, 1, 1, 'GRANTED', ?, ?, 1)
               ON CONFLICT(patient_id, caregiver_id) DO UPDATE SET
                   is_primary = 1,
                   notification_priority = 1,
                   consent_status = 'GRANTED',
                   is_active = 1,
                   valid_from = excluded.valid_from,
                   valid_to = excluded.valid_to""",
            (f"pc_{pid}_{cg1_row['caregiver_id']}", pid, cg1_row["caregiver_id"], valid_from, valid_to)
        )

        # Secondary caregiver (cg2) if available
        if cg2_row:
            cur.execute(
                """INSERT INTO patient_caregivers (patient_caregiver_id, patient_id, caregiver_id, relationship_type,
                                                  is_primary, notification_priority, can_edit_schedule, can_view_health,
                                                  consent_status, valid_from, valid_to, is_active)
                   VALUES (?, ?, ?, 'Người thân', 0, 2, 1, 1, 'GRANTED', ?, ?, 1)
                   ON CONFLICT(patient_id, caregiver_id) DO UPDATE SET
                       is_primary = 0,
                       notification_priority = 2,
                       consent_status = 'GRANTED',
                       is_active = 1,
                       valid_from = excluded.valid_from,
                       valid_to = excluded.valid_to""",
                (f"pc_{pid}_{cg2_row['caregiver_id']}", pid, cg2_row["caregiver_id"], valid_from, valid_to)
            )
        print(f"  [+] patient_caregivers synced for {pid} -> Primary: {cg1_row['full_name']} (Priority 1)" +
              (f", Secondary: {cg2_row['full_name']} (Priority 2)" if cg2_row else ""))

    # 6. Synchronize emergency_contacts for manual fallback calls
    for pid in patient_ids:
        contacts = [
            (f"ec_{pid}_doc", pid, "clinician_on_duty", f"BS. {doc_row['full_name']}", "13423423423", "00:00", "23:59", 1, 1, 1, "Bác sĩ phụ trách"),
            (f"ec_{pid}_cg1", pid, "caregiver_primary", cg1_row["full_name"], cg1_row["phone"] or "03423424324", "00:00", "23:59", 1, 1, 2, "Người chăm sóc chính"),
            (f"ec_{pid}_115", pid, "local_emergency", "Cấp cứu y tế Quốc gia 115", "115", "00:00", "23:59", 1, 1, 3, "Đường dây nóng cấp cứu 115")
        ]
        for ec in contacts:
            cur.execute(
                """INSERT INTO emergency_contacts (contact_id, patient_id, contact_type, contact_name, phone,
                                                  on_duty_start, on_duty_end, is_verified, is_active, priority, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(contact_id) DO UPDATE SET
                       phone = excluded.phone,
                       is_verified = 1,
                       is_active = 1""",
                ec
            )
        print(f"  [+] emergency_contacts synced for {pid}")

    conn.commit()
    conn.close()
    print("[*] Synchronization completed successfully!")
    return True


if __name__ == "__main__":
    db_file = sys.argv[1] if len(sys.argv) > 1 else DB_PATH
    success = sync_database(db_file)
    sys.exit(0 if success else 1)

