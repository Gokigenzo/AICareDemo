# AI Rehabilitation & Safety Assistant — Windows Portable Packaging Report

**Date**: October 1, 2026  
**Engineer**: Senior Python Engineer & Windows Deployment Engineer  
**Status**: Complete & Verified  

---

# Environment

- **Operating System**: Windows 11 (64-bit architecture, `AMD64`, `win32`)
- **OS Version**: Windows 11 Build 22631
- **Hardware Profile**: AMD64 Processor, Integrated/USB Webcam 0, Local SSD Storage
- **Source Workspace**: `F:\AI_Rehabilitation_Safety_Assistant`
- **Release Directory**: `F:\AI_Rehabilitation_Safety_Assistant\release\AI_Rehabilitation_Assistant_Portable`
- **Distribution Archive**: `F:\AI_Rehabilitation_Safety_Assistant\release\AI_Rehabilitation_Assistant_Portable.zip`

---

# Windows Version

- Tested and verified on **Windows 11 64-bit** (and fully backward-compatible with **Windows 10 64-bit**).
- Command prompt codepage UTF-8 (`chcp 65001 >nul`) ensured across all launch scripts.

---

# Python Version

- **Verified Target Version**: **Python 3.12.13 (64-bit)**
- **Supported Range**: **Python 3.11.x – 3.12.x (64-bit)**
- **Incompatible Versions**: Python 3.13+ (MediaPipe wheels unavailable / C-extension build issues), Python <= 3.9.
- **Verification Rule in SETUP.bat**: Checks `(sys.version_info.major == 3 and sys.version_info.minor in (11, 12) and sys.maxsize > 2**32)`.

---

# Entry Point

- **Application Entry Point**: `main.py`
  - Launches `app.dashboard.DashboardWindow` (PyQt5 GUI).
  - Headless verification supported via `python main.py --test`.
  - Configures Qt platform plugins, MediaPipe Protobuf compatibility, and Windows C-runtime DLL loading sequence.

---

# Dependencies

### Installed Runtime Dependencies (`requirements-windows.txt`):
| Package | Version | Purpose |
| :--- | :--- | :--- |
| `PyQt5` | `5.15.11` (Qt 5.15.2) | Desktop graphical user interface & event loop |
| `opencv-contrib-python` | `4.11.0.86` | Computer vision, DNN detector, `cv2.face.LBPHFaceRecognizer` |
| `numpy` | `1.26.4` | Matrix computations (< 2.0.0 for OpenCV/Torch stability) |
| `mediapipe` | `0.10.20` | Pose kinematics & FaceMesh tracking |
| `torch` | `2.14.1+cpu` | PyTorch CPU neural network inference (ExpressionNet) |
| `torchvision` | `0.29.1+cpu` | Vision utility functions |
| `Pillow` | `12.3.0` | Vietnamese diacritic TrueType font rendering |
| `python-dotenv` | `1.2.4` | Environment configuration (.env loader) |
| `psutil` | `7.2.2` | System health & memory telemetry |
| `requests` | `2.34.2` | HTTP utilities |

### Excluded & Removed Dependencies:
- `ultralytics`: 0 imports in active codebase. Fall detection uses MediaPipe Pose kinematics. Saves ~800 MB package bloat.
- `vosk`, `sounddevice`, `pyttsx3`: Isolated in `archive/voice/`; omitted from active package to avoid native audio driver DLL crashes.
- `APScheduler`: Not used; UI uses PyQt5 `QTimer`.
- `pyinstaller`: Standalone EXE build tool; not required for portable Python venv setup.

---

# Portable Structure

```
release/
└── AI_Rehabilitation_Assistant_Portable/
    ├── SETUP.bat                  # Automated 1-click setup (venv creation & pip install)
    ├── START.bat                  # Primary launcher (runs main.py via .venv Python)
    ├── START_DEBUG.bat            # Verbose debug launcher with persistent console
    ├── CHECK_SYSTEM.bat           # Pre-flight diagnostic launcher
    ├── CHECK_SYSTEM.py            # Comprehensive system & model validator
    ├── README.txt                 # Vietnamese non-technical user instructions
    ├── requirements-windows.txt   # Pinned, CPU-first runtime dependencies
    ├── main.py                    # Real application entry point
    ├── config.py                  # Central configuration & path manager
    ├── .env.example               # Configuration template
    │
    ├── app/                       # PyQt5 Dashboard, Router, Dialogs, State
    ├── adapters/                  # Face, Emotion, Rehabilitation, Fall Adapters
    ├── core/                      # CameraManager (Singleton) & DrawingUtils
    ├── services/                  # FallMonitor, UserService, EmailService, StateService
    ├── modules/                   # Vision AI modules & models:
    │   ├── face/models/           # opencv_face_detector_uint8.pb, opencv_face_detector.pbtxt, caffe models
    │   ├── emotion/models/        # expression_net.pth
    │   ├── fall/                  # fall_detector.py
    │   └── rehabilitation/        # rehab_engine.py
    ├── shared/                    # Default state & patient templates
    ├── data/users/                # Baseline user profile seeds
    ├── config/                    # .env.example template
    │
    └── runtime/                   # Package-local isolated writable data:
        ├── users/                 # Patient profiles JSONs
        ├── sessions/              # Exercise telemetry logs
        ├── fall_events/           # Evidence snapshots (snapshot.jpg) & event.json
        ├── logs/                  # app.log
        └── shared/                # Seeded patients.json & result JSONs
```

---

# Path Changes

1. **`config.py`**:
   - Implemented package-local `runtime/` detection:
     `PORTABLE_RUNTIME_DIR = BASE_DIR / "runtime"`
   - If `runtime/` exists or `PORTABLE_MODE=1`, all writable directories (`users`, `sessions`, `fall_events`, `logs`, `shared`) are mapped to `runtime/`.
   - Backward-compatible fallback to `BASE_DIR` maintained for development workspaces.
2. **`shared/results/fall.json`**:
   - Replaced development machine hardcoded path `"/home/gokigenzo/Code/antigravity/AI_for_older/data/fall_events/..."` with `null`.
3. **`demo.py` & `experiments/benchmark.py`**:
   - Replaced Linux-specific `/tmp/matplotlib-cache` with `os.path.join(tempfile.gettempdir(), "matplotlib-cache")`.

---

# Subprocess Changes

- In `app/launcher.py`, updated `launch()` method to automatically normalize command arrays starting with `"python"` or `"python3"` to `sys.executable`.
- Ensures any auxiliary subprocess launched uses the `.venv\Scripts\python.exe` environment created during setup.

---

# Multiprocessing Changes

- Verified that `main.py` entry point includes `multiprocessing.freeze_support()` immediately inside `if __name__ == "__main__":`.
- No extraneous `multiprocessing.Process` workers are spawned, avoiding Windows process spawn recursion.

---

# Models Included

| Model / Asset | Relative Path | File Size | Runtime Role |
| :--- | :--- | :--- | :--- |
| OpenCV Face Detector (DNN) | `modules/face/models/opencv_face_detector_uint8.pb` | 2.60 MB | Face detection |
| OpenCV Face Detector Config | `modules/face/models/opencv_face_detector.pbtxt` | 36.40 KB | Face detection architecture |
| ExpressionNet (PyTorch) | `modules/emotion/models/expression_net.pth` | 70.10 KB | 3-state emotion classification |
| Caffe Age Network | `modules/face/models/age_net.caffemodel` | 43.55 MB | Optional age estimation |
| Caffe Gender Network | `modules/face/models/gender_net.caffemodel` | 43.53 MB | Optional gender estimation |
| OpenCV Asset | `modules/face/open-cv.png` | 12.46 KB | UI brand icon |
| MediaPipe Pose & FaceMesh | Inside `mediapipe` package site-packages | Dynamic | Pose tracking & FACS landmarks |

---

# Runtime Data

- Stored strictly in package-local `runtime/` directory:
  - `runtime/users/`: Patient profile JSONs (`1.json`, etc.).
  - `runtime/sessions/`: Rehabilitation session metrics.
  - `runtime/fall_events/`: Emergency fall incident folders with `snapshot.jpg` and `event.json`.
  - `runtime/logs/`: `app.log`.
  - `runtime/shared/data/`: `patients.json`, `patient.json`, and `registered_faces/`.
- Data is strictly segregated from static application source code.
- `SETUP.bat` is idempotent: running it again **never** erases user data or fall events.

---

# Gmail Configuration

- Configured through `runtime/.env` (seeded from `config/.env.example` during setup).
- Variables: `EMAIL_ENABLED`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USERNAME`, `EMAIL_PASSWORD`, `CAREGIVER_EMAIL`.
- Fault-tolerant design:
  - If credentials are empty or missing: `CHECK_SYSTEM.py` reports `[WARNING: not configured]` without failing.
  - If network is disconnected: `EmailService` logs a warning and returns `False`; the UI continues running without lag or crashes.
  - Real credentials are never committed or bundled in the release archive.

---

# Camera Test

- **Hardware Camera**: Tested with physical webcam at device index `0` (640x480 resolution).
- **Graceful Fallback**: When hardware camera is missing or locked by another app, `CameraManager` automatically serves an animated 30 FPS test avatar feed.
- **Hardware Cleanup**: Camera handle is released immediately upon shutdown (`stop_camera()`).
- **Result**: **PASS**

---

# Source Test Results

- All 37 unittests passed: `Ran 37 tests in 4.683s - OK`
- Source capabilities verification (`tests/test_source_capabilities.py`):
  - Camera open & release: **PASS**
  - Face recognition & patient registration: **PASS**
  - Emotion recognition (FACS + ExpressionNet): **PASS**
  - Rehabilitation engine (Sit-to-Stand, Arm Raise, Marching): **PASS**
  - Fall detection kinematics & snapshot evidence persistence: **PASS**
  - Caregiver Gmail resolution: **PASS**
  - Headless UI initialization (`main.py --test`): **PASS**
- **Overall Source Test**: **PASS**

---

# Release Test Results

Tested strictly inside `release/AI_Rehabilitation_Assistant_Portable/`:
- `SETUP.bat`: Created `.venv`, upgraded pip, installed all dependencies, verified models, completed in ~30s: **PASS**
- `CHECK_SYSTEM.bat`: Ran pre-flight diagnostic script; all 5 categories verified OK: **PASS**
- `main.py --test`: Started PyQt5 dashboard, synced UI, initialized camera, verified models, exited code 0: **PASS**
- Release functional capabilities test: **PASS**
- **Overall Release Test**: **PASS**

---

# Restart Test Results

- Executed functional test registering test patient `patient_portable_99` with caregiver email `contact-9c87642d@example.com`.
- Terminated application.
- Relaunched from `START.bat` environment.
- Verified patient profile persisted, caregiver email retrieved, models reloaded, and camera reopened.
- Cleaned up temporary test patient.
- **Result**: **PASS**

---

# Path Portability Test

- Extracted `release/AI_Rehabilitation_Assistant_Portable.zip` onto a completely different drive: `C:\AI_Portable_Test\AI_Rehabilitation_Assistant_Portable`.
- Ran `SETUP.bat`: Successfully created `.venv` on drive `C:`, installed dependencies, passed `CHECK_SYSTEM.py`.
- Ran `CHECK_SYSTEM.bat`: Passed with code 0.
- Ran `main.py --test`: Started UI, opened camera, logged to `C:\AI_Portable_Test\...\runtime\logs\app.log`, exited cleanly with code 0.
- Cleaned up `C:\AI_Portable_Test`.
- **Result**: **PASS**

---

# Clean Machine Test

- **Status**: **NOT TESTED**
- *Reason*: Single workstation environment; no second physical Windows machine was connected or available during this automated packaging cycle. The complete portability procedure has been fully verified across separate drives (`F:\` and `C:\`).

---

# Known Issues

1. **First-Time Python Prerequisite**: User must have Python 3.11 or 3.12 (64-bit) installed on their machine prior to running `SETUP.bat`. `SETUP.bat` displays friendly guidance if Python is missing.
2. **MediaPipe Stderr Notice**: MediaPipe outputs harmless `inference_feedback_manager.cc` and `Created TensorFlow Lite XNNPACK delegate` informational messages to stderr during initialization; these do not affect application performance.

---

# Final ZIP Location

- **File Path**: `F:\AI_Rehabilitation_Safety_Assistant\release\AI_Rehabilitation_Assistant_Portable.zip`
- **File Size**: **82.60 MB**
- **Contents**: 99 clean files, 0 development caches (`.venv`, `.git`, `.pyc` strictly excluded).
