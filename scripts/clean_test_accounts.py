"""
Clean Test Accounts Utility for AI Care Assistant Release.
Removes all test accounts for patients, elderly, caregivers, and clinicians.
Keeps only the single system administrator account:
- User ID: user_admin_001
- Email / Username: admin@unifiedcare.local (or admin)
- Full Name: Quản trị viên Hệ thống
- Role: admin
- Default Password: admin123
"""

from __future__ import annotations

import json
import logging
import shutil
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CleanAccounts")


def clean_test_accounts() -> None:
    # 1. Clean JSON files and registered faces across both shared/ and runtime/shared/
    shared_dirs = [
        REPO_ROOT / "shared" / "data",
        REPO_ROOT / "runtime" / "shared" / "data",
    ]

    for s_dir in shared_dirs:
        if not s_dir.exists():
            continue

        p_file = s_dir / "patients.json"
        with open(p_file, "w", encoding="utf-8") as f:
            f.write("{}\n")
        logger.info("Reset %s to empty object {}", p_file)

        single_p = s_dir / "patient.json"
        if single_p.exists():
            single_p.unlink()
            logger.info("Removed %s", single_p)

        faces_dir = s_dir / "registered_faces"
        if faces_dir.exists():
            for sub in faces_dir.iterdir():
                if sub.is_dir():
                    shutil.rmtree(sub, ignore_errors=True)
                    logger.info("Removed registered face samples directory: %s", sub)
            (faces_dir / ".gitkeep").touch()

    # Clean user profile JSONs in data/users and runtime/users
    for u_dir in [REPO_ROOT / "data" / "users", REPO_ROOT / "runtime" / "users"]:
        if u_dir.exists():
            for j in u_dir.glob("*.json"):
                j.unlink()
                logger.info("Removed %s", j)

    # 2. Clean SQLite databases
    db_paths = [
        REPO_ROOT / "data" / "unified_care.sqlite3",
        REPO_ROOT / "runtime" / "unified_care.sqlite3",
    ]

    for db_p in db_paths:
        if not db_p.exists():
            continue

        conn = sqlite3.connect(db_p)
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = OFF;")

        # Delete all non-admin users
        cur.execute("DELETE FROM users WHERE user_id != 'user_admin_001' AND role != 'admin';")

        # Ensure default administrator exists
        cur.execute(
            """
            INSERT INTO users (user_id, email, phone, full_name, password_hash, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                full_name=excluded.full_name,
                role='admin',
                is_active=1
            """,
            (
                "user_admin_001",
                "admin@unifiedcare.local",
                "0900000000",
                "Quản trị viên Hệ thống",
                "pbkdf2:admin123",
                "admin",
                1,
                "2026-01-01T00:00:00Z",
            ),
        )

        tables_to_clear = [
            "patients",
            "caregivers",
            "clinicians",
            "patient_caregivers",
            "care_team",
            "legacy_patient_map",
            "rehab_plans",
            "rehab_sessions",
            "rehab_events",
            "caregiver_reports",
            "report_messages",
            "care_recommendations",
            "mood_checkins",
            "emotion_inferences",
            "emergency_contacts",
            "emergency_contact_events",
            "measurement_requests",
            "prescriptions",
            "prescription_items",
            "medication_schedules",
            "dose_occurrences",
            "dose_events",
            "alerts",
            "notification_deliveries",
            "health_observations",
            "symptom_entries",
            "clinician_reviews",
            "clinical_messages",
            "game_sessions",
            "game_results",
        ]

        for tbl in tables_to_clear:
            try:
                cur.execute(f"DELETE FROM {tbl};")
            except Exception:
                pass

        conn.commit()
        cur.execute("PRAGMA foreign_keys = ON;")
        cur.execute("VACUUM;")
        conn.close()
        logger.info("Purged test accounts from %s (Admin account retained).", db_p.name)

    logger.info("Successfully cleaned all test accounts. ONLY administrator account retained.")


if __name__ == "__main__":
    clean_test_accounts()
