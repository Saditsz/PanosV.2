# Panos Discord Bot (refactored + music + slash)

import os
import random
import calendar
import shutil
import subprocess
import sys
import threading
import json
import glob
import atexit
import ctypes
import signal
from collections import deque
from copy import deepcopy
from itertools import cycle
from typing import Dict, List, Optional
from urllib.parse import parse_qs, urlparse

import chess
import time

import asyncio

import discord
from discord.ext import commands, tasks
from discord.ui import Button, View, Select, Item
from discord import File, Intents, app_commands


from easy_pil import Editor, load_image_async, Font
from dotenv import load_dotenv

import yt_dlp as youtube_dl
import yt_dlp
from Music_room import MusicRoomFacade, music_runtime_summary

load_dotenv()

YTDL_PROXY = os.getenv("YTDL_PROXY", "")
YTDL_COOKIES_FILE = os.getenv("YTDL_COOKIES_FILE", "").strip()
YTDL_COOKIES_BROWSER = os.getenv("YTDL_COOKIES_BROWSER", "").strip()
YTDL_PLAYER_CLIENTS = [
    client.strip()
    for client in os.getenv("YTDL_PLAYER_CLIENTS", "android,ios,web").split(",")
    if client.strip()
]
YTDL_FALLBACK_BROWSERS = [
    browser.strip()
    for browser in os.getenv(
        "YTDL_FALLBACK_BROWSERS",
        "chrome,edge,firefox,brave,opera,vivaldi,chromium",
    ).split(",")
    if browser.strip()
]


class _SilentYTDLLogger:
    def debug(self, msg: str):
        return None

    def warning(self, msg: str):
        return None

    def error(self, msg: str):
        return None


YTDL_LOGGER = _SilentYTDLLogger()

# ==========================
#  CONFIG / GLOBAL DATA
# ==========================

intents = Intents.all()
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("+"),
    help_command=None,
    intents=intents,
    application_id=970204776530853928,
)

RESTART_EXIT_CODE = 113
PROCESS_EXIT_CODE = 0
WATCH_POLL_SECONDS = 2.0
SUPERVISOR_ARG = "--supervisor"
CHILD_ARG = "--child"
REPLACE_EXISTING_ARG = "--replace-existing"
ENABLE_SUPERVISOR_ENV = "PANOS_ENABLE_SUPERVISOR"
INSTANCE_LOCK_FILE = os.path.join("data", "panos_runtime.pid")
LEGACY_INSTANCE_LOCK_DIR = os.path.join("data", "panos_runtime.lock")
WATCH_IGNORE_DIRS = {
    ".venv",
    "__pycache__",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".vscode",
    ".idea",
}


betmsg = ["**=w=**", "**yeah**", "**aww**", "**:)**"]
stupidmsg = [
    "**Sorry,** **I'll try to be better.** **You bad**",
    "=w= Meow🙁",
    "sulk.",
]

valorant_image = [
    "https://i.ytimg.com/vi/latqydW2lOo/maxresdefault.jpg",
    "https://i.ytimg.com/vi/xT4gghSQoPc/maxresdefault.jpg",
    "https://drive.tiny.cloud/1/7gj1i1igse8gzizlchgw4q5owgge0ci1xc82p6p9yf0cg1u2/72008f11-53cf-4dac-9605-3f102cd954a6",
]

yuri_image = [
    "https://tenor.com/view/yuri-anime-gif-19126992",
    "https://c.tenor.com/YTsHLAJdOT4AAAAC/anime-kiss.gif",
    "https://c.tenor.com/ewu8BygrzkwAAAAC/yuri.gif",
    "https://c.tenor.com/jlDpJDljsHUAAAAC/yuri-anime.gif",
    "https://i.pinimg.com/originals/58/3e/0e/583e0e1939f211f7cc9dd115f2ae216d.gif",
    "https://pa1.narvii.com/6249/e638e52d88ab76205ba5ce229da1a549c4de3f6e_hq.gif",
    "https://38.media.tumblr.com/822b4317ae95d72cc186956ed7496599/tumblr_nle07a5K1r1th74oto1_500.gif",
    "https://acegif.com/wp-content/uploads/gif/anime-hug-52.gif",
]

loli_gif = [
    "https://media1.tenor.com/images/4373d2c0cd615f29f0ca0465f3787a41/tenor.gif?itemid=19359874",
    "https://gifimage.net/wp-content/uploads/2017/09/anime-loli-gif-1.gif",
    "https://pa1.narvii.com/6427/d52332bc0bba4c11ae80ed4d354cbbe4d3b109a8_hq.gif",
    "https://th.bing.com/th/id/R.17125ba4270d982436fd121118d9c618?rik=H%2fTG7kzOGCqHLA&pid=ImgRaw&r=0",
    "https://pa1.narvii.com/6414/d712bf53a726a0597b5ac1ebb13995d2a507e013_hq.gif",
    "https://pa1.narvii.com/6373/b1f25ab558ac4c7ffa15d0fada68a0b7bed6f926_hq.gif",
    "https://media1.tenor.com/images/3e06b368fbe0e15f1a694d8329c02baa/tenor.gif?itemid=9920985",
    "https://pa1.narvii.com/5603/2ab67a69762fd1a0fc3eb5764b490e66d3ff9fd3_hq.gif",
    "https://media1.tenor.com/images/c7663686b70a23e9666f86122ad3151a/tenor.gif?itemid=5897449",
    "https://i.ytimg.com/vi/j6RhNcHNo_A/hqdefault.jpg",
]

kick_gifs = [
    "https://c.tenor.com/izi_49ZVYyYAAAAC/tiens-retien.gif",
    "https://c.tenor.com/CJj7Ik-0zFEAAAAC/navibot-kick.gif",
]
kick_names = ["Kik you", "first KiK"]

smash_gifs = [
    "https://c.tenor.com/4p2gwNLsxBEAAAAC/whizzy-imposterfox.gif",
    "https://c.tenor.com/_DSkM4tYeckAAAAC/deku-midoriya.gif",
    "https://c.tenor.com/zrEwCsocdxYAAAAC/judgement-ora.gif",
]
smash_names = ["smash 100% !!", "smash one punch", "command smash ora ora ora ora ora"]

yasuo_endgame = [
    "https://images.contentstack.io/v3/assets/blt731acb42bb3d1659/blte29e9d69675e1d09/629804d68eeef945727642ab/060722_Chibi_Yasuo_Base.jpg",
    "https://cdnb.artstation.com/p/assets/images/images/005/214/931/large/akumey-033-.jpg?1489394228",
    "https://i.redd.it/0j59derlw4q31.jpg",
    "https://i.pinimg.com/originals/8c/83/2b/8c832b5ac04a1cb7272e0b5a8bcd1957.jpg",
]

JPG_NAME = ["Pring1.jpg", "Pring4.jpg", "Pring5.jpg"]

status_messages = cycle(["/help", "command + or /", "Bot of the AKANEMI"])

# ==========================
#  MUSIC SYSTEM (YTDL + FFmpeg)
# ==========================

YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "logger": YTDL_LOGGER,
    "proxy": YTDL_PROXY,
    "extractor_args": {
        "youtube": {
            "player_client": YTDL_PLAYER_CLIENTS or ["android", "ios", "web"],
        }
    },
}
if YTDL_COOKIES_FILE and os.path.isfile(YTDL_COOKIES_FILE):
    YTDL_OPTIONS["cookiefile"] = YTDL_COOKIES_FILE
if YTDL_COOKIES_BROWSER:
    # Example: chrome, edge, firefox
    YTDL_OPTIONS["cookiesfrombrowser"] = (YTDL_COOKIES_BROWSER,)


def _env_int(name: str, default: int, minimum: int | None = None, maximum: int | None = None) -> int:
    raw = os.getenv(name, "").strip()
    value = default
    if raw:
        try:
            value = int(raw)
        except ValueError:
            value = default
    if minimum is not None:
        value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)
    return value


def _ffmpeg_candidate_paths(raw_value: str) -> list[str]:
    cleaned = raw_value.strip().strip('"').strip("'")
    if not cleaned:
        return []
    if os.path.isdir(cleaned):
        return [
            os.path.join(cleaned, "ffmpeg.exe"),
            os.path.join(cleaned, "ffmpeg"),
            os.path.join(cleaned, "bin", "ffmpeg.exe"),
            os.path.join(cleaned, "bin", "ffmpeg"),
        ]
    return [cleaned]


def _resolve_ffmpeg_executable() -> str:
    candidates: list[str] = []
    for env_name in ("FFMPEG_PATH", "FFMPEG_BIN", "FFMPEG_DIR", "FFMPEG_HOME"):
        candidates.extend(_ffmpeg_candidate_paths(os.getenv(env_name, "")))

    for binary_name in ("ffmpeg.exe", "ffmpeg"):
        located = shutil.which(binary_name)
        if located:
            candidates.append(located)

    for env_dir in (os.getenv("ProgramFiles", ""), os.getenv("ProgramFiles(x86)", "")):
        if not env_dir:
            continue
        candidates.extend(
            [
                os.path.join(env_dir, "ffmpeg", "bin", "ffmpeg.exe"),
                os.path.join(env_dir, "ffmpeg", "ffmpeg.exe"),
                os.path.join(env_dir, "FFmpeg", "bin", "ffmpeg.exe"),
                os.path.join(env_dir, "FFmpeg", "ffmpeg.exe"),
            ]
        )

    seen: set[str] = set()
    for candidate in candidates:
        normalized = os.path.normpath(candidate)
        if normalized in seen:
            continue
        seen.add(normalized)
        if os.path.isfile(normalized):
            return normalized
    return "ffmpeg"


FFMPEG_OPTIONS = {
    "before_options": (
        "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 "
        "-protocol_whitelist file,http,https,tcp,tls,crypto"
    ),
    "options": "-vn",
}
FFMPEG_EXECUTABLE = _resolve_ffmpeg_executable()

ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)
_instance_lock_acquired = False


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_query(cls, query: str, *, loop=None, stream: bool = True):
        loop = loop or asyncio.get_running_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(query, download=not stream)
        )

        if "entries" in data:
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(
            discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data
        )


class FFmpegStderrBuffer:
    def __init__(self, max_lines: int = 25):
        self.lines = deque(maxlen=max_lines)
        self._buffer = b""
        self._lock = threading.Lock()

    def write(self, data: bytes) -> int:
        if not data:
            return 0

        with self._lock:
            self._buffer += data
            while b"\n" in self._buffer:
                raw_line, self._buffer = self._buffer.split(b"\n", 1)
                line = raw_line.decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                self.lines.append(line)
                print(f"[ffmpeg] {line}")
        return len(data)

    def flush(self) -> None:
        return None

    def tail(self, count: int = 4) -> str:
        with self._lock:
            lines = list(self.lines)
            leftover = self._buffer.decode("utf-8", errors="ignore").strip()
        if leftover:
            lines.append(leftover)
        return "\n".join(lines[-count:])


class OXButton(discord.ui.Button):
    def __init__(self, index: int):
        row = index // 3
        super().__init__(label="⬜", style=discord.ButtonStyle.secondary, row=row)
        self.index = index  # 0–8

    async def callback(self, interaction: discord.Interaction):
        view: "OXView" = self.view  # type: ignore
        await view.cog.handle_player_move(interaction, self.index)


class OXView(discord.ui.View):
    def __init__(self, cog: "SlashCog", user_id: int):
        super().__init__(timeout=180)
        self.cog = cog
        self.user_id = user_id

        for i in range(9):
            self.add_item(OXButton(i))

    async def on_timeout(self) -> None:
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        for game in self.cog.games.values():
            if game.get("view") is self:
                msg = game.get("message")
                if msg:
                    await msg.edit(content="⌛ The game timed out.", view=self)
                break

class SlashCog(commands.Cog):
    """Main slash command collection for utility, music, and games."""

    def __init__(self, bot_: commands.Bot):
        self.bot = bot_
        self.music_room = MusicRoomFacade(self)
        self.queues: Dict[int, List[Dict]] = {}
        self.games: Dict[int, Dict] = {}
        self.next_starter: Dict[int, str] = {}
        self.legacy_music_cache_dir = os.path.join("data", "music_cache")
        self.music_cache_dir = (
            os.getenv("MUSIC_LOCAL_AUDIO_DIR", os.path.join("data", "music_spool")).strip()
            or os.path.join("data", "music_spool")
        )
        self.music_settings_path = os.path.join("data", "music_audio_settings.json")
        self.locked_cookie_browsers: set[str] = set()
        self.runtime_speed: Dict[int, float] = {}
        self.now_playing: Dict[int, Dict] = {}
        self.now_playing_messages: Dict[int, discord.Message] = {}
        self.now_playing_views: Dict[int, object] = {}
        self.voice_locks: Dict[int, asyncio.Lock] = {}
        self.play_locks: Dict[int, asyncio.Lock] = {}
        self.last_voice_channel_id: Dict[int, int] = {}
        self.intentional_voice_disconnects: set[int] = set()
        self.intentional_track_stops: Dict[int, str] = {}
        self.voice_recovery_tasks: Dict[int, asyncio.Task] = {}
        self.voice_recovery_attempts: Dict[int, int] = {}
        self.pending_stage_routes: Dict[int, Dict] = {}
        self.persistent_audio: Dict[str, Dict[str, float]] = self._load_persistent_audio_settings()
        self.music_delete_after_play = os.getenv("MUSIC_DELETE_AFTER_PLAY", "1").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        self.music_cache_max_bytes = _env_int("MUSIC_CACHE_MAX_MB", 128, minimum=32) * 1024 * 1024
        self.music_cache_max_age_hours = _env_int("MUSIC_CACHE_MAX_AGE_HOURS", 6, minimum=0)
        self.music_cache_keep_min_files = _env_int("MUSIC_CACHE_KEEP_MIN_FILES", 0, minimum=0, maximum=20)
        os.makedirs(self.music_cache_dir, exist_ok=True)
        self._cleanup_legacy_music_cache()
        self._prune_music_cache(force=True)

    # ---------- Music helpers ----------

    @staticmethod
    def _normalize_tone(value: str) -> str:
        lowered = str(value).lower().strip()
        if lowered in {"bass", "treble", "normal"}:
            return lowered
        return "normal"

    @staticmethod
    def _tone_to_eq(tone: str) -> tuple[float, float]:
        normalized = SlashCog._normalize_tone(tone)
        if normalized == "bass":
            return 10.0, 0.0
        if normalized == "treble":
            return 0.0, 8.0
        return 0.0, 0.0

    @staticmethod
    def _clamp_eq_db(value: float) -> float:
        return round(max(-20.0, min(20.0, float(value))), 1)

    @staticmethod
    def _tone_label(value: str) -> str:
        tone = SlashCog._normalize_tone(value)
        if tone == "bass":
            return "bass boost"
        if tone == "treble":
            return "treble boost"
        return "normal"

    def _load_persistent_audio_settings(self) -> Dict[str, Dict[str, float]]:
        os.makedirs(os.path.dirname(self.music_settings_path), exist_ok=True)
        if not os.path.isfile(self.music_settings_path):
            return {}
        try:
            with open(self.music_settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return {}
            cleaned: Dict[str, Dict[str, float]] = {}
            for guild_id, raw in data.items():
                bass_db = 0.0
                treble_db = 0.0
                if isinstance(raw, dict):
                    bass_db = self._clamp_eq_db(float(raw.get("bass_db", raw.get("bass", 0.0))))
                    treble_db = self._clamp_eq_db(float(raw.get("treble_db", raw.get("treble", 0.0))))
                else:
                    bass_db, treble_db = self._tone_to_eq(str(raw))
                cleaned[str(guild_id)] = {
                    "bass_db": bass_db,
                    "treble_db": treble_db,
                }
            return cleaned
        except Exception as e:
            print(f"[music] failed to load audio settings: {e}")
            return {}

    def _save_persistent_audio_settings(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.music_settings_path), exist_ok=True)
            tmp_path = self.music_settings_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self.persistent_audio, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self.music_settings_path)
        except Exception as e:
            print(f"[music] failed to save audio settings: {e}")

    @staticmethod
    def _get_ffmpeg_executable() -> str:
        return FFMPEG_EXECUTABLE

    async def _ensure_stage_voice_ready(
        self,
        guild: discord.Guild,
        announce_channel: Optional[object] = None,
    ) -> bool:
        voice = guild.voice_client
        if voice is None or not isinstance(voice.channel, discord.StageChannel):
            return True
        me_voice = guild.me.voice if guild.me else None
        if not me_voice or not me_voice.suppress:
            return True
        try:
            await guild.me.edit(suppress=False)
            return True
        except discord.Forbidden:
            if announce_channel is not None and hasattr(announce_channel, "send"):
                try:
                    await announce_channel.send(
                        "⚠️ The bot is in a Stage channel but is still suppressed. Grant Speak or unsuppress it first."
                    )
                except Exception:
                    pass
            return False
        except Exception as e:
            print(f"[voice] stage unsuppress failed | guild={guild.id} | error={e!r}")
            return False

    def _active_music_cache_paths(self) -> set[str]:
        active_paths: set[str] = set()
        for current in self.now_playing.values():
            local_path = current.get("local_path")
            if isinstance(local_path, str) and os.path.isfile(local_path):
                active_paths.add(os.path.abspath(local_path))
        for queue in self.queues.values():
            for item in queue:
                local_path = item.get("local_path")
                if isinstance(local_path, str) and os.path.isfile(local_path):
                    active_paths.add(os.path.abspath(local_path))
        return active_paths

    def _prune_music_cache(self, force: bool = False) -> None:
        if not os.path.isdir(self.music_cache_dir):
            return

        active_paths = self._active_music_cache_paths()
        files: list[dict[str, float | str]] = []
        for name in os.listdir(self.music_cache_dir):
            path = os.path.join(self.music_cache_dir, name)
            if not os.path.isfile(path):
                continue
            try:
                stats = os.stat(path)
            except OSError:
                continue
            files.append(
                {
                    "path": path,
                    "size": float(stats.st_size),
                    "mtime": float(stats.st_mtime),
                }
            )

        if not files:
            return

        now_ts = time.time()
        total_size = sum(int(item["size"]) for item in files)
        max_age_seconds = self.music_cache_max_age_hours * 3600
        removable = sorted(files, key=lambda item: float(item["mtime"]))
        removed_any = False

        def _remove_file(path: str, reason: str) -> None:
            nonlocal total_size, removed_any
            try:
                size = os.path.getsize(path)
            except OSError:
                size = 0
            try:
                os.remove(path)
                total_size = max(0, total_size - size)
                removed_any = True
                print(f"[music] pruned cache ({reason}): {path}")
            except OSError as e:
                print(f"[music] failed to prune cache {path}: {e}")

        if max_age_seconds > 0:
            for item in list(removable):
                path = str(item["path"])
                if os.path.abspath(path) in active_paths:
                    continue
                age_seconds = now_ts - float(item["mtime"])
                if age_seconds >= max_age_seconds:
                    _remove_file(path, "expired")
                    removable.remove(item)

        remaining_files = [
            item
            for item in removable
            if os.path.isfile(str(item["path"]))
        ]
        remaining_non_active = [
            item
            for item in remaining_files
            if os.path.abspath(str(item["path"])) not in active_paths
        ]

        if total_size > self.music_cache_max_bytes or force:
            while (
                remaining_non_active
                and total_size > self.music_cache_max_bytes
                and len(remaining_files) > self.music_cache_keep_min_files
            ):
                item = remaining_non_active.pop(0)
                path = str(item["path"])
                _remove_file(path, "size")
                remaining_files = [
                    current
                    for current in remaining_files
                    if str(current["path"]) != path
                ]

        if force and not removed_any and total_size > self.music_cache_max_bytes:
            print(
                f"[music] cache still above limit after prune: "
                f"{round(total_size / (1024 * 1024), 1)} MB"
            )

    def _cleanup_legacy_music_cache(self) -> None:
        legacy_dir = self.legacy_music_cache_dir
        if os.path.abspath(legacy_dir) == os.path.abspath(self.music_cache_dir):
            return
        if not os.path.isdir(legacy_dir):
            return

        removed_any = False
        for name in os.listdir(legacy_dir):
            path = os.path.join(legacy_dir, name)
            if not os.path.isfile(path):
                continue
            try:
                os.remove(path)
                removed_any = True
                print(f"[music] removed legacy cache file: {path}")
            except OSError as e:
                print(f"[music] failed to remove legacy cache file {path}: {e}")

        if removed_any:
            try:
                os.rmdir(legacy_dir)
            except OSError:
                pass

    def _is_managed_music_path(self, path: Optional[str]) -> bool:
        if not isinstance(path, str) or not path:
            return False
        try:
            target = os.path.abspath(path)
            root = os.path.abspath(self.music_cache_dir)
            return os.path.commonpath([target, root]) == root
        except (OSError, ValueError):
            return False

    async def _cleanup_local_audio_path(
        self,
        path: Optional[str],
        *,
        delay_seconds: float = 0.0,
    ) -> None:
        if not self.music_delete_after_play or not self._is_managed_music_path(path):
            return

        assert isinstance(path, str)
        target = os.path.abspath(path)
        if delay_seconds > 0:
            await asyncio.sleep(delay_seconds)

        if target in self._active_music_cache_paths():
            return
        if not os.path.isfile(target):
            return

        try:
            os.remove(target)
            print(f"[music] removed local audio: {target}")
        except PermissionError:
            await asyncio.sleep(1.0)
            if target in self._active_music_cache_paths() or not os.path.isfile(target):
                return
            try:
                os.remove(target)
                print(f"[music] removed local audio after retry: {target}")
            except OSError as e:
                print(f"[music] failed to remove local audio {target}: {e}")
        except OSError as e:
            print(f"[music] failed to remove local audio {target}: {e}")

    def _schedule_local_audio_cleanup(
        self,
        path: Optional[str],
        *,
        delay_seconds: float = 0.0,
    ) -> None:
        if not self.music_delete_after_play or not self._is_managed_music_path(path):
            return

        async def _runner() -> None:
            await self._cleanup_local_audio_path(path, delay_seconds=delay_seconds)

        def _start() -> None:
            self.bot.loop.create_task(_runner())

        try:
            self.bot.loop.call_soon_threadsafe(_start)
        except RuntimeError:
            pass

    def _schedule_queue_item_cleanup(
        self,
        item: Optional[Dict],
        *,
        delay_seconds: float = 0.0,
    ) -> None:
        if not isinstance(item, dict):
            return
        self._schedule_local_audio_cleanup(item.get("local_path"), delay_seconds=delay_seconds)

    def _schedule_queue_cleanup(
        self,
        items: List[Dict],
        *,
        delay_seconds: float = 0.0,
    ) -> None:
        for item in items:
            self._schedule_queue_item_cleanup(item, delay_seconds=delay_seconds)

    def _get_guild_speed(self, guild_id: Optional[int]) -> float:
        if guild_id is None:
            return 1.0
        return float(self.runtime_speed.get(guild_id, 1.0))

    def _set_guild_speed(self, guild_id: int, value: float) -> None:
        rounded = round(float(value), 2)
        if abs(rounded - 1.0) < 0.01:
            self.runtime_speed.pop(guild_id, None)
            return
        self.runtime_speed[guild_id] = rounded

    def _get_guild_eq(self, guild_id: Optional[int]) -> Dict[str, float]:
        if guild_id is None:
            return {"bass_db": 0.0, "treble_db": 0.0}
        current = self.persistent_audio.get(str(guild_id), {})
        bass_db = self._clamp_eq_db(float(current.get("bass_db", 0.0)))
        treble_db = self._clamp_eq_db(float(current.get("treble_db", 0.0)))
        return {"bass_db": bass_db, "treble_db": treble_db}

    def _set_guild_eq(
        self,
        guild_id: int,
        bass_db: Optional[float] = None,
        treble_db: Optional[float] = None,
    ) -> None:
        current = self._get_guild_eq(guild_id)
        if bass_db is not None:
            current["bass_db"] = self._clamp_eq_db(bass_db)
        if treble_db is not None:
            current["treble_db"] = self._clamp_eq_db(treble_db)
        self.persistent_audio[str(guild_id)] = current
        self._save_persistent_audio_settings()

    def _get_guild_tone(self, guild_id: Optional[int]) -> str:
        eq = self._get_guild_eq(guild_id)
        bass_db = eq["bass_db"]
        treble_db = eq["treble_db"]
        if abs(bass_db) < 0.1 and abs(treble_db) < 0.1:
            return "normal"
        if bass_db > 0 and bass_db >= treble_db:
            return "bass"
        if treble_db > 0 and treble_db > bass_db:
            return "treble"
        return "normal"

    def _set_guild_tone(self, guild_id: int, tone: str) -> None:
        bass_db, treble_db = self._tone_to_eq(tone)
        self._set_guild_eq(guild_id, bass_db=bass_db, treble_db=treble_db)

    def _build_audio_filter_chain(self, guild_id: Optional[int]) -> str:
        filters: List[str] = []
        speed = self._get_guild_speed(guild_id)
        if abs(speed - 1.0) >= 0.01:
            filters.append(f"atempo={speed:.2f}")

        eq = self._get_guild_eq(guild_id)
        if abs(eq["bass_db"]) >= 0.1:
            filters.append(f'bass=g={eq["bass_db"]:.1f}:f=100:w=0.8')
        if abs(eq["treble_db"]) >= 0.1:
            filters.append(f'treble=g={eq["treble_db"]:.1f}:f=3500:w=0.8')

        return ",".join(filters)

    def _build_ffmpeg_play_options(self, guild_id: Optional[int]) -> str:
        options = FFMPEG_OPTIONS["options"]
        filter_chain = self._build_audio_filter_chain(guild_id)
        if filter_chain:
            options = f'{options} -af "{filter_chain}"'
        return f"{options} -loglevel warning"

    async def _reapply_current_track(self, interaction: discord.Interaction) -> bool:
        if interaction.guild is None:
            return False
        if interaction.guild_id is None:
            return False
        return await self._reapply_current_track_for_guild(interaction.guild_id)

    async def _reapply_current_track_for_guild(self, guild_id: int) -> bool:
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return False
        voice = guild.voice_client
        if voice is None or not (voice.is_playing() or voice.is_paused()):
            return False

        current = self.now_playing.get(guild_id)
        if not current:
            return False

        queue = self.get_queue(guild_id)
        queue.insert(0, dict(current))
        self.intentional_track_stops[guild_id] = "reapply"
        voice.stop()
        return True

    async def _disable_now_playing_message(
        self,
        guild_id: int,
        *,
        footer_text: Optional[str] = None,
    ) -> None:
        message = self.now_playing_messages.pop(guild_id, None)
        self.now_playing_views.pop(guild_id, None)
        if message is None:
            return
        embed = None
        if message.embeds:
            try:
                embed = discord.Embed.from_dict(message.embeds[0].to_dict())
                if footer_text:
                    embed.set_footer(text=footer_text)
            except Exception:
                embed = None
        try:
            if embed is not None:
                await message.edit(embed=embed, view=None)
            else:
                await message.edit(view=None)
        except (discord.NotFound, discord.HTTPException, AttributeError):
            pass

    async def _publish_now_playing_message(
        self,
        guild_id: int,
        channel: object,
        *,
        embed: discord.Embed,
    ) -> None:
        view = self.music_room.build_now_playing_view(guild_id)
        existing = self.now_playing_messages.get(guild_id)

        if existing is not None:
            try:
                existing_channel = getattr(existing, "channel", None)
                if getattr(existing_channel, "id", None) == getattr(channel, "id", None):
                    await existing.edit(embed=embed, view=view)
                    self.now_playing_views[guild_id] = view
                    return
                await existing.edit(view=None)
            except (discord.NotFound, discord.HTTPException, AttributeError):
                pass
            self.now_playing_messages.pop(guild_id, None)
            self.now_playing_views.pop(guild_id, None)

        try:
            message = await channel.send(embed=embed, view=view)
            self.now_playing_messages[guild_id] = message
            self.now_playing_views[guild_id] = view
        except Exception as e:
            print(f"[music] failed to publish now playing message: {e}")

    async def _stop_guild_playback(
        self,
        guild_id: Optional[int],
        *,
        disconnect: bool = False,
    ) -> bool:
        if guild_id is None:
            return False

        guild = self.bot.get_guild(guild_id)
        voice = guild.voice_client if guild is not None else None
        queued_items = list(self.queues.get(guild_id, []))
        current = self.now_playing.pop(guild_id, None)
        had_state = bool(queued_items or current or (voice and voice.is_connected()))

        self.queues[guild_id] = []
        self.pending_stage_routes.pop(guild_id, None)
        self.voice_recovery_attempts.pop(guild_id, None)
        self._schedule_queue_cleanup(queued_items)
        self._schedule_queue_item_cleanup(current, delay_seconds=2.0)
        await self._disable_now_playing_message(guild_id, footer_text="Playback stopped")

        if voice is None or not voice.is_connected():
            return had_state

        if disconnect:
            self.intentional_voice_disconnects.add(guild_id)
            self.intentional_track_stops[guild_id] = "disconnect"
            if voice.is_playing() or voice.is_paused():
                voice.stop()
            await voice.disconnect()
            return True

        if voice.is_playing() or voice.is_paused():
            self.intentional_track_stops[guild_id] = "stop"
            voice.stop()
            return True
        return had_state

    @staticmethod
    def _is_cookie_copy_error(exc: Exception) -> bool:
        msg = str(exc).lower()
        if "cookie" not in msg:
            return False
        if "could not copy" in msg and "database" in msg:
            return True
        if "failed to load cookies" in msg:
            return True
        if "permission denied" in msg:
            return True
        if "database is locked" in msg:
            return True
        return False

    @staticmethod
    def _without_cookie_options(opts: Dict[str, object]) -> Dict[str, object]:
        cleaned = dict(opts)
        cleaned.pop("cookiesfrombrowser", None)
        cleaned.pop("cookiefile", None)
        return cleaned

    @staticmethod
    def _clone_ydl_opts(opts: Dict[str, object]) -> Dict[str, object]:
        return deepcopy(opts)

    def _candidate_player_client_sets(self, base_opts: Dict[str, object]) -> List[List[str]]:
        configured_clients = YTDL_PLAYER_CLIENTS or ["android", "ios", "web"]
        client_sets: List[List[str]] = [configured_clients]

        for fallback_set in (
            ["android", "ios"],
            ["android", "web"],
            ["tv", "web"],
            ["android"],
            ["ios"],
            ["web"],
        ):
            if fallback_set != configured_clients:
                client_sets.append(fallback_set)

        unique_sets: List[List[str]] = []
        seen = set()
        for client_set in client_sets:
            normalized = tuple(client.strip() for client in client_set if client.strip())
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            unique_sets.append(list(normalized))
        return unique_sets

    def _with_player_clients(
        self,
        opts: Dict[str, object],
        clients: List[str],
    ) -> Dict[str, object]:
        cloned = self._clone_ydl_opts(opts)
        extractor_args = cloned.get("extractor_args")
        if not isinstance(extractor_args, dict):
            extractor_args = {}
        youtube_args = extractor_args.get("youtube")
        if not isinstance(youtube_args, dict):
            youtube_args = {}
        youtube_args["player_client"] = clients
        extractor_args["youtube"] = youtube_args
        cloned["extractor_args"] = extractor_args
        return cloned

    def _get_guild_lock(self, locks: Dict[int, asyncio.Lock], guild_id: int) -> asyncio.Lock:
        lock = locks.get(guild_id)
        if lock is None:
            lock = asyncio.Lock()
            locks[guild_id] = lock
        return lock

    @staticmethod
    def _queue_item_key(item: Optional[Dict]) -> tuple[str, str, str]:
        if not isinstance(item, dict):
            return ("", "", "")
        return (
            str(item.get("url", "")),
            str(item.get("title", "")),
            str(item.get("local_path", "")),
        )

    def _resolve_announce_channel(
        self,
        guild: discord.Guild,
        channel_id: Optional[int],
    ) -> Optional[object]:
        if not channel_id:
            return None
        channel = guild.get_channel(channel_id) or self.bot.get_channel(channel_id)
        if channel is not None and hasattr(channel, "send"):
            return channel
        return None

    async def _connect_voice_channel(
        self,
        guild: discord.Guild,
        voice_channel: discord.abc.Connectable,
    ) -> discord.VoiceClient:
        guild_id = guild.id
        async with self._get_guild_lock(self.voice_locks, guild_id):
            voice = guild.voice_client
            print(
                f"[voice] connect request | guild={guild_id} | target={voice_channel} | "
                f"existing={'yes' if voice else 'no'}"
            )
            if voice is None:
                voice = await voice_channel.connect(
                    reconnect=False,
                    timeout=12.0,
                    self_deaf=True,
                )
            else:
                if not voice.is_connected():
                    try:
                        await voice.disconnect(force=True)
                    except Exception:
                        pass
                    voice = await voice_channel.connect(
                        reconnect=False,
                        timeout=12.0,
                        self_deaf=True,
                    )
                elif voice.channel != voice_channel:
                    await voice.move_to(voice_channel)

            self.last_voice_channel_id[guild_id] = voice_channel.id
            print(
                f"[voice] connect ok | guild={guild_id} | channel={voice.channel} | "
                f"connected={voice.is_connected()}"
            )
            return voice

    def _schedule_voice_recovery(
        self,
        guild_id: int,
        announce_channel_id: Optional[int] = None,
    ) -> None:
        task = self.voice_recovery_tasks.get(guild_id)
        if task and not task.done():
            return

        self.voice_recovery_tasks[guild_id] = asyncio.create_task(
            self._recover_voice_connection(guild_id, announce_channel_id)
        )

    async def _recover_voice_connection(
        self,
        guild_id: int,
        announce_channel_id: Optional[int] = None,
    ) -> None:
        try:
            await asyncio.sleep(1.5)
            guild = self.bot.get_guild(guild_id)
            if guild is None:
                return

            voice = guild.voice_client
            if voice and voice.is_connected():
                return

            current = self.now_playing.get(guild_id)
            queue = self.get_queue(guild_id)
            if not current:
                return

            recovery_attempt = self.voice_recovery_attempts.get(guild_id, 0) + 1
            self.voice_recovery_attempts[guild_id] = recovery_attempt
            print(
                f"[voice] recovery start | guild={guild_id} | attempt={recovery_attempt} | "
                f"queue={len(queue)} | current={'yes' if current else 'no'}"
            )
            if recovery_attempt > 3:
                channel = self._resolve_announce_channel(guild, announce_channel_id)
                if channel is not None:
                    await channel.send("❌ Voice recovery failed too many times. Please try `/play` again.")
                return

            if current:
                current_key = self._queue_item_key(current)
                queue_head_key = self._queue_item_key(queue[0]) if queue else ("", "", "")
                if current_key != queue_head_key:
                    queue.insert(0, dict(current))

            channel_id = self.last_voice_channel_id.get(guild_id)
            voice_channel = guild.get_channel(channel_id) if channel_id else None
            if not isinstance(voice_channel, (discord.VoiceChannel, discord.StageChannel)):
                return

            channel = self._resolve_announce_channel(
                guild,
                announce_channel_id or (current.get("announce_channel_id") if current else None),
            )
            if channel is not None:
                await channel.send(
                    f"⚠️ Voice connection dropped. Attempting recovery (`{recovery_attempt}/3`)."
                )

            await self._connect_voice_channel(guild, voice_channel)
            await self.play_next(
                guild_id=guild_id,
                announce_channel_id=announce_channel_id or (current.get("announce_channel_id") if current else None),
            )
        except Exception as e:
            print(f"[voice] recovery failed | guild={guild_id} | error={e}")
        finally:
            self.voice_recovery_tasks.pop(guild_id, None)

    def _build_ydl_option_candidates(self, base_opts: Dict[str, object]) -> List[Dict[str, object]]:
        candidates: List[Dict[str, object]] = []
        has_cookie_opts = bool(base_opts.get("cookiesfrombrowser") or base_opts.get("cookiefile"))
        cookie_browser = base_opts.get("cookiesfrombrowser")
        current_browser = ""
        if isinstance(cookie_browser, (list, tuple)) and cookie_browser:
            current_browser = str(cookie_browser[0]).lower()

        # Prefer cookie-less extraction first for runtime stability.
        # Browser cookie databases on Windows are often locked and can delay music playback.
        base_no_cookie = self._without_cookie_options(base_opts)
        candidates.append(base_no_cookie)

        if has_cookie_opts:
            current_locked = bool(current_browser and current_browser in self.locked_cookie_browsers)
            if not current_locked:
                candidates.append(dict(base_opts))

            # Try other browsers if the current profile is locked.
            for browser_name in YTDL_FALLBACK_BROWSERS:
                if (
                    browser_name == current_browser
                    or browser_name in self.locked_cookie_browsers
                ):
                    continue
                candidate = self._without_cookie_options(base_opts)
                candidate["cookiesfrombrowser"] = (browser_name,)
                candidates.append(candidate)
        else:
            # Prefer cookie-less extraction first, then try browser fallbacks.
            for browser_name in YTDL_FALLBACK_BROWSERS:
                if browser_name in self.locked_cookie_browsers:
                    continue
                candidate = dict(base_opts)
                candidate["cookiesfrombrowser"] = (browser_name,)
                candidates.append(candidate)

        expanded_candidates: List[Dict[str, object]] = []
        for candidate in candidates:
            for player_clients in self._candidate_player_client_sets(candidate):
                expanded_candidates.append(
                    self._with_player_clients(candidate, player_clients)
                )

        unique: List[Dict[str, object]] = []
        seen = set()
        for candidate in expanded_candidates:
            key = str(sorted((k, str(v)) for k, v in candidate.items()))
            if key in seen:
                continue
            seen.add(key)
            unique.append(candidate)
        return unique

    async def _extract_info(self, query: str, ydl_opts: Dict[str, object]) -> Dict:
        loop = asyncio.get_running_loop()
        merged_opts = dict(YTDL_OPTIONS)
        merged_opts.update(ydl_opts)

        def _do_extract():
            option_candidates = self._build_ydl_option_candidates(merged_opts)

            last_error: Optional[Exception] = None
            for idx, opts in enumerate(option_candidates):
                try:
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        return ydl.extract_info(query, download=False)
                except Exception as e:
                    last_error = e
                    if self._is_cookie_copy_error(e):
                        browser = opts.get("cookiesfrombrowser")
                        browser_name = "unknown"
                        if isinstance(browser, (list, tuple)) and browser:
                            browser_name = str(browser[0])
                            self.locked_cookie_browsers.add(browser_name.lower())
                        print(
                            f"[yt-dlp] browser cookies locked ({browser_name}); trying fallback source..."
                        )
                    elif idx > 0:
                        print(f"[yt-dlp] extract retry failed: {e}")
            if last_error:
                raise last_error
            raise RuntimeError("yt-dlp extract failed")

        return await loop.run_in_executor(None, _do_extract)

    @staticmethod
    def _escape_ffmpeg_value(value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"')

    def _build_ffmpeg_headers_blob(
        self,
        http_headers: Dict[str, str],
        referer: Optional[str] = None,
    ) -> str:
        header_lines: List[str] = []
        if referer:
            header_lines.append(f"Referer: {referer}")
        for key, value in http_headers.items():
            if not key or value is None:
                continue
            lower_key = str(key).lower()
            if lower_key in {
                "accept-encoding",
                "content-length",
                "transfer-encoding",
                "connection",
                "user-agent",
                "referer",
            }:
                continue
            header_lines.append(f"{key}: {value}")
        if not header_lines:
            return ""
        escaped_lines = [self._escape_ffmpeg_value(line) for line in header_lines]
        return "\\r\\n".join(escaped_lines) + "\\r\\n"

    def _build_before_options(self, http_headers: Optional[Dict[str, str]] = None) -> str:
        before_options = FFMPEG_OPTIONS["before_options"]
        if not http_headers:
            return before_options

        user_agent = http_headers.get("User-Agent") or http_headers.get("user-agent")
        referer = http_headers.get("Referer") or http_headers.get("referer")
        headers_blob = self._build_ffmpeg_headers_blob(
            http_headers,
            str(referer) if referer else None,
        )

        dynamic_options: List[str] = [before_options]
        if user_agent:
            dynamic_options.append(
                f'-user_agent "{self._escape_ffmpeg_value(str(user_agent))}"'
            )
        if headers_blob:
            dynamic_options.append(f'-headers "{headers_blob}"')
        return " ".join(dynamic_options)

    @staticmethod
    def _extract_youtube_video_id(video_url: str) -> Optional[str]:
        try:
            parsed = urlparse(video_url)
        except Exception:
            return None

        host = parsed.netloc.lower()
        if host.endswith("youtu.be"):
            video_id = parsed.path.lstrip("/").split("/")[0]
            return video_id or None

        query_video_ids = parse_qs(parsed.query).get("v")
        if query_video_ids and query_video_ids[0]:
            return query_video_ids[0]

        path_parts = [part for part in parsed.path.split("/") if part]
        for marker in ("shorts", "embed"):
            if marker in path_parts:
                marker_index = path_parts.index(marker)
                if marker_index + 1 < len(path_parts):
                    return path_parts[marker_index + 1]
        return None

    def _find_cached_audio_file(self, video_url: str) -> Optional[str]:
        video_id = self._extract_youtube_video_id(video_url)
        if not video_id:
            return None

        matches = sorted(
            glob.glob(os.path.join(self.music_cache_dir, f"{video_id}.*")),
            key=os.path.getmtime,
            reverse=True,
        )
        for path in matches:
            if os.path.isfile(path):
                try:
                    os.utime(path, None)
                except OSError:
                    pass
                return path
        return None

    def _ffmpeg_is_available(self) -> bool:
        executable = self._get_ffmpeg_executable()
        if os.path.isfile(executable):
            return True
        return shutil.which(executable) is not None

    @staticmethod
    def _pick_stream_url(info: Dict) -> str:
        requested_formats = info.get("requested_formats")
        if isinstance(requested_formats, list):
            for fmt in requested_formats:
                if fmt.get("acodec") != "none" and fmt.get("url"):
                    return str(fmt["url"])

        stream_url = info.get("url")
        if stream_url:
            return stream_url

        formats = info.get("formats", [])
        if isinstance(formats, list):
            for fmt in reversed(formats):
                if fmt.get("acodec") != "none" and fmt.get("url"):
                    return str(fmt["url"])

        raise RuntimeError("No playable audio stream was found for this video.")

    @staticmethod
    def _normalize_video_url(entry: Dict) -> str:
        candidate = entry.get("webpage_url") or entry.get("url")
        if isinstance(candidate, str) and candidate.startswith(("http://", "https://")):
            return candidate

        video_id = entry.get("id")
        if isinstance(video_id, str) and video_id:
            return f"https://www.youtube.com/watch?v={video_id}"

        if isinstance(candidate, str) and candidate:
            return f"https://www.youtube.com/watch?v={candidate}"

        raise RuntimeError("No video could be resolved from the search result.")

    async def youtube_search(self, query: str) -> tuple[str, str, Dict[str, str], str]:
        """Resolve a query or URL into audio metadata."""
        if query.startswith("http://") or query.startswith("https://"):
            ydl_opts = {"format": "bestaudio/best", "noplaylist": True}
            info = await self._extract_info(query, ydl_opts)
            stream_url = self._pick_stream_url(info)
            http_headers = info.get("http_headers")
            if not isinstance(http_headers, dict):
                http_headers = {}
            webpage_url = info.get("webpage_url") if isinstance(info.get("webpage_url"), str) else query
            return stream_url, info.get("title", query), http_headers, webpage_url

        search_opts = {
            "noplaylist": True,
            "extract_flat": "in_playlist",
        }
        search_info = await self._extract_info(f"ytsearch1:{query}", search_opts)
        entries = search_info.get("entries") if isinstance(search_info, dict) else None
        if not isinstance(entries, list) or not entries:
            raise RuntimeError("No results were found for that query.")

        target_url = self._normalize_video_url(entries[0])
        info = await self._extract_info(
            target_url,
            {"format": "bestaudio/best", "noplaylist": True},
        )

        stream_url = self._pick_stream_url(info)
        http_headers = info.get("http_headers")
        if not isinstance(http_headers, dict):
            http_headers = {}
        webpage_url = info.get("webpage_url")
        if not isinstance(webpage_url, str):
            webpage_url = target_url
        return stream_url, info.get("title", query), http_headers, webpage_url

    async def download_audio_file(self, video_url: str) -> Optional[str]:
        loop = asyncio.get_running_loop()
        cached_path = self._find_cached_audio_file(video_url)
        if cached_path:
            print(f"[music] reuse local audio: {cached_path}")
            return cached_path

        def _download() -> Optional[str]:
            base_opts: Dict[str, object] = {
                "format": "bestaudio[acodec=opus]/bestaudio/best",
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
                "logger": YTDL_LOGGER,
                "proxy": YTDL_PROXY,
                "outtmpl": os.path.join(self.music_cache_dir, "%(id)s.%(ext)s"),
                "overwrites": True,
            }
            if YTDL_COOKIES_FILE and os.path.isfile(YTDL_COOKIES_FILE):
                base_opts["cookiefile"] = YTDL_COOKIES_FILE
            if YTDL_COOKIES_BROWSER:
                base_opts["cookiesfrombrowser"] = (YTDL_COOKIES_BROWSER,)
            base_opts["extractor_args"] = {
                "youtube": {"player_client": YTDL_PLAYER_CLIENTS or ["android", "ios", "web"]}
            }

            option_candidates = self._build_ydl_option_candidates(base_opts)

            last_error: Optional[Exception] = None
            for idx, ydl_opts in enumerate(option_candidates):
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(video_url, download=True)
                        path = ydl.prepare_filename(info)

                        if os.path.isfile(path):
                            return path

                        requested = info.get("requested_downloads")
                        if isinstance(requested, list):
                            for item in requested:
                                filepath = item.get("filepath")
                                if isinstance(filepath, str) and os.path.isfile(filepath):
                                    return filepath
                    return None
                except Exception as e:
                    last_error = e
                    if self._is_cookie_copy_error(e):
                        browser = ydl_opts.get("cookiesfrombrowser")
                        browser_name = "unknown"
                        if isinstance(browser, (list, tuple)) and browser:
                            browser_name = str(browser[0])
                            self.locked_cookie_browsers.add(browser_name.lower())
                        print(
                            f"[yt-dlp] browser cookies locked while downloading ({browser_name}); trying fallback source..."
                        )
                    elif idx > 0:
                        print(f"[yt-dlp] download retry failed: {e}")

            if last_error:
                raise last_error
            return None

        downloaded_path = await loop.run_in_executor(None, _download)
        if downloaded_path:
            self._prune_music_cache()
        return downloaded_path

    def get_queue(self, guild_id: int) -> List[Dict]:
        return self.queues.setdefault(guild_id, [])

    async def ensure_voice(self, interaction: discord.Interaction) -> Optional[discord.VoiceClient]:
        if interaction.guild is None:
            await interaction.followup.send(
                "This command can only be used in servers.", ephemeral=True
            )
            return None
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("❌ You must be in a voice channel first.", ephemeral=True)
            return None

        voice_channel = interaction.user.voice.channel
        me = interaction.guild.me or interaction.guild.get_member(self.bot.user.id)
        if me:
            perms = voice_channel.permissions_for(me)
            if not perms.connect:
                await interaction.followup.send(
                    f"❌ The bot does not have Connect permission for `{voice_channel.name}`.",
                    ephemeral=True,
                )
                return None
            if not perms.speak:
                await interaction.followup.send(
                    f"❌ The bot does not have Speak permission for `{voice_channel.name}`.",
                    ephemeral=True,
                )
                return None

        guild_id = interaction.guild.id
        try:
            voice = await self._connect_voice_channel(interaction.guild, voice_channel)
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "❌ Voice connection timed out.",
                ephemeral=True,
            )
            return None
        except discord.ClientException as e:
            await interaction.followup.send(
                f"❌ Voice connection failed: `{e}`",
                ephemeral=True,
            )
            return None
        except Exception as e:
            print(f"[voice] connect failed | guild={guild_id} | error={e!r}")
            await interaction.followup.send(
                f"❌ Voice connection failed (`{type(e).__name__}`).",
                ephemeral=True,
            )
            return None

        self.voice_recovery_attempts[guild_id] = 0

        if isinstance(voice.channel, discord.StageChannel):
            await self._ensure_stage_voice_ready(
                interaction.guild,
                announce_channel=self._resolve_announce_channel(
                    interaction.guild,
                    interaction.channel_id,
                ),
            )

        return voice

    async def play_next(
        self,
        interaction: Optional[discord.Interaction] = None,
        *,
        guild_id: Optional[int] = None,
        announce_channel_id: Optional[int] = None,
    ):
        guild: Optional[discord.Guild] = None
        if interaction is not None:
            guild = interaction.guild
            guild_id = interaction.guild_id
            if announce_channel_id is None:
                announce_channel_id = interaction.channel_id
        elif guild_id is not None:
            guild = self.bot.get_guild(guild_id)

        if guild is None or guild_id is None:
            return

        async with self._get_guild_lock(self.play_locks, guild_id):
            queue = self.get_queue(guild_id)
            if not queue:
                await self._disable_now_playing_message(guild_id, footer_text="Queue finished")
                return

            item = queue[0]
            target_voice_channel_id = item.get("voice_channel_id") or self.last_voice_channel_id.get(guild_id)
            target_voice_channel = guild.get_channel(target_voice_channel_id) if target_voice_channel_id else None
            voice = guild.voice_client

            if (voice is None or not voice.is_connected()) and isinstance(
                target_voice_channel,
                (discord.VoiceChannel, discord.StageChannel),
            ):
                try:
                    voice = await self._connect_voice_channel(guild, target_voice_channel)
                except Exception as e:
                    print(f"[voice] reconnect before play failed | guild={guild_id} | error={e}")
                    self._schedule_voice_recovery(guild_id, announce_channel_id)
                    return

            if not voice or not voice.is_connected():
                return

            if voice.is_playing() or voice.is_paused():
                return

            item = queue.pop(0)
            pending_stage = self.pending_stage_routes.get(guild_id)
            pending_requester_id = None
            if pending_stage:
                pending_requester_id = pending_stage.get("requester_id")
            item_requester_id = getattr(item.get("requested_by"), "id", None)
            if (
                pending_stage
                and pending_stage.get("stage_channel_id") == item.get("voice_channel_id")
                and pending_requester_id == item_requester_id
            ):
                self.pending_stage_routes.pop(guild_id, None)
            url = item["url"]
            title = item["title"]
            user = item["requested_by"]
            http_headers = item.get("http_headers")
            local_path = item.get("local_path")
            effective_channel_id = announce_channel_id or item.get("announce_channel_id")
            channel = self._resolve_announce_channel(guild, effective_channel_id) or user.dm_channel
            if isinstance(getattr(voice, "channel", None), discord.StageChannel):
                await self._ensure_stage_voice_ready(guild, announce_channel=channel)
            stderr_capture = FFmpegStderrBuffer(max_lines=25)
            started_at = time.monotonic()
            source = None
            self.now_playing[guild_id] = dict(item)
            ffmpeg_play_options = self._build_ffmpeg_play_options(guild_id)

            def after_play(err):
                elapsed = time.monotonic() - started_at
                stderr_tail = stderr_capture.tail(4)
                intentional_stop = self.intentional_track_stops.pop(guild_id, "")
                if err:
                    print(f"Player error: {err}")
                    if channel is not None:
                        msg = f"❌ Failed to play `{title}`: `{err}`"
                        if stderr_tail:
                            msg += f"\n```{stderr_tail[:800]}```"
                        asyncio.run_coroutine_threadsafe(
                            channel.send(msg),
                            self.bot.loop,
                        )
                else:
                    print(f"[music] finished: {title}")
                    if intentional_stop:
                        print(
                            f"[music] intentional stop ignored | guild={guild_id} | "
                            f"title={title} | reason={intentional_stop}"
                        )
                    elif elapsed < 5 and channel is not None:
                        reason = (
                            f"⚠️ `{title}` stopped unusually early ({elapsed:.1f}s)."
                        )
                        if stderr_tail:
                            reason += f"\n```{stderr_tail[:800]}```"
                        if not stderr_tail:
                            reason += (
                                "\nTry setting `.env` to "
                                "`YTDL_COOKIES_BROWSER=chrome` and restart the bot."
                            )
                        asyncio.run_coroutine_threadsafe(
                            channel.send(reason),
                            self.bot.loop,
                        )
                self.now_playing.pop(guild_id, None)
                self._schedule_local_audio_cleanup(local_path, delay_seconds=2.0)
                fut = self.play_next(
                    guild_id=guild_id,
                    announce_channel_id=effective_channel_id,
                )
                asyncio.run_coroutine_threadsafe(fut, self.bot.loop)

            try:
                if isinstance(local_path, str) and os.path.isfile(local_path):
                    source = discord.FFmpegOpusAudio(
                        local_path,
                        executable=FFMPEG_EXECUTABLE,
                        options=ffmpeg_play_options,
                        stderr=stderr_capture,
                    )
                else:
                    source = discord.FFmpegOpusAudio(
                        url,
                        executable=FFMPEG_EXECUTABLE,
                        before_options=self._build_before_options(http_headers),
                        options=ffmpeg_play_options,
                        stderr=stderr_capture,
                    )
                voice.play(source, after=after_play)
                eq = self._get_guild_eq(guild_id)
                print(
                    f"[music] started: {title} | guild={guild_id} | "
                    f"voice={voice.channel} | opus_loaded={discord.opus.is_loaded()} | "
                    f"source_is_opus={source.is_opus()} | "
                    f"speed={self._get_guild_speed(guild_id):.2f} | "
                    f"bass={eq['bass_db']:+.1f}dB | "
                    f"treble={eq['treble_db']:+.1f}dB"
                )
                self.voice_recovery_attempts[guild_id] = 0
            except discord.ClientException as e:
                if "Already playing audio" in str(e):
                    return
                self.now_playing.pop(guild_id, None)
                self._schedule_local_audio_cleanup(local_path, delay_seconds=1.0)
                if channel is not None:
                    await channel.send(f"❌ Could not play `{title}`: `{e}`")
                asyncio.get_running_loop().create_task(
                    self.play_next(
                        guild_id=guild_id,
                        announce_channel_id=effective_channel_id,
                    )
                )
                return
            except Exception as e:
                self.now_playing.pop(guild_id, None)
                self._schedule_local_audio_cleanup(local_path, delay_seconds=1.0)
                if channel is not None:
                    await channel.send(f"❌ Could not play `{title}`: `{e}`")
                asyncio.get_running_loop().create_task(
                    self.play_next(
                        guild_id=guild_id,
                        announce_channel_id=effective_channel_id,
                    )
                )
                return

        if channel is not None:
            embed = self.music_room.build_now_playing_embed(
                item=item,
                voice_channel=getattr(voice, "channel", None),
                guild_id=guild_id,
            )
            await self._publish_now_playing_message(
                guild_id,
                channel,
                embed=embed,
            )

    @app_commands.command(name="play", description="Play music from YouTube by link or search query")
    @app_commands.describe(
        query="A YouTube link or search query",
        route="Choose whether the bot joins your room or uses its own Stage room",
    )
    @app_commands.choices(
        route=[
            app_commands.Choice(name="auto - best route", value="auto"),
            app_commands.Choice(name="join - join my current room", value="join"),
            app_commands.Choice(name="bot_stage - use the bot Stage room", value="bot_stage"),
        ]
    )
    async def play(
        self,
        interaction: discord.Interaction,
        query: str,
        route: Optional[app_commands.Choice[str]] = None,
    ):
        await self.music_room.play(
            interaction,
            query,
            route.value if route is not None else "auto",
        )

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        await self.music_room.handle_voice_state_update(member, before, after)



    @app_commands.command(name="skip", description="Skip the current track")
    async def skip(self, interaction: discord.Interaction):
        await self.music_room.skip(interaction)

    @app_commands.command(name="stop", description="Stop playback and clear the queue")
    async def stop(self, interaction: discord.Interaction):
        await self.music_room.stop(interaction)

    @app_commands.command(name="pause", description="Pause playback")
    async def pause(self, interaction: discord.Interaction):
        await self.music_room.pause(interaction)

    @app_commands.command(name="resume", description="Resume playback")
    async def resume(self, interaction: discord.Interaction):
        await self.music_room.resume(interaction)

    @app_commands.command(
        name="speed",
        description="Adjust playback speed from 0.5x to 2.0x",
    )
    async def set_speed(
        self,
        interaction: discord.Interaction,
        value: app_commands.Range[float, 0.5, 2.0],
    ):
        await self.music_room.set_speed(interaction, float(value))

    @app_commands.command(
        name="tone",
        description="Apply a preset tone profile",
    )
    @app_commands.describe(mode="Choose the tone preset")
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="normal", value="normal"),
            app_commands.Choice(name="bass", value="bass"),
            app_commands.Choice(name="treble", value="treble"),
        ]
    )
    async def set_tone(
        self,
        interaction: discord.Interaction,
        mode: app_commands.Choice[str],
    ):
        await self.music_room.set_tone(interaction, mode)

    @app_commands.command(
        name="eq",
        description="Adjust bass and treble manually in dB",
    )
    @app_commands.describe(
        bass_db="Range: -20 to 20 dB",
        treble_db="Range: -20 to 20 dB",
    )
    async def set_eq(
        self,
        interaction: discord.Interaction,
        bass_db: app_commands.Range[float, -20.0, 20.0],
        treble_db: app_commands.Range[float, -20.0, 20.0],
    ):
        await self.music_room.set_eq(
            interaction,
            float(bass_db),
            float(treble_db),
        )

    @app_commands.command(name="audio_profile", description="Show the current audio profile")
    async def audio_profile(self, interaction: discord.Interaction):
        await self.music_room.audio_profile(interaction)

    @app_commands.command(name="queue", description="Show the music queue")
    async def queue_cmd(self, interaction: discord.Interaction):
        await self.music_room.queue_cmd(interaction)

    @app_commands.command(name="mdebug", description="Show music and voice debug status")
    async def music_debug(self, interaction: discord.Interaction):
        await self.music_room.music_debug(interaction)

    @app_commands.command(name="testtone", description="Play an 8-second voice test tone")
    async def test_tone(self, interaction: discord.Interaction):
        await self.music_room.test_tone(interaction)

    @staticmethod
    def _trim_output(text: str, max_chars: int = 900) -> str:
        cleaned = text.strip().replace("```", "'''")
        if not cleaned:
            return "-"
        if len(cleaned) <= max_chars:
            return cleaned
        return cleaned[:max_chars] + "\n... (truncated)"

    async def _can_manage_bot(self, interaction: discord.Interaction) -> bool:
        try:
            if await self.bot.is_owner(interaction.user):
                return True
        except Exception:
            pass

        if isinstance(interaction.user, discord.Member):
            return interaction.user.guild_permissions.administrator
        return False

    async def _request_restart(self, reason: str):
        global PROCESS_EXIT_CODE
        PROCESS_EXIT_CODE = RESTART_EXIT_CODE
        print(f"[restart] requested: {reason}")
        await self.bot.close()

    async def _run_subprocess(
        self, command: List[str], cwd: str
    ) -> subprocess.CompletedProcess[str]:
        return await asyncio.to_thread(
            subprocess.run,
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

    @app_commands.command(name="restart", description="Restart the bot (owner/admin)")
    async def restart_bot(self, interaction: discord.Interaction):
        if not await self._can_manage_bot(interaction):
            await interaction.response.send_message(
                "❌ This command is restricted to the owner or admins.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message("♻️ Restarting the bot...", ephemeral=True)
        await self._request_restart(f"/restart by {interaction.user}")

    @app_commands.command(name="selfupdate", description="Pull the latest code and restart (owner/admin)")
    async def self_update(self, interaction: discord.Interaction, install_requirements: bool = True):
        if not await self._can_manage_bot(interaction):
            await interaction.response.send_message(
                "❌ This command is restricted to the owner or admins.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        project_root = os.path.dirname(os.path.abspath(__file__))
        git_path = shutil.which("git")
        if not git_path:
            await interaction.followup.send(
                "❌ `git` was not found on this system.",
                ephemeral=True,
            )
            return
        if not os.path.isdir(os.path.join(project_root, ".git")):
            await interaction.followup.send(
                "❌ This folder is not a git repository (`.git` not found).",
                ephemeral=True,
            )
            return

        pull_result = await self._run_subprocess(
            [git_path, "pull", "--ff-only"],
            cwd=project_root,
        )
        pull_stdout = pull_result.stdout or ""
        pull_stderr = pull_result.stderr or ""
        pull_output = (pull_stdout + "\n" + pull_stderr).strip()
        pull_output_short = self._trim_output(pull_output, max_chars=600)
        if pull_result.returncode != 0:
            await interaction.followup.send(
                f"❌ `git pull --ff-only` failed.\n```{pull_output_short}```",
                ephemeral=True,
            )
            return

        if "already up to date" in pull_output.lower() or "already up-to-date" in pull_output.lower():
            await interaction.followup.send("✅ The code is already up to date.", ephemeral=True)
            return

        deps_msg = "⏭ Dependency installation skipped."
        if install_requirements and os.path.isfile(os.path.join(project_root, "requirements.txt")):
            pip_result = await self._run_subprocess(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                cwd=project_root,
            )
            pip_output = ((pip_result.stdout or "") + "\n" + (pip_result.stderr or "")).strip()
            pip_output_short = self._trim_output(pip_output, max_chars=500)
            if pip_result.returncode == 0:
                deps_msg = "✅ Dependencies installed successfully."
            else:
                deps_msg = f"⚠️ Dependency installation failed.\n```{pip_output_short}```"

        await interaction.followup.send(
            f"✅ Code updated successfully.\n```{pull_output_short}```\n{deps_msg}\n♻️ Restarting the bot...",
            ephemeral=True,
        )
        await self._request_restart(f"/selfupdate by {interaction.user}")

    @app_commands.command(name="leave", description="Disconnect the bot from voice")
    async def leave(self, interaction: discord.Interaction):
        await self.music_room.leave(interaction)

    @app_commands.command(name="clear", description="Delete messages in this channel (up to 100)")
    async def clear_slash(self, interaction: discord.Interaction, amount: int):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in servers.", ephemeral=True
            )
            return
        if amount < 1:
            await interaction.response.send_message(
                "Please specify a number between 1 and 100.", ephemeral=True
            )
            return
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "❌ You do not have permission to delete messages.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        try:
            deleted = await interaction.channel.purge(limit=min(amount, 100))
        except (discord.Forbidden, discord.HTTPException):
            await interaction.followup.send(
                "I could not delete messages here. Check the bot permissions.", ephemeral=True
            )
            return
        await interaction.followup.send(
            f"🧹 Deleted {len(deleted)} message(s).", ephemeral=True
        )

    # ---------- Slash: Tic-Tac-Toe ----------

    @staticmethod
    def _winner(board: list[str]) -> Optional[str]:
        wins = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]
        for a, b, c in wins:
            if board[a] != " " and board[a] == board[b] == board[c]:
                return board[a]
        return None

    @staticmethod
    def _is_full(board: list[str]) -> bool:
        return all(cell != " " for cell in board)

    @staticmethod
    def _symbol_to_emoji(symbol: str) -> str:
        if symbol == "X":
            return "❌"
        if symbol == "O":
            return "⭕"
        return "⬜"

    def _update_view_from_board(self, view: OXView, board: list[str], lock_all: bool = False):
        for i, child in enumerate(view.children):
            if isinstance(child, discord.ui.Button):
                symbol = board[i]
                child.label = self._symbol_to_emoji(symbol)
                if board[i] != " ":
                    child.disabled = True
                if lock_all:
                    child.disabled = True

    def _best_move(self, board: list[str], bot_sym: str, player_sym: str) -> int:
        # Simple minimax search.

        def minimax(bd: list[str], is_bot_turn: bool) -> int:
            winner = self._winner(bd)
            if winner == bot_sym:
                return 1
            if winner == player_sym:
                return -1
            if self._is_full(bd):
                return 0

            if is_bot_turn:
                best_score = -999
                for i in range(9):
                    if bd[i] == " ":
                        bd[i] = bot_sym
                        score = minimax(bd, False)
                        bd[i] = " "
                        best_score = max(best_score, score)
                return best_score
            else:
                best_score = 999
                for i in range(9):
                    if bd[i] == " ":
                        bd[i] = player_sym
                        score = minimax(bd, True)
                        bd[i] = " "
                        best_score = min(best_score, score)
                return best_score

        best_score = -999
        move = -1
        for i in range(9):
            if board[i] == " ":
                board[i] = bot_sym
                score = minimax(board, False)
                board[i] = " "
                if score > best_score:
                    best_score = score
                    move = i
        # Fall back to the first open slot if something unexpected happens.
        if move == -1:
            for i in range(9):
                if board[i] == " ":
                    move = i
                    break
        return move

    async def _bot_move(self, interaction: discord.Interaction, user_id: int):
        game = self.games.get(user_id)
        if not game:
            return

        board: list[str] = game["board"]
        view: OXView = game["view"]
        bot_sym: str = game["bot_sym"]
        player_sym: str = game["player_sym"]

        # Do not move if the game is already finished.
        if self._winner(board) or self._is_full(board):
            return

        idx = self._best_move(board, bot_sym, player_sym)
        if board[idx] != " ":
            return

        board[idx] = bot_sym

        winner = self._winner(board)
        is_full = self._is_full(board)

        msg: discord.Message = game["message"]

        if winner or is_full:
            self._update_view_from_board(view, board, lock_all=True)
            if winner == bot_sym:
                await msg.edit(content="🤖 I win!", view=view)
            elif winner == player_sym:
                await msg.edit(content="😲 You beat me!", view=view)
            else:
                await msg.edit(content="🤝 It's a draw.", view=view)
            return
        else:
            self._update_view_from_board(view, board)
            await msg.edit(content="Your turn. (❌)", view=view)
            game["turn"] = "player"

    async def handle_player_move(self, interaction: discord.Interaction, index: int):
        user_id = interaction.user.id
        game = self.games.get(user_id)

        if not game:
            await interaction.response.send_message("❌ You have not started a game yet. Use `/ox_start` first.", ephemeral=True)
            return

        if interaction.user.id != game["user_id"]:
            await interaction.response.send_message("❌ This is not your game.", ephemeral=True)
            return

        board: list[str] = game["board"]
        view: OXView = game["view"]
        player_sym: str = game["player_sym"]
        bot_sym: str = game["bot_sym"]
        turn: str = game["turn"]
        msg: discord.Message = game["message"]

        if turn != "player":
            await interaction.response.send_message("⏳ It is not your turn yet.", ephemeral=True)
            return

        if board[index] != " ":
            await interaction.response.send_message("❌ That square is already taken.", ephemeral=True)
            return

        board[index] = player_sym
        winner = self._winner(board)
        is_full = self._is_full(board)

        if winner or is_full:
            self._update_view_from_board(view, board, lock_all=True)
            if winner == player_sym:
                await interaction.response.edit_message(content="🎉 You win!", view=view)
                print("Human winner")
            elif winner == bot_sym:
                await interaction.response.edit_message(content="🤖 I win!", view=view)
                print("bot winner")
            else:
                await interaction.response.edit_message(content="🤝 It's a draw.", view=view)
                print("Bot = Human")
            return
        else:
            self._update_view_from_board(view, board)
            await interaction.response.edit_message(content="My turn. (⭕)", view=view)
            game["turn"] = "bot"
            await self._bot_move(interaction, user_id)

    @app_commands.command(name="ox_start", description="Start a Tic-Tac-Toe match against the bot")
    async def ox_start(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        starter = self.next_starter.get(user_id, "player")
        self.next_starter[user_id] = "bot" if starter == "player" else "player"

        board = [" "] * 9
        player_sym = "X"
        bot_sym = "O"

        view = OXView(self, user_id)

        if starter == "player":
            text = "Tic-Tac-Toe started. 🎮\nYou go first. (❌)"
        else:
            text = "Tic-Tac-Toe started. 🎮\nI go first. (⭕)"

        await interaction.response.send_message(text, view=view)
        msg = await interaction.original_response()

        self.games[user_id] = {
            "user_id": user_id,
            "board": board,
            "player_sym": player_sym,
            "bot_sym": bot_sym,
            "turn": "player" if starter == "player" else "bot",
            "message": msg,
            "view": view,
        }

        if starter == "bot":
            await self._bot_move(interaction, user_id)

# ==========================
#  BACKGROUND STATUS TASK
# ==========================

@tasks.loop(seconds=6)
async def change_bot_status():
    await bot.change_presence(activity=discord.Game(next(status_messages)))

class ControlButton(discord.ui.Button):
    def __init__(self, label: str, style: discord.ButtonStyle):
        super().__init__(label=label, style=style)

    async def callback(self, interaction: discord.Interaction):
        view: "ChessView" = self.view  # type: ignore
        if self.label == "🏳 Resign":
            await view.cog.handle_resign(interaction, view.game_id)
        elif self.label == "🤝 Offer Draw":
            await view.cog.handle_draw_request(interaction, view.game_id)


class ChessView(discord.ui.View):
    def __init__(self, cog: "ChessCog", game_id: int):
        super().__init__(timeout=1800)
        self.cog = cog
        self.game_id = game_id

        self.add_item(ControlButton("🏳 Resign", discord.ButtonStyle.danger))
        self.add_item(ControlButton("🤝 Offer Draw", discord.ButtonStyle.success))

    async def on_timeout(self):
        game = self.cog.games.get(self.game_id)
        if not game:
            return
        msg = game.get("message")
        if msg:
            for c in self.children:
                if isinstance(c, discord.ui.Button):
                    c.disabled = True
            await msg.edit(content="⌛ The game timed out.", view=self)

class ChessCog(commands.Cog):
    """Chess commands and game state management."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.games: dict[int, dict] = {}
        self.game_counter = 0

    def _board_to_text(self, board: chess.Board) -> str:
        return "```" + board.unicode(borders=True) + "```"

    def _format_clock(self, seconds: float) -> str:
        seconds = max(0, int(seconds))
        m = seconds // 60
        s = seconds % 60
        return f"{m:02d}:{s:02d}"

    def _current_clocks_text(self, game: dict) -> str:
        w_time = game["white_time"]
        b_time = game["black_time"]
        return f"⏱ White {self._format_clock(w_time)} | Black {self._format_clock(b_time)}"

    def _apply_clock(self, game: dict):
        now = time.time()
        last = game["last_time"]
        dt = now - last
        if game["board"].turn == chess.WHITE:
            game["white_time"] -= dt
        else:
            game["black_time"] -= dt
        game["last_time"] = now

    @app_commands.command(name="zchess", description="Start a chess game against the bot or a friend")
    @app_commands.describe(
        mode="vs_bot to play the bot, or vs_friend to play another user",
        opponent="Tag a friend when using vs_friend",
        minutes="Time control in minutes per side",
    )
    async def chess_start(
        self,
        interaction: discord.Interaction,
        mode: str,
        opponent: Optional[discord.Member],
        minutes: int = 5,
    ):
        if mode not in ("vs_bot", "vs_friend"):
            await interaction.response.send_message("Mode must be `vs_bot` or `vs_friend`.", ephemeral=True)
            return

        if mode == "vs_friend" and (opponent is None or opponent.bot):
            await interaction.response.send_message("`vs_friend` requires a tagged user who is not a bot.", ephemeral=True)
            return

        await interaction.response.defer()

        board = chess.Board()
        self.game_counter += 1
        game_id = self.game_counter

        total_seconds = minutes * 60
        now = time.time()

        if mode == "vs_bot":
            white_id = interaction.user.id
            black_id = self.bot.user.id
        else:
            white_id = interaction.user.id
            black_id = opponent.id

        view = ChessView(self, game_id)
        game = {
            "id": game_id,
            "board": board,
            "white_id": white_id,
            "black_id": black_id,
            "mode": mode,
            "white_time": total_seconds,
            "black_time": total_seconds,
            "last_time": now,
            "message": None,
            "draw_offered_by": None,
        }
        self.games[game_id] = game

        text = (
            f"♟ New game started. White: <@{white_id}> | Black: <@{black_id}>\n"
            f"Use `/zmove`, for example `/zmove move:e2e4`\n\n"
            f"{self._board_to_text(board)}\n"
            f"{self._current_clocks_text(game)}"
        )
        msg = await interaction.followup.send(text, view=view)
        game["message"] = msg

    @app_commands.command(name="zmove", description="Make a move in chess, for example e2e4")
    async def zmove(self, interaction: discord.Interaction, move: str):
        game = None
        for g in self.games.values():
            if interaction.user.id in (g["white_id"], g["black_id"]):
                game = g
                break

        if not game:
            await interaction.response.send_message("You do not have an active game. Use `/zchess` first.", ephemeral=True)
            return

        board: chess.Board = game["board"]
        self._apply_clock(game)

        raw = move.strip().lower()
        raw = raw.replace(" ", "").replace("-", "")
        raw = raw.replace("x", "")

        if len(raw) not in (4, 5):
            await interaction.response.send_message(
                "Invalid move format. Use `e2e4`, `g1f3`, or `e7e8q` for promotion.",
                ephemeral=True,
            )
            return

        try:
            mv = chess.Move.from_uci(raw)
        except ValueError:
            await interaction.response.send_message(
                "Invalid move format. Use `e2e4`, `g1f3`, or `e7e8q` for promotion.",
                ephemeral=True,
            )
            return

        if mv not in board.legal_moves:
            await interaction.response.send_message(
                "That move is not legal in the current position.\n"
                "- Make sure a piece exists on the source square\n"
                "- Make sure it is your turn\n"
                "- Make sure the path is not blocked",
                ephemeral=True,
            )
            return

        board: chess.Board = game["board"]
        self._apply_clock(game)

        if game["white_time"] <= 0:
            await interaction.response.send_message("⏱ White ran out of time. Black wins.", ephemeral=False)
            await self._end_game(game["id"])
            return
        if game["black_time"] <= 0:
            await interaction.response.send_message("⏱ Black ran out of time. White wins.", ephemeral=False)
            await self._end_game(game["id"])
            return

        user_id = interaction.user.id
        turn_color = board.turn  # True=white, False=black

        if turn_color == chess.WHITE and user_id != game["white_id"]:
            await interaction.response.send_message("It is White's turn.", ephemeral=True)
            return
        if turn_color == chess.BLACK and user_id != game["black_id"]:
            await interaction.response.send_message("It is Black's turn.", ephemeral=True)
            return

        try:
            mv = chess.Move.from_uci(move.lower())
        except ValueError:
            await interaction.response.send_message("Invalid move format. Use `e2e4`.", ephemeral=True)
            return

        if mv not in board.legal_moves:
            await interaction.response.send_message("That move is not legal.", ephemeral=True)
            return

        board.push(mv)

        if game["mode"] == "vs_bot" and not board.is_game_over():
            if (board.turn == chess.WHITE and game["white_id"] == self.bot.user.id) or (
                board.turn == chess.BLACK and game["black_id"] == self.bot.user.id
            ):
                bot_move = self._choose_bot_move(board)
                board.push(bot_move)

        text = self._board_to_text(board) + "\n" + self._current_clocks_text(game)

        if board.is_checkmate():
            winner = "White" if board.turn == chess.BLACK else "Black"
            text = f"🏁 Checkmate. {winner} wins.\n" + text
            await interaction.response.send_message(text)
            await self._end_game(game["id"])
        elif board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves():
            text = "🤝 The game ended in a draw.\n" + text
            await interaction.response.send_message(text)
            await self._end_game(game["id"])
        else:
            await interaction.response.send_message(text)

        msg = game.get("message")
        if msg:
            await msg.edit(content="♟ Chess Game\n" + text, view=msg.view)

    def _choose_bot_move(self, board: chess.Board) -> chess.Move:
        capture_moves = [m for m in board.legal_moves if board.is_capture(m)]
        if capture_moves:
            return random.choice(capture_moves)
        return random.choice(list(board.legal_moves))

    async def _end_game(self, game_id: int):
        game = self.games.pop(game_id, None)
        if not game:
            return
        msg = game.get("message")
        if msg:
            view: ChessView = msg.view
            for c in view.children:
                if isinstance(c, discord.ui.Button):
                    c.disabled = True
            try:
                await msg.edit(view=view)
            except Exception:
                pass

    async def handle_resign(self, interaction: discord.Interaction, game_id: int):
        game = self.games.get(game_id)
        if not game:
            await interaction.response.send_message("That game no longer exists.", ephemeral=True)
            return
        user_id = interaction.user.id
        if user_id not in (game["white_id"], game["black_id"]):
            await interaction.response.send_message("This is not your game.", ephemeral=True)
            return
        winner = game["black_id"] if user_id == game["white_id"] else game["white_id"]
        await interaction.response.send_message(
            f"<@{user_id}> resigned. Winner: <@{winner}>.", ephemeral=False
        )
        await self._end_game(game_id)

    async def handle_draw_request(self, interaction: discord.Interaction, game_id: int):
        game = self.games.get(game_id)
        if not game:
            await interaction.response.send_message("That game no longer exists.", ephemeral=True)
            return
        user_id = interaction.user.id
        if user_id not in (game["white_id"], game["black_id"]):
            await interaction.response.send_message("This is not your game.", ephemeral=True)
            return
        if game["draw_offered_by"] is None:
            game["draw_offered_by"] = user_id
            await interaction.response.send_message(
                "Draw offered. Waiting for the other player to accept.", ephemeral=True
            )
        else:
            if game["draw_offered_by"] == user_id:
                await interaction.response.send_message(
                    "You already offered a draw. Wait for the other player to respond.", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "🤝 Both players agreed to a draw.", ephemeral=False
                )
                await self._end_game(game_id)

# ==========================
#  EVENTS
# ==========================

@bot.event
async def on_ready():
    if not change_bot_status.is_running():
        change_bot_status.start()

    try:
        # Sync global commands so they are available in every guild.
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} GLOBAL slash commands")
        print([cmd.name for cmd in synced])
    except Exception as e:
        print(f"Slash sync error: {e}") 

    print("=================================================================================")
    print(f" Logged in as: {bot.user} (ID: {bot.user.id})")
    print(f" Ping: < {round(bot.latency * 1000)} > ms")
    music_summary = music_runtime_summary()
    print(
        f" Music ytdlp clients: {','.join(music_summary['clients'])} | "
        f"cookies: {music_summary['cookies_mode']}"
    )
    print(f" Music ffmpeg: {FFMPEG_EXECUTABLE}")
    print(f" Music ytdlp fallback browsers: {','.join(music_summary['fallback_browsers'])}")
    print(
        f" Music voice runtime: davey={music_summary['davey_available']} | "
        f"supports_non_stage={music_summary['supports_non_stage_voice']}"
    )
    slash_cog = bot.get_cog("SlashCog")
    if slash_cog is not None:
        print(
            " Music local audio policy: "
            f"{round(slash_cog.music_cache_max_bytes / (1024 * 1024))}MB / "
            f"{slash_cog.music_cache_max_age_hours}h | "
            f"delete_after_play={slash_cog.music_delete_after_play}"
        )
    print(f" Music allow unsafe non-stage: {music_summary['allow_unsafe_non_stage']}")
    print("=================================================================================")


@bot.event
async def on_member_join(member: discord.Member):
    print("________________________ [ member new join ] ________________________")
    channel = member.guild.system_channel
    if channel is None:
        return

    background = Editor(random.choice(JPG_NAME))
    profile_image = await load_image_async(str(member.display_avatar.url))

    profile = Editor(profile_image).resize((315, 315)).circle_image()
    poppins = Font.poppins(size=75, variant="bold")
    poppins_small = Font.poppins(size=30, variant="bold")

    background.paste(profile, (483, 55))
    background.ellipse((483, 55), 315, 315, outline="white", stroke_width=8)

    background.text(
        (600, 390),
        f"Welcome to {member.guild.name}",
        color="white",
        font=poppins,
        align="center",
    )
    background.text(
        (600, 500),
        f"Welcome {member.name}#{member.discriminator} for member",
        color="pink",
        font=poppins_small,
        align="center",
    )

    file = File(fp=background.image_bytes, filename="welcome.jpg")
    await channel.send(file=file)


@bot.event
async def on_member_remove(member: discord.Member):
    print("________________________ [ member removed ] ________________________")
    channel = member.guild.system_channel
    if channel is None:
        return

    background = Editor(random.choice(JPG_NAME))
    profile_image = await load_image_async(str(member.display_avatar.url))

    profile = Editor(profile_image).resize((315, 315)).circle_image()
    poppins = Font.poppins(size=75, variant="bold")
    poppins_small = Font.poppins(size=30, variant="bold")

    background.paste(profile, (483, 55))
    background.ellipse((483, 55), 315, 315, outline="white", stroke_width=8)

    background.text(
        (600, 390),
        f"Leave server {member.guild.name}",
        color="white",
        font=poppins,
        align="center",
    )
    background.text(
        (600, 500),
        f"Goodbye {member.name}#{member.discriminator}",
        color="pink",
        font=poppins_small,
        align="center",
    )

    file = File(fp=background.image_bytes, filename="leave.jpg")
    await channel.send(file=file)


# ==========================
#  ERROR HANDLERS
# ==========================

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    print(error)

    async def _safe_delete():
        if ctx.guild is None:
            return
        me = ctx.guild.me
        if me is None:
            return
        if not ctx.channel.permissions_for(me).manage_messages:
            return
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("I can't answer your problem.")
        await _safe_delete()
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter all the required args.")
        await _safe_delete()

# ==========================
#  UI VIEWS (BUTTON / SELECT)
# ==========================

class MyView(View):
    @discord.ui.button(label="improvement", style=discord.ButtonStyle.green, emoji="👌🏻")
    async def improvement_button(
        self, interaction: discord.Interaction, button: Button
    ):
        button.label = "Okay"
        button.disabled = True
        await interaction.response.send_message("Thank you!")
        print("________________________ [button improvement] ________________________")

    async def on_error(
        self,
        error: Exception,
        item: Item,
        interaction: discord.Interaction,
    ) -> None:
        print(f"View error: {error}")
        return await super().on_error(error, item, interaction)


class MySelection(View):
    @discord.ui.select(
        min_values=0,
        max_values=10,
        placeholder="make in a code",
        options=[
            discord.SelectOption(
                label="Python", emoji="🔐", description="Makes Python"
            ),
            discord.SelectOption(
                label="javascript", emoji="🔐", description="Makes javascript"
            ),
            discord.SelectOption(label="HTML", emoji="🔐", description="Makes HTML"),
            discord.SelectOption(label="Latex", emoji="🔐", description="Makes Latex"),
            discord.SelectOption(label="C++", emoji="🔐", description="Makes C++"),
            discord.SelectOption(
                label="C language", emoji="🔐", description="Makes C language"
            ),
            discord.SelectOption(label="Java", emoji="🔐", description="Makes Java"),
            discord.SelectOption(label="C#", emoji="🔐", description="Makes C#"),
            discord.SelectOption(label="GO", emoji="🔐", description="Makes GO"),
            discord.SelectOption(label="PHP", emoji="🔐", description="Makes PHP"),
            discord.SelectOption(label="Kotlin", emoji="🔐", description="Makes Kotlin"),
            discord.SelectOption(label="CSS", emoji="🔐", description="Makes CSS"),
        ],
    )
    async def select_callback(
        self, interaction: discord.Interaction, select: Select
    ):
        await interaction.response.send_message(f"```Code : {select.values}```")
        print("________________________ [select code] ________________________")


class MyButton(View):
    @discord.ui.button(
        label="congratulate", style=discord.ButtonStyle.red, emoji="🎂"
    )
    async def congratulate_button(
        self, interaction: discord.Interaction, button: Button
    ):
        button.label = "birthday"
        button.disabled = True
        await interaction.response.send_message("Thank you🎂🎂")
        print("________________________ [button birthday] ________________________")


# ==========================
#  ON_MESSAGE (MODMAIL + AUTO REPLIES)
# ==========================

@bot.event
async def on_message(message: discord.Message):
    # mod-mail
    empty_array = []
    modmail_channel = discord.utils.get(
        bot.get_all_channels(), name="📋clips-and-highlights"
    )

    if message.author.bot:
        return

    # DM to staff
    if str(message.channel.type) == "private" and modmail_channel:
        if message.attachments != empty_array:
            files = message.attachments
            await modmail_channel.send(f"[{message.author.name}]")
            for f in files:
                await modmail_channel.send(f.url)
        else:
            await modmail_channel.send(f"[{message.author.name}] {message.content}")
    # reply from staff
    elif (
        str(message.channel) == "📋clips-and-highlights"
        and message.content.startswith("<")
    ):
        if not message.author.guild_permissions.manage_messages:
            await message.channel.send("You don't have permission to reply to modmail.")
            return
        if not message.mentions:
            await message.channel.send("Please mention a user to reply.")
            return
        member_object = message.mentions[0]
        if message.attachments != empty_array:
            files = message.attachments
            await member_object.send(f"[{message.author.name}]")
            for f in files:
                await member_object.send(f.url)
        else:
            index = message.content.index(" ")
            mod_message = message.content[index:]
            await member_object.send(f"[{message.author}] {mod_message}")

    # ====== Auto English replies ======
    content = message.content

    async def log_simple(user: discord.Member):
        print("______________________________________________________________________________________>")
        print(f"[{message.channel}]")
        print(f"[{message.channel.id}]")
        print(f"[{user}]")
        print(f"[{user.id}]")
        guild_name = message.guild.name if message.guild else "DM"
        guild_id = message.guild.id if message.guild else "N/A"
        print(f"[{guild_name}]")
        print(f"[{guild_id}]")
        print(f"Ping: < {round(bot.latency * 1000)} > ms")
        print("______________________________________________________________________________________>")

    if content in ("hello", "Hello"):
        await log_simple(message.author)
        await message.reply("**Hello to welcome**")

    elif content in ("+my name", "+my name is"):
        await log_simple(message.author)
        await message.reply(f"Hello **{message.author.name}**")

    elif content in ("+name",):
        await log_simple(message.author)
        await message.reply(bot.user.name)

    elif content == "+=w=":
        await log_simple(message.author)
        await message.reply("**🐈😸😸🐈‍⬛**")

    elif content == "+I so hot":
        await log_simple(message.author)
        embed = discord.Embed(
            title="hot.♨️♨️🔥", color=0xFCAC28, timestamp=message.created_at
        )
        embed.set_image(url="https://c.tenor.com/gOMGvUqQrhwAAAAC/anime-too-hot.gif")
        await message.reply(embed=embed)

    elif content in ("+your name", "+you name"):
        await log_simple(message.author)
        await message.reply(f"my name is **{bot.user.name}**")

    elif content == "+you user":
        await log_simple(message.author)
        await message.reply(f"my name is **{bot.user}**")

    elif content in ("+user", "+User"):
        is_owner = await bot.is_owner(message.author)
        has_admin = message.guild is not None and message.author.guild_permissions.administrator
        if not (is_owner or has_admin):
            await message.reply("You don't have permission to do that.")
            return
        await log_simple(message.author)
        await message.reply(f"Okay **{message.author}**")
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="A Movie"
            )
        )
        await bot.close()

    elif content in ("+invite", "+link discord"):
        await log_simple(message.author)
        embed = discord.Embed(
            title="Server AKANEMI",
            description="**Link** : https://discord.gg/psPcfD6x6P",
            color=discord.Colour.random(),
            timestamp=message.created_at,
        )
        embed.set_footer(text=f"Requested by - {message.author}")
        await message.reply(embed=embed)

    # Keep prefix commands working after custom on_message logic.
    await bot.process_commands(message)


# ==========================
#  PREFIX COMMANDS (8BALL, MEME, NEKO, CALENDAR)
# ==========================


@bot.command(aliases=["Kick"])
async def kick(ctx: commands.Context, user: discord.Member | None = None):
    view = MyView()
    if user is None:
        user = ctx.author

    embed = discord.Embed(
        color=discord.Colour.random(),
        description=f"**{ctx.author.mention} {random.choice(kick_names)}**",
    )
    embed.set_image(url=random.choice(kick_gifs))
    await ctx.send(embed=embed, view=view)


@bot.command(aliases=["sting"])
async def smash(ctx: commands.Context, user: discord.Member | None = None):
    view = MyView()
    if user is None:
        user = ctx.author

    embed = discord.Embed(
        color=discord.Colour.random(),
        description=f"**{ctx.author.mention} {random.choice(smash_names)}**",
    )
    embed.set_image(url=random.choice(smash_gifs))
    await ctx.send(embed=embed, view=view)


def _month_embed(year: int, month: int) -> str:
    return f"```{calendar.month(year, month)}```"


@bot.command()
async def month1(ctx):
    await ctx.send(_month_embed(2026, 1))


@bot.command()
async def month2(ctx):
    await ctx.send(_month_embed(2026, 2))


@bot.command()
async def month3(ctx):
    await ctx.send(_month_embed(2026, 3))


@bot.command()
async def month4(ctx):
    await ctx.send(_month_embed(2026, 4))


@bot.command()
async def month5(ctx):
    await ctx.send(_month_embed(2026, 5))


@bot.command()
async def month6(ctx):
    await ctx.send(_month_embed(2026, 6))


@bot.command()
async def month7(ctx):
    await ctx.send(_month_embed(2026, 7))


@bot.command()
async def month8(ctx):
    await ctx.send(_month_embed(2026, 8))


@bot.command()
async def month9(ctx):
    await ctx.send(_month_embed(2026, 9))


@bot.command()
async def month10(ctx):
    await ctx.send(_month_embed(2026, 10))


@bot.command()
async def month11(ctx):
    await ctx.send(_month_embed(2026, 11))


@bot.command()
async def month12(ctx):
    await ctx.send(_month_embed(2026, 12))


@bot.command()
async def year(ctx):
    for m in range(1, 13):
        await ctx.send(_month_embed(2026, m))

# ==========================
#  REGISTER COG & RUN BOT
# ==========================

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not found in environment/.env")


async def main():
    # Load cogs before starting the bot.
    await bot.add_cog(SlashCog(bot))
    await bot.add_cog(ChessCog(bot))
    await bot.load_extension("cogs.snake_cog")
    await bot.load_extension("cogs.help_cog")
    await bot.load_extension("cogs.talk_cog")
    await bot.load_extension("cogs.meme_cog")
    await bot.load_extension("cogs.anime_cog")
    # Start the bot after all cogs are ready.
    await bot.start(TOKEN)


def _is_watched_file(rel_path: str) -> bool:
    lowered = rel_path.replace("\\", "/").lower()
    if lowered.endswith(".py"):
        return True
    return lowered in {".env", "requirements.txt"}


def _build_watch_snapshot(root: str) -> Dict[str, float]:
    snapshot: Dict[str, float] = {}
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in WATCH_IGNORE_DIRS]
        for filename in filenames:
            full_path = os.path.join(current_root, filename)
            rel_path = os.path.relpath(full_path, root)
            if not _is_watched_file(rel_path):
                continue
            try:
                snapshot[rel_path.replace("\\", "/")] = os.path.getmtime(full_path)
            except OSError:
                continue
    return snapshot


def _diff_snapshot(old: Dict[str, float], new: Dict[str, float]) -> List[str]:
    changed = [path for path in (set(old) | set(new)) if old.get(path) != new.get(path)]
    changed.sort()
    return changed


def _pid_exists(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            error_code = ctypes.get_last_error()
            return error_code == 5
        try:
            exit_code = ctypes.c_ulong()
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                return False
            return exit_code.value == STILL_ACTIVE
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except (OSError, SystemError, ValueError):
        return False
    return True


def _wait_for_pid_exit(pid: int, timeout_seconds: float = 12.0) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if not _pid_exists(pid):
            return True
        time.sleep(0.25)
    return not _pid_exists(pid)


def _terminate_process(pid: int) -> bool:
    if pid <= 0:
        return False
    if not _pid_exists(pid):
        return True

    if os.name == "nt":
        try:
            result = subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )
        except OSError as e:
            print(f"[runtime] could not terminate pid={pid}: {e}")
            return False

        if result.returncode not in {0, 128, 255} and _pid_exists(pid):
            output = ((result.stdout or "") + "\n" + (result.stderr or "")).strip()
            print(f"[runtime] taskkill failed for pid={pid}: {output or 'unknown error'}")
            return False
        return _wait_for_pid_exit(pid)

    try:
        os.kill(pid, signal.SIGTERM)
    except (OSError, SystemError, ValueError) as e:
        print(f"[runtime] could not terminate pid={pid}: {e}")
        return False
    return _wait_for_pid_exit(pid)


def _release_instance_lock() -> None:
    global _instance_lock_acquired
    if not _instance_lock_acquired:
        return
    try:
        if os.path.isfile(INSTANCE_LOCK_FILE):
            os.remove(INSTANCE_LOCK_FILE)
    except OSError:
        pass
    _instance_lock_acquired = False


def _acquire_instance_lock(allow_replace_existing: bool = False) -> bool:
    global _instance_lock_acquired
    if _instance_lock_acquired:
        return True

    os.makedirs(os.path.dirname(INSTANCE_LOCK_FILE), exist_ok=True)

    legacy_pid_path = os.path.join(LEGACY_INSTANCE_LOCK_DIR, "pid")
    if os.path.isdir(LEGACY_INSTANCE_LOCK_DIR):
        legacy_pid = 0
        try:
            with open(legacy_pid_path, "r", encoding="utf-8") as f:
                legacy_pid = int((f.read() or "0").strip() or "0")
        except (OSError, ValueError):
            legacy_pid = 0

        if legacy_pid and _pid_exists(legacy_pid):
            if allow_replace_existing:
                print(f"[runtime] replacing existing PanosV2 instance (legacy pid={legacy_pid})")
                if not _terminate_process(legacy_pid):
                    print(f"[runtime] failed to stop existing legacy instance (pid={legacy_pid})")
                    return False
            else:
                print(f"[runtime] another PanosV2 instance is already running (legacy pid={legacy_pid})")
                return False

        if os.path.isfile(legacy_pid_path):
            try:
                os.remove(legacy_pid_path)
                print("[runtime] removed stale legacy lock pid file")
            except OSError as e:
                print(f"[runtime] could not remove legacy lock pid file: {e}")

    while True:
        try:
            with open(INSTANCE_LOCK_FILE, "x", encoding="utf-8") as f:
                f.write(str(os.getpid()))
            atexit.register(_release_instance_lock)
            _instance_lock_acquired = True
            print(f"[runtime] instance lock acquired | pid={os.getpid()}")
            return True
        except FileExistsError:
            existing_pid = 0
            try:
                with open(INSTANCE_LOCK_FILE, "r", encoding="utf-8") as f:
                    existing_pid = int((f.read() or "0").strip() or "0")
            except (OSError, ValueError):
                existing_pid = 0

            if existing_pid and _pid_exists(existing_pid):
                if allow_replace_existing:
                    print(f"[runtime] replacing existing PanosV2 instance (pid={existing_pid})")
                    if not _terminate_process(existing_pid):
                        print(f"[runtime] failed to stop existing instance (pid={existing_pid})")
                        return False
                    continue
                print(f"[runtime] another PanosV2 instance is already running (pid={existing_pid})")
                return False

            print("[runtime] stale instance lock detected; cleaning up")
            try:
                if os.path.isfile(INSTANCE_LOCK_FILE):
                    os.remove(INSTANCE_LOCK_FILE)
            except OSError as e:
                print(f"[runtime] could not remove stale instance lock: {e}")
                return False


def _run_bot_once(allow_replace_existing: bool = False) -> int:
    global PROCESS_EXIT_CODE
    PROCESS_EXIT_CODE = 0
    if not _acquire_instance_lock(allow_replace_existing=allow_replace_existing):
        return 2
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[bot] stopped by keyboard interrupt")
        return 0
    return PROCESS_EXIT_CODE


def _run_supervisor() -> int:
    child_cmd = [sys.executable, os.path.abspath(__file__), CHILD_ARG]
    snapshot = _build_watch_snapshot(PROJECT_ROOT)
    print(f"[supervisor] active | poll={WATCH_POLL_SECONDS}s")
    print(f"[supervisor] launching child: {' '.join(child_cmd)}")

    while True:
        env = os.environ.copy()
        env["PANOS_CHILD"] = "1"
        child = subprocess.Popen(child_cmd, cwd=PROJECT_ROOT, env=env)
        requested_restart = False
        exit_code: Optional[int] = None

        while True:
            exit_code = child.poll()
            if exit_code is not None:
                break

            time.sleep(WATCH_POLL_SECONDS)
            new_snapshot = _build_watch_snapshot(PROJECT_ROOT)
            changed_files = _diff_snapshot(snapshot, new_snapshot)
            if changed_files:
                preview = ", ".join(changed_files[:5])
                if len(changed_files) > 5:
                    preview += f" (+{len(changed_files) - 5} more)"
                print(f"[supervisor] change detected -> restart child ({preview})")
                snapshot = new_snapshot
                requested_restart = True
                child.terminate()
                try:
                    child.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=5)
                break

        if requested_restart:
            print("[supervisor] relaunching child after source change")
            continue

        if exit_code == RESTART_EXIT_CODE:
            print("[supervisor] child requested restart")
            snapshot = _build_watch_snapshot(PROJECT_ROOT)
            continue

        if exit_code == 0:
            print("[supervisor] child exited normally; supervisor will stop")
            return 0

        print(f"[supervisor] child exited with code {exit_code}; restart in 3s")
        time.sleep(3)
        snapshot = _build_watch_snapshot(PROJECT_ROOT)


def _is_supervisor_enabled() -> bool:
    return os.getenv(ENABLE_SUPERVISOR_ENV, "").strip().lower() in {"1", "true", "yes", "on"}


def _project_is_in_onedrive() -> bool:
    normalized_parts = [part.lower() for part in PROJECT_ROOT.replace("/", "\\").split("\\")]
    return "onedrive" in normalized_parts


if __name__ == "__main__":
    allow_replace_existing = REPLACE_EXISTING_ARG in sys.argv
    if SUPERVISOR_ARG in sys.argv and CHILD_ARG not in sys.argv:
        if not _is_supervisor_enabled():
            print(
                f"[supervisor] ignored. Hot-reload is disabled by default for runtime stability.\n"
                f"[supervisor] If you really want dev hot-reload, set {ENABLE_SUPERVISOR_ENV}=1 and run again."
            )
        else:
            if _project_is_in_onedrive():
                print(
                    "[supervisor] warning: project is inside OneDrive. File sync can trigger restarts,\n"
                    "[supervisor] which will disconnect the bot from voice channels while music is playing."
                )
            raise SystemExit(_run_supervisor())
    raise SystemExit(_run_bot_once(allow_replace_existing=allow_replace_existing))
