import json
import os
import subprocess
import sys
import time
from typing import List, Optional


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOT_SCRIPT = os.path.join(PROJECT_ROOT, "PanosV2.py")
LOCK_FILE = os.path.join(PROJECT_ROOT, "data", "panos_runtime.pid")
LEGACY_LOCK_PID = os.path.join(PROJECT_ROOT, "data", "panos_runtime.lock", "pid")
REPLACE_EXISTING_ARG = "--replace-existing"


def _run_powershell(script: str) -> str:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            script,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        output = ((result.stdout or "") + "\n" + (result.stderr or "")).strip()
        raise RuntimeError(output or "PowerShell command failed")
    return (result.stdout or "").strip()


def _find_existing_runtime_pids(excluded_pids: Optional[List[int]] = None) -> List[int]:
    excluded_pids = sorted({int(pid) for pid in (excluded_pids or []) if int(pid) > 0})
    excluded_literal = ",".join(str(pid) for pid in excluded_pids) or "-1"
    script = """
$excluded = @(__EXCLUDED__)
$items = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object {
    -not ($excluded -contains $_.ProcessId) -and
    $_.CommandLine -notlike '*-m compileall*' -and
    (
        $_.CommandLine -like '*launch_panos.py*' -or
        $_.CommandLine -like '*PanosV2.py*'
    )
} | Select-Object -ExpandProperty ProcessId
if ($items) { $items | ConvertTo-Json -Compress }
""".replace("__EXCLUDED__", excluded_literal)
    output = _run_powershell(script)
    if not output:
        return []
    data = json.loads(output)
    if isinstance(data, int):
        return [data]
    if isinstance(data, list):
        return [int(item) for item in data]
    return []


def _terminate_pid(pid: int) -> bool:
    result = subprocess.run(
        ["taskkill", "/PID", str(pid), "/T", "/F"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        cwd=PROJECT_ROOT,
    )
    if result.returncode not in {0, 128, 255}:
        output = ((result.stdout or "") + "\n" + (result.stderr or "")).strip()
        print(f"[launcher] failed to stop pid={pid}: {output or 'unknown error'}")
        return False
    return True


def _wait_until_pids_exit(target_pids: List[int], timeout_seconds: float = 12.0) -> bool:
    deadline = time.time() + timeout_seconds
    remaining = set(int(pid) for pid in target_pids if pid > 0)
    excluded_pids = [os.getpid(), os.getppid()]
    while remaining and time.time() < deadline:
        active = set(_find_existing_runtime_pids(excluded_pids=excluded_pids))
        remaining &= active
        if not remaining:
            return True
        time.sleep(0.25)
    return not remaining


def _cleanup_lock_files() -> None:
    for path in (LOCK_FILE, LEGACY_LOCK_PID):
        if os.path.isfile(path):
            try:
                os.remove(path)
                print(f"[launcher] removed stale lock file: {os.path.relpath(path, PROJECT_ROOT)}")
            except OSError as e:
                print(f"[launcher] could not remove lock file {path}: {e}")


def main() -> int:
    excluded_pids = [os.getpid(), os.getppid()]
    try:
        existing_pids = sorted(set(_find_existing_runtime_pids(excluded_pids=excluded_pids)))
    except Exception as e:
        print(f"[launcher] failed to inspect existing bot processes: {e}")
        existing_pids = []

    if existing_pids:
        print(f"[launcher] replacing existing PanosV2 process(es): {', '.join(str(pid) for pid in existing_pids)}")
        stopped = True
        for pid in existing_pids:
            if not _terminate_pid(pid):
                stopped = False
        if not stopped:
            return 2
        if not _wait_until_pids_exit(existing_pids):
            print("[launcher] existing PanosV2 process did not exit in time")
            return 2

    _cleanup_lock_files()

    bot_cmd = [sys.executable, BOT_SCRIPT, REPLACE_EXISTING_ARG]
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    return subprocess.call(bot_cmd, cwd=PROJECT_ROOT, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
