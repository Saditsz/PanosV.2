from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = PROJECT_ROOT / "data" / "runtime_bootstrap_state.json"
REQUIREMENTS_PATH = PROJECT_ROOT / "requirements.txt"
REQUIRED_MODULES = ("discord", "yt_dlp", "dotenv", "nacl", "davey")
YTDLP_REFRESH_SECONDS = 7 * 24 * 60 * 60


def _log(message: str) -> None:
    text = f"[bootstrap] {message}"
    encoding = sys.stdout.encoding or "utf-8"
    safe_text = text.encode(encoding, errors="replace").decode(encoding, errors="replace")
    print(safe_text)


def _load_state() -> dict:
    if not STATE_PATH.is_file():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _module_missing(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is None


def _trim_output(text: str, max_chars: int = 1200) -> str:
    cleaned = text.strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[:max_chars] + "\n... (truncated)"


def _run(command: list[str], dry_run: bool = False) -> int:
    pretty = " ".join(command)
    if dry_run:
        _log(f"dry-run: {pretty}")
        return 0

    _log(f"run: {pretty}")
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    combined_output = ((completed.stdout or "") + "\n" + (completed.stderr or "")).strip()
    if completed.returncode != 0 and combined_output:
        _log("command output:")
        print(_trim_output(combined_output))
    return int(completed.returncode)


def _requirements_mtime() -> float:
    if not REQUIREMENTS_PATH.is_file():
        return 0.0
    return float(REQUIREMENTS_PATH.stat().st_mtime)


def _ensure_requirements(state: dict, dry_run: bool = False) -> None:
    missing_modules = [name for name in REQUIRED_MODULES if _module_missing(name)]
    requirements_mtime = _requirements_mtime()
    state_mtime = float(state.get("requirements_mtime", 0.0))
    needs_install = bool(missing_modules)
    needs_install = needs_install or (
        REQUIREMENTS_PATH.is_file() and abs(requirements_mtime - state_mtime) > 0.001
    )

    if not needs_install:
        _log("requirements look healthy")
        return

    reason = []
    if missing_modules:
        reason.append(f"missing modules: {', '.join(missing_modules)}")
    if REQUIREMENTS_PATH.is_file() and abs(requirements_mtime - state_mtime) > 0.001:
        reason.append("requirements.txt changed")
    _log("installing dependencies because " + " | ".join(reason))

    if not REQUIREMENTS_PATH.is_file():
        _log("requirements.txt not found, skipping install")
        return

    return_code = _run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-r",
            str(REQUIREMENTS_PATH),
        ],
        dry_run=dry_run,
    )
    if dry_run:
        _log("dry-run: requirements install skipped")
        return
    if return_code == 0:
        state["requirements_mtime"] = requirements_mtime
        _save_state(state)
        _log("dependencies ready")
    else:
        _log("dependency install failed; continuing with current environment")


def _maybe_refresh_ytdlp(state: dict, dry_run: bool = False) -> None:
    now = time.time()
    last_checked = float(state.get("yt_dlp_checked_at", 0.0))
    age_seconds = now - last_checked
    if age_seconds < YTDLP_REFRESH_SECONDS:
        days_left = int((YTDLP_REFRESH_SECONDS - age_seconds) // 86400)
        _log(f"skip yt-dlp refresh for now ({days_left} day(s) until next check)")
        return

    _log("refreshing yt-dlp to keep YouTube extraction stable")
    return_code = _run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--upgrade",
            "yt-dlp",
        ],
        dry_run=dry_run,
    )
    if dry_run:
        _log("dry-run: yt-dlp refresh skipped")
        return
    state["yt_dlp_checked_at"] = now
    state["yt_dlp_refresh_ok"] = return_code == 0
    _save_state(state)
    if return_code == 0:
        _log("yt-dlp refresh completed")
    else:
        _log("yt-dlp refresh failed; current version will still be used")


def main(argv: list[str]) -> int:
    dry_run = "--dry-run" in argv
    state = _load_state()
    _ensure_requirements(state, dry_run=dry_run)
    _maybe_refresh_ytdlp(state, dry_run=dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
