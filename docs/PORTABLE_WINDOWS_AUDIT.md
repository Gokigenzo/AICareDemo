# AI Rehabilitation & Safety Assistant — Windows Portable Packaging Audit

**Date**: October 1, 2026  
**Auditor**: Senior Python Desktop Application & Windows Deployment Engineer  
**Document Status**: Official Phase 0 Audit Document  

---

# Current Project State

- **Application Name**: AI Rehabilitation & Safety Assistant (AI Care)
- **Target Platform**: Windows 10 / Windows 11 (64-bit Architecture, `AMD64`, `win32`)
- **Repository Location**: `F:\AI_Rehabilitation_Safety_Assistant`
- **Git Branch**: `windows-packaging`
- **Execution Architecture**: In-process multi-threaded desktop application with PyQt5 GUI, OpenCV DNN, MediaPipe Pose/FaceMesh, and PyTorch inference pipelines.
- **Packaging Goal**: Portable Auto-Setup Package (`.zip` containing `SETUP.bat`, `START.bat`, `CHECK_SYSTEM.bat`, application code, models, assets, and config templates). No EXE / PyInstaller bundling.

---

# Application Entry Point

- **Primary Entry Point**: `main.py`
  - Sets critical environment variables:
    - `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` (prevents MediaPipe protobuf descriptor collision)
    - `MPLCONFIGDIR=%TEMP%\matplotlib-cache`
  - Pre-initializes `mediapipe` and `torch` before Qt import to prevent Windows C-runtime DLL loading conflicts (WinError 1114).
  - Configures Qt platform plugin library paths.
  - Instantiates `QApplication` and attaches modern dark stylesheet (`STYLESHEET`).
  - Launches `DashboardWindow` (`app.dashboard.DashboardWindow`).
  - Supports `--test` headless validation flag for automated pre-flight testing and CI/CD verification.
- **Application Lifespan**: Clean shutdown releases camera hardware and closes log handlers gracefully.

---

# Python Version

- **Verified Target Python Runtime**: **Python 3.12 (64-bit)** (specifically verified on CPython 3.12.13).
- **Supported Python Range**: **Python 3.11 – 3.12 (64-bit)**.
- **Incompatible Versions**:
  - Python 3.13+: MediaPipe does not provide stable official Windows wheels; C-extension build failures.
  - Python 3.14+: Unsupported pre-release; broken binary wheel compatibility.
  - Python <= 3.9: End-of-life; unsupported by current OpenCV and MediaPipe releases.
- **Bitness Requirement**: Strict 64-bit (`AMD64`) required by MediaPipe, PyTorch, and OpenCV Contrib.
- **SETUP.bat Requirement**: Must validate Python availability and ensure major=3 and minor in {11, 12}. Must abort safely if an incompatible version is detected.

---

# Runtime Modules

1. **Face Recognition & Enrollment** (`adapters/face_adapter.py`, `app/registration_dialog.py`):
   - OpenCV DNN face detector (`opencv_face_detector_uint8.pb`, `opencv_face_detector.pbtxt`) with Haar Cascade fallback.
   - Local Binary Patterns Histograms (`cv2.face.LBPHFaceRecognizer`) with CLAHE illumination normalization and bilateral filtering.
   - Real-time patient identification and webcam-based registration workflow.
2. **Emotion Recognition** (`adapters/emotion_adapter.py`):
   - MediaPipe FaceMesh biometric Facial Action Coding System (FACS) action units (AU12 smile, AU15/AU1/4 frown).
   - PyTorch ExpressionNet (`expression_net.pth`) neural network inference.
   - 3 focused states: *Bình thường (Neutral)*, *Vui vẻ (Happy)*, *Buồn bã (Sad)* with temporal smoothing queue.
3. **Rehabilitation Exercise Engine** (`adapters/rehabilitation_adapter.py`, `modules/rehabilitation/rehab_engine.py`):
   - MediaPipe Pose landmark extraction and biomechanical joint angle computation.
   - Finite State Machine (FSM) repetition counter, posture validation, form penalty deduction, and telemetry HUD for 3 exercises:
     - Sit-to-Stand (*Co duỗi chân / Đứng lên ngồi xuống*)
     - Arm Raise (*Vươn vai / Nâng tay qua đầu*)
     - Marching (*Đi bộ tại chỗ / Nâng cao đùi*)
4. **Fall Detection & Safety Monitoring** (`adapters/fall_adapter.py`, `modules/fall/fall_detector.py`, `services/fall_monitor.py`):
   - Real-time posture kinematics (torso vertical inclination angle, bounding box aspect ratio, vertical hip displacement velocity).
   - Multi-stage Temporal Verification FSM:
     `NORMAL -> SUSPECTED -> CONFIRMING -> FALL_CONFIRMED -> COOLDOWN -> NORMAL`.
   - Automatic snapshot capture (`snapshot.jpg`) and event logging (`event.json`).
   - Dispatches emergency alert to registered Caregiver Gmail.
5. **Camera Subsystem** (`core/camera_manager.py`):
   - Thread-safe Singleton `CameraManager` (inherits `QThread`).
   - Unified frame capture loop serving Face, Emotion, Rehab, and Fall pipelines simultaneously without handle contention.
   - Automatic fallback to animated synthetic test feed if hardware webcam is unavailable or in use.
6. **User Profile & Caregiver Service** (`services/user_service.py`):
   - Local JSON storage for patient metadata, medical notes, and caregiver emergency contact details.
   - Email format validation via regex.
7. **Email Alert Service** (`services/email_service.py`):
   - Fault-tolerant SMTP client over TLS (port 587) using Python standard `smtplib`.
   - Sends HTML notification with JPEG evidence attachment.
   - Network failure or missing credentials produce non-blocking warnings without crashing the UI.
8. **UI & Rendering Engine** (`app/dashboard.py`, `core/drawing_utils.py`):
   - PyQt5 dark GUI dashboard.
   - High-contrast Vietnamese diacritic HUD rendering using Pillow and Windows system TrueType fonts (`arialbd.ttf`, `segoeuib.ttf`).

---

# Dependencies

### Active Runtime Dependencies:
- `PyQt5 >= 5.15.10`
- `opencv-contrib-python >= 4.8.0.76` (includes `cv2.face` module)
- `numpy >= 1.24.0, < 2.0.0` (pinned to 1.26.4 for maximum stability across OpenCV/MediaPipe/Torch)
- `mediapipe >= 0.10.14, <= 0.10.20`
- `torch >= 2.0.0` (CPU wheel)
- `torchvision >= 0.15.0`
- `Pillow >= 10.0.0`
- `python-dotenv >= 1.0.0`
- `psutil >= 5.9.0`
- `requests >= 2.31.0`

### Obsolete Dependencies Excluded from Portable Package:
- `ultralytics`: 0 imports in active codebase. Fall detection uses MediaPipe Pose kinematics. Saves ~800MB.
- `vosk`, `sounddevice`, `pyttsx3`: Voice module isolated in `archive/voice/`; not referenced by active runtime. Eliminates native audio driver issues and audio DLL crashes.
- `APScheduler`: Not used; active UI timer uses PyQt5 `QTimer`.
- `pyinstaller`: Only used for building standalone EXE; unnecessary for portable Python venv setup.

---

# Models

| Model File | Path | Size | Module | Required at Runtime | Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `opencv_face_detector_uint8.pb` | `modules/face/models/` | 2.60 MB | `FaceAdapter` | Yes | Include in release |
| `opencv_face_detector.pbtxt` | `modules/face/models/` | 36.40 KB | `FaceAdapter` | Yes | Include in release |
| `expression_net.pth` | `modules/emotion/models/` | 70.10 KB | `EmotionAdapter` | Yes | Include in release |
| `age_deploy.prototxt` | `modules/face/models/` | 2.42 KB | `FaceAdapter` (optional) | Optional | Include in release |
| `age_net.caffemodel` | `modules/face/models/` | 43.55 MB | `FaceAdapter` (optional) | Optional | Include in release |
| `gender_deploy.prototxt` | `modules/face/models/` | 2.42 KB | `FaceAdapter` (optional) | Optional | Include in release |
| `gender_net.caffemodel` | `modules/face/models/` | 43.53 MB | `FaceAdapter` (optional) | Optional | Include in release |
| MediaPipe Pose / FaceMesh | Bundled in `mediapipe` package | Dynamic | Fall, Rehab, Emotion | Yes | Installed via pip |

---

# Assets

- `modules/face/open-cv.png` (12.7 KB): OpenCV logo asset.
- Fonts: Uses Windows system TrueType fonts (`%WINDIR%\Fonts\arialbd.ttf`, `segoeuib.ttf`, `tahoma.ttf`). Fully abstracted in `core/drawing_utils.py` with default fallback.

---

# Runtime Data

Portable release strictly separates static application code from writable runtime data:
```
runtime/
├── users/               # Patient JSON profiles (e.g. 1.json)
├── sessions/            # Rehabilitation session exercise logs
├── fall_events/         # Fall evidence snapshots (snapshot.jpg) & event.json
├── logs/                # app.log
└── shared/
    ├── data/            # patients.json, patient.json, registered_faces/
    └── results/         # face.json, emotion.json, rehabilitation.json, fall.json
```
- Centralized path resolution in `config.py` automatically detects and creates `runtime/` directories on startup.
- Setup script will never wipe user data, logs, or fall events.

---

# Gmail Configuration

- Configured through package-local `.env` file (copied from `config/.env.example` during setup if not present).
- Configuration variables:
  - `EMAIL_ENABLED=true` / `false`
  - `EMAIL_HOST=smtp.gmail.com`
  - `EMAIL_PORT=587`
  - `EMAIL_USERNAME=` (System sender Gmail)
  - `EMAIL_PASSWORD=` (Google App Password)
  - `CAREGIVER_EMAIL=` (Default recipient caregiver Gmail)
- Safety rules:
  - Missing or blank credentials result in `[WARNING: not configured]` during check, but do not prevent the app from launching.
  - No internet connection logs a warning during an alert event without interrupting UI or video processing.
  - Real credentials are never committed to git or bundled in release archives.

---

# Camera

- Abstracted by `core.camera_manager.CameraManager`.
- Primary backend: `cv2.VideoCapture(CAMERA_INDEX)`.
- If camera is absent, disabled, or locked by another application:
  - Logs warning: `Hardware camera not found at index 0. Running in Simulation Mode.`
  - Generates animated test frames smoothly at 30 FPS.
  - Completely prevents crashes or hanging threads.
- Proper hardware release on window close (`stop_camera()`).

---

# Subprocess Usage

- Active runtime modules (Face, Emotion, Rehab, Fall, UI) do **not** use subprocesses; they execute in-process within Qt threads.
- Auxiliary script `app/launcher.py` contains `subprocess.Popen` for testing isolated commands, which resolves Python using `config.PYTHON_EXE` (`sys.executable` / `.venv/Scripts/python.exe`).
- All execution is verified to use `sys.executable`.

---

# Multiprocessing Usage

- No separate `multiprocessing.Process` workers are spawned.
- `main.py` includes `multiprocessing.freeze_support()` at entry point to guard against process recursion on Windows spawn semantics.

---

# Hard-coded Paths

- Identified:
  1. `shared/results/fall.json`: contains stale Linux path `/home/gokigenzo/Code/antigravity/AI_for_older/...`.
     *Resolution*: Clean `shared/results/fall.json` to use relative/portable structure.
  2. `demo.py`, `experiments/benchmark.py`: `/tmp/matplotlib-cache`.
     *Resolution*: Standardize to `tempfile.gettempdir()`.
- Verified: All production pathing in `config.py`, `adapters/`, `services/`, and `modules/` is based on relative `Path(__file__).resolve().parent` and `pathlib.Path`. No machine-specific drive letters (`C:\Users\USER\...`) are hardcoded.

---

# Linux-Specific Code

- No shell scripts (`.sh`), `bash`, `sudo`, `apt`, or `python3` invocations in active application execution.
- All OS platform checks use `sys.platform == "win32"` and standard Windows batch / PowerShell equivalents.

---

# Windows-Specific Risks

1. **App Execution Alias**: Windows default PATH may point to WindowsApps `python.exe` (stub that opens Microsoft Store) instead of actual installed Python.
   *Mitigation*: `SETUP.bat` explicitly searches for Python using multiple discovery methods (`where python`, `py -3.12`, `py -3.11`, standard `C:\Python312`, `%LOCALAPPDATA%\Programs\Python\Python312`, etc.) and tests `-c "import sys"` to verify execution.
2. **MediaPipe / Torch OpenMP DLL collision (WinError 1114)**:
   *Mitigation*: Pre-importing `mediapipe` and `torch` in `config.py` and `main.py` before PyQt5 initialization eliminates this collision entirely.
3. **Protobuf Collisions**:
   *Mitigation*: Setting `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` in environment at startup.
4. **Console UTF-8 Encoding**:
   *Mitigation*: Windows command prompt codepage configured via `chcp 65001 >nul` and Python stdout reconfigured to UTF-8.

---

# Obsolete Dependencies

- Excluded: `ultralytics`, `vosk`, `sounddevice`, `pyttsx3`, `APScheduler`, `pyinstaller`.
- Preserved: All modules required for Face, Emotion, Rehabilitation, Fall Detection, User Registration, Caregiver Email, Camera, and PyQt5 Dashboard.

---

# Required Minimal Changes

1. **`config.py`**: Ensure runtime directory structure resolves cleanly to `runtime/` when available or relative root.
2. **`requirements-windows.txt`**: Clean, pinned dependencies excluding unneeded packages.
3. **`shared/results/fall.json`**: Reset stale development snapshot path.
4. **`demo.py`**: Update `MPLCONFIGDIR` to use `tempfile.gettempdir()`.
5. **`CHECK_SYSTEM.py`**: Diagnostic pre-flight check script.
6. **`CHECK_SYSTEM.bat`**: User-facing launcher for diagnostics.
7. **`SETUP.bat`**: Automated one-click setup script for Windows.
8. **`START.bat`**: Application launcher using `.venv\Scripts\python.exe`.
9. **`START_DEBUG.bat`**: Console-enabled debug launcher.
10. **`README.txt`**: User-friendly Vietnamese instructions.
11. **`packaging/portable/BUILD_PORTABLE.bat`**: Clean packaging script to construct `release/AI_Rehabilitation_Assistant_Portable/` and `.zip`.

---

# Portable Packaging Plan

- **Step 1**: Finalize and verify minimal code adjustments (`config.py`, `requirements-windows.txt`).
- **Step 2**: Re-verify unit tests and `--test` suite from source.
- **Step 3**: Develop `CHECK_SYSTEM.py`, `CHECK_SYSTEM.bat`, `SETUP.bat`, `START.bat`, `START_DEBUG.bat`, `README.txt`.
- **Step 4**: Develop automated release builder `packaging/portable/BUILD_PORTABLE.bat`.
- **Step 5**: Execute build script to create `release/AI_Rehabilitation_Assistant_Portable/`.
- **Step 6**: Test `SETUP.bat`, `CHECK_SYSTEM.bat`, `START.bat` inside the release directory.
- **Step 7**: Test path portability (relocate package to another directory and verify execution).
- **Step 8**: Create final distribution archive `AI_Rehabilitation_Assistant_Portable.zip`.
- **Step 9**: Generate comprehensive report `docs/PORTABLE_WINDOWS_REPORT.md`.

