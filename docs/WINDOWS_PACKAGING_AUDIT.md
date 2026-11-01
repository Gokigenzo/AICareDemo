# AI Rehabilitation & Safety Assistant — Windows Packaging Audit
**Date**: September 30, 2026  
**Auditor**: Senior Python Desktop Application & Windows Deployment Engineer  
**Document Status**: Official Phase 0 Audit Document  

---

## 1. Current Environment
- **Operating System**: Windows 10 / Windows 11 (64-bit Architecture, `win32` platform)
- **Local Workspace**: `c:\Users\USER\Downloads\AI_for_older\AI_Rehabilitation_Safety_Assistant`
- **Git State**: Clean working tree on safety branch `windows-packaging` (checkpointed from `main`).
- **Python Runtimes Detected**:
  - `CPython 3.12.13 (64-bit)`: Located at `C:\Users\USER\AppData\Roaming\uv\python\cpython-3.12.13-windows-x86_64-none\python.exe`
  - `CPython 3.11.15 (64-bit)`: Located at `C:\Users\USER\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe`
  - `Python 3.14.5 (64-bit)`: Located at `C:\Users\USER\AppData\Local\Python\pythoncore-3.14-64\python.exe`
  - `uv` package manager: version `0.11.16`
- **Selected Target Runtime**: **Python 3.12.13 (64-bit)**. Python 3.12 offers mature, verified Windows wheels for PyTorch 2.x, OpenCV Contrib, MediaPipe, and PyQt5, avoiding C-extension incompatibilities found in newer pre-releases such as Python 3.14.

---

## 2. Application Entry Point
- **Primary Entry Point**: `main.py`
  - Initializes root logger and sets default environment variables (`PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python`, `MPLCONFIGDIR`).
  - Sets up PyQt5 platform plugin paths (`Qt5/plugins/platforms`).
  - Creates the master `QApplication` instance and loads global stylesheet.
  - Instantiates `DashboardWindow` (`app.dashboard`).
  - Supports `--test` flag: loads dashboard, updates UI, fires telemetry tick, and performs clean shutdown for headless verification without user blocking.

---

## 3. Python Version
- **Application Requirement**: Python 3.10, 3.11, or 3.12.
- **Packaging Target**: Python 3.12.13 (64-bit).

---

## 4. Runtime Modules
The core application consists of 4 main subsystems orchestrated in a single-process architecture:
1. **Face Recognition & User Enrolment**:
   - `adapters/face_adapter.py`: In-memory OpenCV DNN face detector (`opencv_face_detector_uint8.pb`) + LBPH Recognizer (`cv2.face.LBPHFaceRecognizer_create`). Illumination normalization with CLAHE and bilateral filtering.
   - `app/registration_dialog.py`: Dialog for enrolling new patients with webcam snapshot capture and instant LBPH retraining.
2. **Emotion Recognition**:
   - `adapters/emotion_adapter.py`: Biomechanical Facial Action Coding System (FACS) action units extracted from MediaPipe FaceMesh, blended with PyTorch ExpressionNet (`expression_net.pth`), filtered via a temporal circular buffer for 3 primary states: *Bình thường (Neutral)*, *Vui vẻ (Happy)*, *Buồn bã (Sad)*.
3. **Rehabilitation Exercise Engine**:
   - `adapters/rehabilitation_adapter.py` & `modules/rehabilitation/rehab_engine.py`: MediaPipe Pose landmark extraction, biomechanical planar joint angle computation, Finite State Machine (FSM) repetition counter, form penalty scoring, and HUD telemetry for:
     - Sit-to-Stand (*Co duỗi chân / Đứng lên ngồi xuống*)
     - Arm Raise (*Vươn vai / Nâng tay qua đầu*)
     - Marching (*Đi bộ tại chỗ / Nâng cao đùi*)
4. **Fall Detection & Safety Monitoring**:
   - `adapters/fall_adapter.py`, `modules/fall/fall_detector.py`, & `services/fall_monitor.py`: Real-time posture kinematics (torso vertical inclination angle, bounding box aspect ratio, vertical hip displacement rate). Multi-stage Temporal Verification FSM:
     `NORMAL -> SUSPECTED -> CONFIRMING -> FALL_CONFIRMED -> COOLDOWN -> NORMAL`.
   - Saves evidence snapshot JPEG to persistent storage.
   - Dispatches Gmail SMTP alert to registered Caregiver.
5. **Core Services & Framework**:
   - `core/camera_manager.py`: Singleton thread-safe camera capture engine with fallback synthetic video generator.
   - `core/drawing_utils.py`: High-performance Vietnamese diacritic text rendering via Pillow and Windows TrueType fonts.
   - `services/user_service.py`: Local profile CRUD and caregiver contact resolution.
   - `services/email_service.py`: Fault-tolerant Gmail SMTP client.

---

## 5. Dependencies
### A. Required Windows Runtime Dependencies:
- `PyQt5 >= 5.15.10` (GUI Framework & event loop)
- `opencv-contrib-python >= 4.8.0` (Computer vision + `cv2.face.LBPHFaceRecognizer`)
- `numpy >= 1.24.0, < 2.0.0` (Array operations, compatibility with OpenCV/PyTorch)
- `mediapipe >= 0.10.14` (Pose & FaceMesh tracking pipelines)
- `torch >= 2.0.0` (ExpressionNet neural network inference; CPU wheel preferred)
- `torchvision >= 0.15.0` (Vision utilities)
- `Pillow >= 10.0.0` (Vietnamese font rasterization & image processing)
- `python-dotenv >= 1.0.0` (Configuration loading)
- `psutil >= 5.9.0` (System monitoring)
- `requests >= 2.31.0` (HTTP utilities)
- `pyinstaller >= 6.4.0` (Executable bundling tool)

### B. Obsolete Dependencies Audited & Removed:
- `ultralytics`: 0 imports across all active modules. Not used in Fall Detection (which uses MediaPipe Pose) or Face/Emotion. Eliminates >800MB of package bloat.
- `vosk`, `pyttsx3`, `sounddevice`: Subsystem isolated in `archive/voice/`; not referenced or imported anywhere in active application flow. Eliminates audio device driver risks and DLL conflicts.
- `APScheduler`: Not used in active PyQt5 timer loop.

---

## 6. AI Models
| Model File | Path | Size | Used By | Packaging Action |
| :--- | :--- | :--- | :--- | :--- |
| `opencv_face_detector_uint8.pb` | `modules/face/models/` | ~2.7 MB | `FaceAdapter` | Bundle as read-only data |
| `opencv_face_detector.pbtxt` | `modules/face/models/` | ~2.6 KB | `FaceAdapter` | Bundle as read-only data |
| `age_net.caffemodel` | `modules/face/models/` | ~44 MB | `FaceAdapter` (optional) | Bundle as read-only data |
| `age_deploy.prototxt` | `modules/face/models/` | ~2.0 KB | `FaceAdapter` (optional) | Bundle as read-only data |
| `gender_net.caffemodel` | `modules/face/models/` | ~44 MB | `FaceAdapter` (optional) | Bundle as read-only data |
| `gender_deploy.prototxt` | `modules/face/models/` | ~2.0 KB | `FaceAdapter` (optional) | Bundle as read-only data |
| `expression_net.pth` | `modules/emotion/models/` | ~1.2 MB | `EmotionAdapter` | Bundle as read-only data |
| MediaPipe Pose / FaceMesh | Inside `mediapipe` pkg | Dynamic | `FallDetector`, `RehabEngine`, `EmotionAdapter` | Collected via `collect_data_files('mediapipe')` |

---

## 7. Required Assets
- **Fonts**: Pillow TrueType rendering uses Windows system fonts located at `%WINDIR%\Fonts` (`arialbd.ttf`, `segoeuib.ttf`, etc.). Fallback implemented in `drawing_utils.py`.
- **Configuration Template**: `.env.example` bundled to seed `.env` if not present.
- **Images**: `modules/face/open-cv.png`.

---

## 8. Runtime Data
To satisfy Windows standards and avoid permission issues when installed in `C:\Program Files`, data is strictly bifurcated:
- **Read-Only (Bundled)**: Model weights (`modules/**/models/`), static assets, configuration templates. Resolved via `sys._MEIPASS` when frozen, or project root during development.
- **Writable Application Data**:
  - Standard Windows path: `%LOCALAPPDATA%\AIRehabilitationAssistant\`
  - Structure:
    ```
    %LOCALAPPDATA%\AIRehabilitationAssistant\
    ├── users/               (Individual patient profile JSONs)
    ├── registered_faces/    (Enrolled face crops for LBPH recognizer)
    ├── sessions/            (Rehabilitation session metric logs)
    ├── fall_events/         (Evidence snapshots & event JSONs)
    ├── logs/                (app.log)
    └── config/              (.env configuration)
    ```
  - Automatically initialized on application startup.

---

## 9. Environment Variables
- `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION`: Must be set to `python` to prevent MediaPipe protobuf C++ descriptor collisions.
- `MPLCONFIGDIR`: Must point to `%TEMP%\matplotlib-cache` on Windows rather than hardcoded `/tmp/matplotlib-cache`.
- `CAMERA_INDEX`: Hardware webcam device index (default: `0`).
- `EMAIL_ENABLED`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USERNAME`, `EMAIL_PASSWORD`: Gmail SMTP credentials.

---

## 10. Camera Dependencies
- Handled exclusively through `core.camera_manager.CameraManager` (Singleton).
- Thread-safe frame distribution ensures Face, Emotion, Rehab, and Fall pipelines never open competing `cv2.VideoCapture` handles.
- Built-in simulation fallback generates animated test frames if no hardware camera is connected, preventing hard crashes.

---

## 11. Gmail Dependencies
- Standard library `smtplib` + `email.mime.*`.
- Fully isolated in `services/email_service.py` with non-blocking error handling.
- SMTP connection or authentication failures log warnings and update the UI status badge without raising unhandled exceptions or interrupting video processing.

---

## 12. Subprocess Usage
- Audited: `app/launcher.py` contains `subprocess.Popen` logic, but is an auxiliary utility and is **never invoked** by `main.py` or `dashboard.py`.
- All production AI modules (Face, Emotion, Rehab, Fall) run in-process within the main application thread / camera thread.
- Conclusion: No secondary worker executable or external Python subprocess is required for runtime operation.

---

## 13. Multiprocessing Usage
- No explicit `multiprocessing` processes are spawned by application code.
- To prevent PyInstaller bootloader process-cloning recursion on Windows spawn behavior (e.g. from PyTorch/NumPy worker pools), `multiprocessing.freeze_support()` will be placed at the entry point in `main.py`.

---

## 14. Linux-Specific Code Identified
1. **`/tmp/` Paths**:
   - `main.py`, `demo.py`, `adapters/emotion_adapter.py`, `experiments/benchmark.py`, `tests/test_fall_and_safety.py`: `os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")`.
   - *Fix*: Replace with `os.path.join(tempfile.gettempdir(), "matplotlib-cache")` or `%TEMP%`.
2. **Python Virtual Environment Path**:
   - `config.py` line 68: `VENV_PYTHON = BASE_DIR / ".venv" / "bin" / "python"`.
   - *Fix*: Support Windows `.venv / "Scripts" / "python.exe"`.
3. **Hardcoded Linux Output Path**:
   - `shared/results/fall.json`: contains `/home/gokigenzo/...` snapshot path.
   - *Fix*: Cleared or made relative/Windows-compatible.
4. **Relative Data Paths**:
   - `Path("data/users")` in `face_adapter.py` and `user_service.py` depends on cwd.
   - *Fix*: Standardize on centralized `config.DATA_DIR`.

---

## 15. Windows Compatibility Risks
- **Camera Backend**: OpenCV on Windows may default to MSMF with high startup latency; fallback to DirectShow (`cv2.CAP_DSHOW`) if necessary.
- **Write Permissions**: Writing to relative `data/` when launched from Program Files causes `PermissionDenied`. Resolved by `%LOCALAPPDATA%`.
- **Qt Platform Plugins**: Setting `QT_QPA_PLATFORM_PLUGIN_PATH` manually inside a frozen PyInstaller bundle can override PyInstaller's native plugin resolution.

---

## 16. PyInstaller Risks
- **MediaPipe Binary Assets**: MediaPipe requires its `.binarypb` and `.tflite` model files to be explicitly collected.
- **PyQt5 Windows Platform Plugin**: Missing `qwindows.dll` plugin will prevent UI from rendering.
- **PyTorch DLLs**: Dynamic loading of `torch_cpu.dll` and Intel MKL/OpenMP runtimes.
- **Hidden Imports**: Dynamic imports in `cv2.face`, `mediapipe.python.solutions.*`, and subpackages.

---

## 17. Proposed Minimal Changes
1. **`requirements-windows.txt`**: Create clean requirements file excluding unneeded voice & YOLO packages.
2. **`config.py`**:
   - Add centralized resource resolver `resource_path(relative_path)` supporting both `sys._MEIPASS` and normal development.
   - Configure writable data directory in `%LOCALAPPDATA%\AIRehabilitationAssistant` with startup auto-creation.
   - Fix `VENV_PYTHON` for Windows (`Scripts/python.exe`).
3. **`main.py`**:
   - Add `multiprocessing.freeze_support()`.
   - Fix `MPLCONFIGDIR` to use Windows `%TEMP%`.
   - Guard `QT_QPA_PLATFORM_PLUGIN_PATH` so it does not interfere when frozen.
4. **`adapters/emotion_adapter.py`**:
   - Fix `MPLCONFIGDIR` to use `tempfile.gettempdir()`.
   - Resolve `expression_net.pth` via centralized `resource_path`.
5. **`adapters/face_adapter.py` & `services/user_service.py`**:
   - Direct user data, registered faces, and fallback JSONs to `config.DATA_DIR`.
6. **`packaging/`**:
   - Spec file `AI_Rehabilitation_Assistant.spec` configured for ONEDIR mode.
   - PowerShell build scripts `build_windows_debug.ps1` and `build_windows_release.ps1`.

---

## 18. Packaging Plan
- **Phase 1**: Create local virtual environment `.venv` using Python 3.12.13.
- **Phase 2**: Install audited dependencies (`requirements-windows.txt`).
- **Phase 3-5**: Execute application from source (`python main.py --test` and interactive UI run), verify all modules.
- **Phase 6-8**: Apply minimal Windows path normalizations and resource resolver.
- **Phase 9**: Generate clean PyInstaller `.spec` file in `packaging/`.
- **Phase 10-13**: Compile and test `DEBUG ONEDIR` (with console window enabled to capture runtime tracebacks).
- **Phase 14-15**: Compile and test `RELEASE ONEDIR` (windowed, clean console-free execution).
- **Phase 16-17**: Acceptance testing and performance verification.
- **Phase 18-19**: Generate Vietnamese README, packaging report, and final distribution ZIP.
