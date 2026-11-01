# Supported medication checks

- `verify_medication.py`: regression tests with isolated data and SMTP blocked.
- `smoke_medication.py`: full dashboard, sample reminders, adapter routing and screenshots.
- `verify_medication_bundle.py`: compare compiled debug bundle with sources; verify timezone data and absence of fall modules and profiles.

Scripts containing `fall` or `hfd` in their names, and `capture_verification_screenshots.py`, are historical tooling. They do not validate the current application. Their paths are retained for historical references; old UI capture scripts require the historical dashboard. Use `smoke_medication.py` for current screenshots.

Build instructions: `../HUONG_DAN_DONG_GOI_WINDOWS.md`.
