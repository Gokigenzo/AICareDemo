"""
Reliable, Atomic AI Model Downloader with SHA-256 Integrity Verification.
Reads models/manifest.json and ensures all models are present and uncorrupted.
Retries up to 3 times with exponential backoff on network failures.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
import time
import tarfile
import shutil
import urllib.request
from pathlib import Path

# Force UTF-8 stdout on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Project root
REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_FILE = REPO_ROOT / "models" / "manifest.json"

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ModelDownloader")


def calculate_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def download_file(url: str, dest_path: Path, expected_sha256: str, max_retries: int = 3, archive_member: str = "") -> bool:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = dest_path.with_suffix(dest_path.suffix + ".download.tmp")

    for attempt in range(1, max_retries + 1):
        try:
            logger.info("Downloading %s (Attempt %d/%d)...", dest_path.name, attempt, max_retries)
            
            # Simple progress reporting
            def reporthook(count: int, block_size: int, total_size: int) -> None:
                if total_size > 0:
                    percent = min(100.0, float(count * block_size) / total_size * 100.0)
                    if count % 100 == 0:
                        sys.stdout.write(f"\r  -> Tiến độ: {percent:.1f}% ({count * block_size // 1024} KB)")
                        sys.stdout.flush()

            urllib.request.urlretrieve(url, str(temp_path), reporthook=reporthook)
            sys.stdout.write("\n")

            if archive_member:
                extracted = temp_path.with_suffix('.extracted.tmp')
                try:
                    with tarfile.open(temp_path, 'r:bz2') as archive:
                        member = archive.getmember(archive_member)
                        if not member.isfile():
                            raise ValueError('Expected regular model file')
                        with archive.extractfile(member) as src, extracted.open('wb') as dst:
                            shutil.copyfileobj(src, dst)
                    extracted.replace(temp_path)
                finally:
                    extracted.unlink(missing_ok=True)

            # Verify integrity
            computed_sha = calculate_sha256(temp_path)
            if expected_sha256 and computed_sha.lower() != expected_sha256.lower():
                logger.error("Hash mismatch for %s! Expected: %s, Got: %s", dest_path.name, expected_sha256, computed_sha)
                if temp_path.exists():
                    temp_path.unlink()
                time.sleep(attempt * 2)
                continue

            # Atomic rename on success
            if dest_path.exists():
                dest_path.unlink()
            temp_path.rename(dest_path)
            logger.info("Successfully downloaded and verified: %s", dest_path.name)
            return True

        except Exception as e:
            logger.warning("Error downloading %s: %s", dest_path.name, e)
            if temp_path.exists():
                temp_path.unlink()
            time.sleep(attempt * 2)

    logger.error("Failed to download %s after %d retries.", dest_path.name, max_retries)
    return False


def verify_or_download_models(core_only: bool = False) -> int:
    if not MANIFEST_FILE.exists():
        logger.error("Model manifest not found: %s", MANIFEST_FILE)
        return 1

    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    models = data.get("models", [])
    logger.info("Found %d models in manifest.", len(models))

    missing_or_corrupt = 0
    downloaded_count = 0

    for m in models:
        target = REPO_ROOT / m["target_path"]
        expected_sha = m.get("sha256", "")
        url = m.get("source_url", "")
        req_core = m.get("required_for_core", True)

        if core_only and not req_core:
            continue

        needs_download = False
        if not target.exists():
            logger.info("Model missing: %s (%s)", m["name"], target)
            needs_download = True
        else:
            actual_sha = calculate_sha256(target)
            if expected_sha and actual_sha.lower() != expected_sha.lower():
                logger.warning("Model corrupt or mismatched: %s. Expected: %s, Found: %s", m["name"], expected_sha, actual_sha)
                needs_download = True

        if needs_download:
            if not url:
                logger.error("Bundled model missing or corrupt and has no download URL: %s", m["name"])
                missing_or_corrupt += 1
                continue
            success = download_file(url, target, expected_sha, archive_member=m['archive_member']) if m.get('archive_member') else download_file(url, target, expected_sha)
            if success:
                downloaded_count += 1
            else:
                missing_or_corrupt += 1

    if missing_or_corrupt > 0:
        logger.warning("Completed with %d missing or failed model downloads.", missing_or_corrupt)
        return 1

    logger.info("All required AI models are present and verified.")
    return 0


if __name__ == "__main__":
    log_dir = REPO_ROOT / "runtime" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "model_download.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(file_handler)
    parser = argparse.ArgumentParser(description="AI Model Downloader and Verifier")
    parser.add_argument("--core-only", action="store_true", help="Download only essential vision models (exclude large Whisper)")
    args = parser.parse_args()
    sys.exit(verify_or_download_models(core_only=args.core_only))

