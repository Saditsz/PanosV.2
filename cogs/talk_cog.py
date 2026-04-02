import asyncio
import cmath
import json
import math
import random
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import discord
from discord.ext import commands
from discord import app_commands

MEMORY_PATH = Path("data") / "user_memory.json"
ENGLISH_BANK_PATH = Path("data") / "english_bank.json"
ENGLISH_BANK_GLOB = "english_bank_*.json"
MAX_NOTES = 1000000
MAX_NOTE_LEN = 2000
MAX_RECENT_MESSAGES = 1000000
MAX_RECALL_RESULTS = 8
MAX_RECALL_TEXT_LEN = 200
MAX_FOOD_MEMORY = 1000000
MAX_FOOD_ITEM_LEN = 200
MAX_FOOD_SUGGESTIONS = 5
MIN_QA_MATCH_LEN = 6
MAX_MOOD_MEMORY = 1000000
MAX_THOUGHT_MEMORY = 1000000
MAX_MOOD_ITEM_LEN = 300
MAX_THOUGHT_ITEM_LEN = 500
MAX_RECENT_FEELINGS = 5
MAX_RECENT_THOUGHTS = 5
MAX_NOTES_IN_PROFILE = 10
CREATOR_ID = 842640031284985886
CREATOR_NAME = "Dale"
BOT_GIRL_NAME = "Panos"
BOT_BIRTHDAY_TEXT = "May 10, 2022 (10 May 2565 BE)"
REPLY_VISIBILITY_KEY = "reply visibility"
MAX_LAST_MESSAGE_LEN = 2000
MAX_PREF_KEY_LEN = 32
MAX_PREF_VALUE_LEN = 500
MAX_PREFS_IN_PROFILE = 12
MAX_QA_QUESTION_LEN = 500
MAX_QA_ANSWER_LEN = 2000
MAX_STORY_MEMORY = 1000000
MAX_STORY_ITEM_LEN = 400
MAX_TIME_MEMORY = 1000000
MAX_TIME_ITEM_LEN = 200
MAX_RECENT_TIME_NOTES = 5
MAX_RECENT_STORY_NOTES = 5
MAX_MESSAGE_LOG = 1000000
MAX_MESSAGE_LOG_LEN = 2000
MAX_RECENT_QUESTION_MEMORY = 8
MAX_TOPIC_SIGNAL_MEMORY = 12
MAX_BOND_LABELS = 5
MAX_GUILD_AI_REASON_LOG = 20
GUILD_AI_STATE_DIM = 4
GUILD_AI_IMAG_DIM = 3
GUILD_AI_TOPIC_DIM = 6
GUILD_AI_TIME_BUCKETS = 4
GUILD_AI_HORMONE_DIM = 6
GUILD_AI_INSTINCT_DIM = 4
MAX_GUILD_AI_SNIPPETS = 2000
MAX_GUILD_AI_PHRASES = 8000
MAX_GUILD_AI_TOKENS = 12000

GUILD_AI_A = [
    [0.82, 0.06, 0.05, 0.03],
    [0.04, 0.80, 0.06, 0.04],
    [0.05, 0.04, 0.84, 0.05],
    [0.03, 0.06, 0.05, 0.83],
]
GUILD_AI_B = [
    [0.55, 0.12, 0.08, 0.10],
    [0.10, 0.62, 0.10, 0.05],
    [0.08, 0.10, 0.58, 0.12],
    [0.12, 0.06, 0.10, 0.60],
]
GUILD_AI_D = [
    [0.20, 0.08, 0.06],
    [0.10, 0.18, 0.08],
    [0.06, 0.08, 0.16],
    [0.08, 0.06, 0.14],
]
GUILD_AI_W = [
    [0.36, 0.20, 0.12, 0.10, 0.14, 0.08],
    [0.10, 0.34, 0.08, 0.22, 0.10, 0.16],
    [0.12, 0.14, 0.32, 0.12, 0.16, 0.10],
]
GUILD_AI_BLEND_ALPHA = 0.08
GUILD_AI_STYLE_ALPHA = 0.10
GUILD_AI_TIME_BUCKET_LABELS = ["night", "morning", "afternoon", "evening"]
GUILD_AI_DEFAULT_PROFILE = "beast"
GUILD_AI_PROFILE_CONFIG = {
    "balanced": {
        "quality_floor": 0.18,
        "blend_alpha": 0.08,
        "style_alpha": 0.10,
        "replay_steps": 1,
        "phrase_limit": 900,
        "snippet_limit": 260,
        "token_limit": 1500,
        "ngram_max": 2,
        "reply_warmup": 18,
    },
    "aggressive": {
        "quality_floor": 0.12,
        "blend_alpha": 0.14,
        "style_alpha": 0.16,
        "replay_steps": 2,
        "phrase_limit": 2200,
        "snippet_limit": 600,
        "token_limit": 3200,
        "ngram_max": 3,
        "reply_warmup": 12,
    },
    "overdrive": {
        "quality_floor": 0.08,
        "blend_alpha": 0.20,
        "style_alpha": 0.22,
        "replay_steps": 3,
        "phrase_limit": 4500,
        "snippet_limit": 1200,
        "token_limit": 7000,
        "ngram_max": 3,
        "reply_warmup": 8,
    },
    "beast": {
        "quality_floor": 0.05,
        "blend_alpha": 0.26,
        "style_alpha": 0.28,
        "replay_steps": 5,
        "phrase_limit": 7000,
        "snippet_limit": 1800,
        "token_limit": 10000,
        "ngram_max": 4,
        "reply_warmup": 5,
    },
}
GUILD_AI_HORMONE_LABELS = [
    "dopamine",
    "serotonin",
    "cortisol",
    "oxytocin",
    "curiosity",
    "focus",
]
GUILD_AI_INSTINCT_LABELS = [
    "social_need",
    "attachment",
    "exploration",
    "safety_guard",
]
GUILD_AI_BELIEF_KEYS = ["alien_life", "isekai_rebirth"]
GUILD_AI_HORMONE_A = [
    [0.86, 0.04, -0.02, 0.03, 0.05, 0.04],
    [0.05, 0.88, -0.03, 0.06, 0.02, 0.03],
    [-0.04, -0.03, 0.90, -0.02, 0.03, 0.02],
    [0.03, 0.06, -0.02, 0.87, 0.02, 0.02],
    [0.06, 0.03, 0.02, 0.03, 0.85, 0.04],
    [0.03, 0.02, 0.03, 0.02, 0.04, 0.86],
]
GUILD_AI_HORMONE_B = [
    [0.42, 0.16, -0.26, 0.10],
    [0.34, 0.08, -0.18, 0.14],
    [-0.28, 0.22, 0.38, -0.10],
    [0.18, 0.06, -0.14, 0.42],
    [0.16, 0.34, 0.06, 0.08],
    [0.10, 0.18, -0.05, 0.22],
]
GUILD_AI_HORMONE_C = [
    [0.20, 0.16, 0.10],
    [0.16, 0.12, 0.08],
    [0.06, 0.12, 0.08],
    [0.10, 0.18, 0.10],
    [0.24, 0.22, 0.18],
    [0.10, 0.14, 0.12],
]
GUILD_AI_INSTINCT_H = [
    [0.12, 0.08, 0.06, 0.18, 0.10, 0.02],
    [0.10, 0.12, 0.04, 0.24, 0.06, 0.04],
    [0.08, 0.06, -0.04, 0.02, 0.28, 0.12],
    [0.04, 0.06, 0.24, 0.02, 0.04, 0.10],
]
GUILD_AI_INSTINCT_S = [
    [0.14, 0.06, 0.04, 0.22],
    [0.10, 0.04, 0.06, 0.18],
    [0.08, 0.12, 0.18, 0.04],
    [-0.06, 0.10, 0.12, 0.08],
]

GUILD_AI_RISK_TERMS = {
    "nsfw",
    "nude",
    "porn",
    "rape",
    "suicide",
    "self-harm",
    "drug",
    "meth",
    "ฆ่า",
    "ข่มขืน",
    "ยาเสพติด",
}
GUILD_AI_POSITIVE_TERMS = {
    "good",
    "great",
    "love",
    "happy",
    "thanks",
    "awesome",
    "ดี",
    "ดีใจ",
    "รัก",
    "ชอบ",
    "ขอบคุณ",
    "สนุก",
    "เยี่ยม",
    "สุขใจ",
}
GUILD_AI_NEGATIVE_TERMS = {
    "bad",
    "sad",
    "angry",
    "hate",
    "stress",
    "anxious",
    "แย่",
    "เศร้า",
    "โกรธ",
    "เกลียด",
    "เครียด",
    "กังวล",
    "เหนื่อย",
    "ท้อ",
}
GUILD_AI_AROUSAL_TERMS = {
    "urgent",
    "asap",
    "now",
    "เร็ว",
    "ด่วน",
    "รีบ",
    "ตื่นเต้น",
}
GUILD_AI_ASSERTIVE_TERMS = {
    "must",
    "definitely",
    "sure",
    "confident",
    "ต้อง",
    "แน่นอน",
    "ชัวร์",
    "มั่นใจ",
}
GUILD_AI_UNCERTAIN_TERMS = {
    "maybe",
    "perhaps",
    "not sure",
    "uncertain",
    "อาจ",
    "ไม่แน่",
    "ลังเล",
}
GUILD_AI_SOCIAL_TERMS = {
    "we",
    "team",
    "together",
    "friend",
    "เรา",
    "พวกเรา",
    "ทีม",
    "เพื่อน",
    "ครอบครัว",
}
GUILD_AI_TOPIC_KEYWORDS = {
    "music": {"music", "song", "playlist", "band", "artist", "เพลง", "ดนตรี"},
    "game": {"game", "gaming", "rank", "match", "เกม", "แรงค์", "แมตช์"},
    "study": {"study", "school", "learn", "exam", "เรียน", "สอบ", "การบ้าน"},
    "emotion": {"feel", "emotion", "sad", "happy", "รัก", "เศร้า", "ดีใจ", "เครียด"},
    "work": {"work", "job", "project", "meeting", "งาน", "โปรเจกต์", "ประชุม"},
    "social": {"friend", "community", "party", "hangout", "เพื่อน", "สังคม", "ชุมชน"},
}

FREEFORM_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "but",
    "by",
    "can",
    "could",
    "did",
    "do",
    "does",
    "for",
    "from",
    "had",
    "has",
    "have",
    "how",
    "i",
    "if",
    "in",
    "is",
    "it",
    "me",
    "my",
    "not",
    "of",
    "on",
    "or",
    "our",
    "she",
    "so",
    "that",
    "the",
    "their",
    "them",
    "then",
    "there",
    "they",
    "this",
    "to",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "will",
    "with",
    "would",
    "you",
    "your",
}


def _normalize_key(text: str) -> str:
    return " ".join(text.strip().split()).casefold()


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryStore:
    def __init__(self, path: Path):
        self.path = path
        self.data = {"users": {}, "qa_pairs": {}, "message_log": [], "guild_ai": {}}
        self._lock = asyncio.Lock()
        self._save_task: asyncio.Task | None = None
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("memory data is not a dict")
            self.data = data
        except (OSError, ValueError, json.JSONDecodeError):
            self.data = {"users": {}, "qa_pairs": {}, "message_log": [], "guild_ai": {}}
            return
        if "users" not in self.data:
            self.data["users"] = {}
        if "qa_pairs" not in self.data:
            self.data["qa_pairs"] = {}
        if "message_log" not in self.data:
            self.data["message_log"] = []
        if "guild_ai" not in self.data:
            self.data["guild_ai"] = {}

    def _get_user(self, user_id: int) -> dict:
        users = self.data.setdefault("users", {})
        uid = str(user_id)
        user = users.get(uid)
        if user is None:
            user = {
                "display_name": None,
                "nickname": None,
                "last_seen": None,
                "message_count": 0,
                "command_counts": {},
                "notes": [],
                "preferences": {},
                "last_message": None,
                "last_message_at": None,
                "recent_messages": [],
                "food_memory": [],
                "mood_history": [],
                "thought_history": [],
                "story_memory": [],
                "time_memory": [],
                "bond_state": self._new_bond_state(),
                "emotion_profile": {},
                "topic_signals": {},
                "recent_questions": [],
            }
            users[uid] = user
        if not isinstance(user.get("bond_state"), dict):
            user["bond_state"] = self._new_bond_state()
        if not isinstance(user.get("emotion_profile"), dict):
            user["emotion_profile"] = {}
        if not isinstance(user.get("topic_signals"), dict):
            user["topic_signals"] = {}
        if not isinstance(user.get("recent_questions"), list):
            user["recent_questions"] = []
        return user

    @staticmethod
    def _new_bond_state() -> dict[str, float]:
        return {
            "warmth": 0.0,
            "trust": 0.0,
            "curiosity": 0.0,
            "playfulness": 0.0,
            "confidence": 0.0,
        }

    @staticmethod
    def _clamp_bond_value(value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 4)

    def _record_message(self, user: dict, message: str) -> None:
        text = _truncate(message, MAX_LAST_MESSAGE_LEN)
        user["last_message"] = text
        user["last_message_at"] = _now_iso()
        history = user.setdefault("recent_messages", [])
        if not isinstance(history, list):
            history = []
            user["recent_messages"] = history
        history.append(text)
        if len(history) > MAX_RECENT_MESSAGES:
            del history[:-MAX_RECENT_MESSAGES]

    def touch_message(self, user: discord.abc.User, message: str | None = None) -> None:
        u = self._get_user(user.id)
        display_name = getattr(user, "display_name", user.name)
        u["display_name"] = display_name
        u["last_seen"] = _now_iso()
        u["message_count"] = int(u.get("message_count", 0)) + 1
        if message:
            self._record_message(u, message)
        self._schedule_save()

    def log_message(
        self,
        user: discord.abc.User,
        message: str,
        channel_id: int | None = None,
        guild_id: int | None = None,
        source: str | None = None,
    ) -> None:
        log = self.data.setdefault("message_log", [])
        if not isinstance(log, list):
            log = []
            self.data["message_log"] = log
        entry = {
            "user_id": user.id,
            "user_name": user.name,
            "display_name": getattr(user, "display_name", user.name),
            "message": _truncate(message, MAX_MESSAGE_LOG_LEN),
            "at": _now_iso(),
        }
        if channel_id is not None:
            entry["channel_id"] = channel_id
        if guild_id is not None:
            entry["guild_id"] = guild_id
        if source:
            entry["source"] = source
        log.append(entry)
        if len(log) > MAX_MESSAGE_LOG:
            del log[:-MAX_MESSAGE_LOG]
        self._schedule_save()

    def set_last_message(self, user: discord.abc.User, message: str) -> None:
        u = self._get_user(user.id)
        display_name = getattr(user, "display_name", user.name)
        u["display_name"] = display_name
        u["last_seen"] = _now_iso()
        self._record_message(u, message)
        self._schedule_save()

    def set_preference(self, user_id: int, key: str, value: str) -> None:
        u = self._get_user(user_id)
        prefs = u.setdefault("preferences", {})
        prefs[key] = value
        self._schedule_save()

    def remove_preference(self, user_id: int, key: str) -> bool:
        u = self._get_user(user_id)
        prefs = u.setdefault("preferences", {})
        removed = prefs.pop(key, None)
        if removed is None:
            return False
        self._schedule_save()
        return True

    def mark_command(self, user_id: int, command_name: str) -> None:
        u = self._get_user(user_id)
        counts = u.setdefault("command_counts", {})
        counts[command_name] = int(counts.get(command_name, 0)) + 1
        self._schedule_save()

    def set_nickname(self, user_id: int, nickname: str | None) -> None:
        u = self._get_user(user_id)
        u["nickname"] = nickname
        self._schedule_save()

    def add_note(self, user_id: int, note: str) -> None:
        u = self._get_user(user_id)
        notes = u.setdefault("notes", [])
        if not isinstance(notes, list):
            notes = []
            u["notes"] = notes
        notes.append(_truncate(note, MAX_NOTE_LEN))
        if len(notes) > MAX_NOTES:
            del notes[:-MAX_NOTES]
        self._schedule_save()

    def add_food_memory(self, user_id: int, food: str) -> None:
        u = self._get_user(user_id)
        foods = u.setdefault("food_memory", [])
        if not isinstance(foods, list):
            foods = []
            u["food_memory"] = foods
        food = _truncate(food, MAX_FOOD_ITEM_LEN)
        if not food:
            return
        foods.append(food)
        if len(foods) > MAX_FOOD_MEMORY:
            del foods[:-MAX_FOOD_MEMORY]
        self._schedule_save()

    def get_food_suggestions(self, user_id: int) -> list[str]:
        u = self._get_user(user_id)
        foods = u.get("food_memory", [])
        if not foods:
            return []
        counts: dict[str, int] = {}
        display: dict[str, str] = {}
        for item in foods:
            text = str(item).strip()
            key = _normalize_key(text)
            if not key:
                continue
            counts[key] = counts.get(key, 0) + 1
            display.setdefault(key, text)
        sorted_keys = sorted(counts, key=lambda k: (-counts[k], k))
        return [display[k] for k in sorted_keys]

    def add_mood(self, user_id: int, mood: str, detail: str | None = None) -> None:
        u = self._get_user(user_id)
        moods = u.setdefault("mood_history", [])
        if not isinstance(moods, list):
            moods = []
            u["mood_history"] = moods
        detail_text = _truncate(detail, MAX_MOOD_ITEM_LEN) if detail else None
        moods.append(
            {"mood": mood, "detail": detail_text, "at": _now_iso()}
        )
        if len(moods) > MAX_MOOD_MEMORY:
            del moods[:-MAX_MOOD_MEMORY]
        self._schedule_save()

    def add_thought(self, user_id: int, thought: str) -> None:
        u = self._get_user(user_id)
        thoughts = u.setdefault("thought_history", [])
        if not isinstance(thoughts, list):
            thoughts = []
            u["thought_history"] = thoughts
        thought_text = _truncate(thought, MAX_THOUGHT_ITEM_LEN)
        if not thought_text:
            return
        thoughts.append({"thought": thought_text, "at": _now_iso()})
        if len(thoughts) > MAX_THOUGHT_MEMORY:
            del thoughts[:-MAX_THOUGHT_MEMORY]
        self._schedule_save()

    def add_story_memory(self, user_id: int, event: str) -> None:
        u = self._get_user(user_id)
        events = u.setdefault("story_memory", [])
        if not isinstance(events, list):
            events = []
            u["story_memory"] = events
        event_text = _truncate(event, MAX_STORY_ITEM_LEN)
        if not event_text:
            return
        normalized = _normalize_key(event_text)
        if events:
            last = events[-1]
            if isinstance(last, dict) and _normalize_key(str(last.get("event", ""))) == normalized:
                return
        events.append({"event": event_text, "at": _now_iso()})
        if len(events) > MAX_STORY_MEMORY:
            del events[:-MAX_STORY_MEMORY]
        self._schedule_save()

    def add_time_memory(self, user_id: int, note: str) -> None:
        u = self._get_user(user_id)
        notes = u.setdefault("time_memory", [])
        if not isinstance(notes, list):
            notes = []
            u["time_memory"] = notes
        note_text = _truncate(note, MAX_TIME_ITEM_LEN)
        if not note_text:
            return
        normalized = _normalize_key(note_text)
        if notes:
            last = notes[-1]
            if isinstance(last, dict) and _normalize_key(str(last.get("note", ""))) == normalized:
                return
        notes.append({"note": note_text, "at": _now_iso()})
        if len(notes) > MAX_TIME_MEMORY:
            del notes[:-MAX_TIME_MEMORY]
        self._schedule_save()

    def learn_conversation_state(
        self,
        user_id: int,
        *,
        warmth_delta: float = 0.0,
        trust_delta: float = 0.0,
        curiosity_delta: float = 0.0,
        playfulness_delta: float = 0.0,
        confidence_delta: float = 0.0,
        emotion_tag: str | None = None,
        topics: list[str] | None = None,
        question: str | None = None,
    ) -> None:
        u = self._get_user(user_id)
        bond = u.setdefault("bond_state", self._new_bond_state())
        for key, delta in (
            ("warmth", warmth_delta),
            ("trust", trust_delta),
            ("curiosity", curiosity_delta),
            ("playfulness", playfulness_delta),
            ("confidence", confidence_delta),
        ):
            try:
                bond[key] = self._clamp_bond_value(float(bond.get(key, 0.0)) + float(delta))
            except (TypeError, ValueError):
                bond[key] = self._clamp_bond_value(delta)

        if emotion_tag:
            emotion_profile = u.setdefault("emotion_profile", {})
            key = _normalize_key(emotion_tag)
            if key:
                emotion_profile[key] = int(emotion_profile.get(key, 0)) + 1

        if topics:
            topic_signals = u.setdefault("topic_signals", {})
            for topic in topics:
                key = _normalize_key(topic)
                if not key:
                    continue
                topic_signals[key] = int(topic_signals.get(key, 0)) + 1
            if len(topic_signals) > MAX_TOPIC_SIGNAL_MEMORY:
                sorted_items = sorted(
                    topic_signals.items(),
                    key=lambda item: (-int(item[1]), item[0]),
                )[:MAX_TOPIC_SIGNAL_MEMORY]
                u["topic_signals"] = {key: value for key, value in sorted_items}

        question_text = _truncate(" ".join((question or "").split()), MAX_RECALL_TEXT_LEN)
        if question_text:
            recent_questions = u.setdefault("recent_questions", [])
            recent_questions.append({"question": question_text, "at": _now_iso()})
            if len(recent_questions) > MAX_RECENT_QUESTION_MEMORY:
                del recent_questions[:-MAX_RECENT_QUESTION_MEMORY]

        self._schedule_save()

    def teach_qa(self, question: str, answer: str, author_id: int) -> None:
        qa_pairs = self.data.setdefault("qa_pairs", {})
        key = _normalize_key(question)
        qa_pairs[key] = {
            "question": question,
            "answer": answer,
            "updated_at": _now_iso(),
            "updated_by": author_id,
        }
        self._schedule_save()

    def get_qa(self, question: str) -> dict | None:
        qa_pairs = self.data.setdefault("qa_pairs", {})
        key = _normalize_key(question)
        qa = qa_pairs.get(key)
        if qa is None:
            return None
        return dict(qa)

    def get_qa_answer(self, question: str) -> str | None:
        qa = self.get_qa(question)
        if qa is None:
            return None
        return qa.get("answer")

    def find_qa_answer(self, question: str) -> str | None:
        qa_pairs = self.data.setdefault("qa_pairs", {})
        q = _normalize_key(question)
        if not q:
            return None
        qa = qa_pairs.get(q)
        if qa:
            return qa.get("answer")

        if len(q) < MIN_QA_MATCH_LEN:
            return None

        best_key = None
        best_len = 0
        for key, qa in qa_pairs.items():
            if len(key) < MIN_QA_MATCH_LEN:
                continue
            if key in q or q in key:
                if len(key) > best_len:
                    best_len = len(key)
                    best_key = key
        if best_key:
            return qa_pairs.get(best_key, {}).get("answer")
        return None

    def search_qa(self, user_id: int, query: str) -> list[dict]:
        q = _normalize_key(query)
        results: list[dict] = []
        for qa in self.data.get("qa_pairs", {}).values():
            if qa.get("updated_by") != user_id:
                continue
            question = str(qa.get("question", ""))
            answer = str(qa.get("answer", ""))
            if q in question.casefold() or q in answer.casefold():
                results.append({"question": question, "answer": answer})
        return results

    def forget_user(self, user_id: int) -> None:
        self.data.get("users", {}).pop(str(user_id), None)
        self._schedule_save()

    def get_profile(self, user_id: int) -> dict:
        return dict(self._get_user(user_id))

    @staticmethod
    def _blank_vector(size: int) -> list[float]:
        return [0.0 for _ in range(size)]

    @staticmethod
    def _blank_matrix(rows: int, cols: int) -> list[list[float]]:
        return [[0.0 for _ in range(cols)] for _ in range(rows)]

    @staticmethod
    def _blank_tensor(depth: int, rows: int, cols: int) -> list[list[list[float]]]:
        return [
            [[0.0 for _ in range(cols)] for _ in range(rows)]
            for _ in range(depth)
        ]

    @staticmethod
    def _new_human_style() -> dict[str, float]:
        return {
            "avg_tokens": 0.0,
            "question_ratio": 0.0,
            "emoji_ratio": 0.0,
            "exclaim_ratio": 0.0,
            "slang_ratio": 0.0,
            "warmth": 0.0,
        }

    def _new_guild_ai_state(self) -> dict:
        return {
            "enabled": True,
            "learning_profile": GUILD_AI_DEFAULT_PROFILE,
            "messages_seen": 0,
            "messages_learned": 0,
            "messages_blocked": 0,
            "psych_state": self._blank_vector(GUILD_AI_STATE_DIM),
            "imagination_state": self._blank_vector(GUILD_AI_IMAG_DIM),
            "hormone_state": self._blank_vector(GUILD_AI_HORMONE_DIM),
            "instinct_state": self._blank_vector(GUILD_AI_INSTINCT_DIM),
            "psych_gradient": self._blank_vector(GUILD_AI_STATE_DIM),
            "complex_phase": 0.0,
            "speculative_beliefs": {
                "alien_life": 0.5,
                "isekai_rebirth": 0.5,
            },
            "transition_matrix": self._blank_matrix(
                GUILD_AI_STATE_DIM, GUILD_AI_STATE_DIM
            ),
            "memory_2d": self._blank_matrix(
                GUILD_AI_STATE_DIM, GUILD_AI_TOPIC_DIM
            ),
            "memory_3d": self._blank_tensor(
                GUILD_AI_TIME_BUCKETS, GUILD_AI_STATE_DIM, GUILD_AI_TOPIC_DIM
            ),
            "human_style": self._new_human_style(),
            "phrase_bank": {},
            "token_counts": {},
            "recent_snippets": [],
            "topic_totals": {},
            "recent_reasons": [],
            "last_quality": 0.0,
            "last_features": self._blank_vector(GUILD_AI_STATE_DIM),
            "last_message_preview": "",
            "updated_at": _now_iso(),
            "created_at": _now_iso(),
        }

    def _get_guild_ai(self, guild_id: int) -> dict:
        guild_ai = self.data.setdefault("guild_ai", {})
        gid = str(guild_id)
        state = guild_ai.get(gid)
        if not isinstance(state, dict):
            state = self._new_guild_ai_state()
            guild_ai[gid] = state
            return state

        state.setdefault("enabled", True)
        state.setdefault("learning_profile", GUILD_AI_DEFAULT_PROFILE)
        state.setdefault("messages_seen", 0)
        state.setdefault("messages_learned", 0)
        state.setdefault("messages_blocked", 0)
        state.setdefault("psych_state", self._blank_vector(GUILD_AI_STATE_DIM))
        state.setdefault("imagination_state", self._blank_vector(GUILD_AI_IMAG_DIM))
        state.setdefault("hormone_state", self._blank_vector(GUILD_AI_HORMONE_DIM))
        state.setdefault("instinct_state", self._blank_vector(GUILD_AI_INSTINCT_DIM))
        state.setdefault("psych_gradient", self._blank_vector(GUILD_AI_STATE_DIM))
        state.setdefault("complex_phase", 0.0)
        state.setdefault(
            "speculative_beliefs",
            {
                "alien_life": 0.5,
                "isekai_rebirth": 0.5,
            },
        )
        state.setdefault(
            "transition_matrix",
            self._blank_matrix(GUILD_AI_STATE_DIM, GUILD_AI_STATE_DIM),
        )
        state.setdefault(
            "memory_2d",
            self._blank_matrix(GUILD_AI_STATE_DIM, GUILD_AI_TOPIC_DIM),
        )
        state.setdefault(
            "memory_3d",
            self._blank_tensor(
                GUILD_AI_TIME_BUCKETS, GUILD_AI_STATE_DIM, GUILD_AI_TOPIC_DIM
            ),
        )
        state.setdefault("human_style", self._new_human_style())
        state.setdefault("phrase_bank", {})
        state.setdefault("token_counts", {})
        state.setdefault("recent_snippets", [])
        state.setdefault("topic_totals", {})
        state.setdefault("recent_reasons", [])
        state.setdefault("last_quality", 0.0)
        state.setdefault("last_features", self._blank_vector(GUILD_AI_STATE_DIM))
        state.setdefault("last_message_preview", "")
        if not isinstance(state.get("human_style"), dict):
            state["human_style"] = self._new_human_style()
        if not isinstance(state.get("phrase_bank"), dict):
            state["phrase_bank"] = {}
        if not isinstance(state.get("token_counts"), dict):
            state["token_counts"] = {}
        if not isinstance(state.get("recent_snippets"), list):
            state["recent_snippets"] = []
        if not isinstance(state.get("speculative_beliefs"), dict):
            state["speculative_beliefs"] = {
                "alien_life": 0.5,
                "isekai_rebirth": 0.5,
            }
        profile = str(state.get("learning_profile", GUILD_AI_DEFAULT_PROFILE)).casefold()
        if profile not in GUILD_AI_PROFILE_CONFIG:
            state["learning_profile"] = GUILD_AI_DEFAULT_PROFILE
        state.setdefault("updated_at", _now_iso())
        state.setdefault("created_at", _now_iso())
        return state

    def get_guild_ai(self, guild_id: int) -> dict:
        return dict(self._get_guild_ai(guild_id))

    def set_guild_ai_enabled(self, guild_id: int, enabled: bool) -> None:
        state = self._get_guild_ai(guild_id)
        state["enabled"] = bool(enabled)
        state["updated_at"] = _now_iso()
        self._schedule_save()

    def set_guild_ai_profile(self, guild_id: int, profile: str) -> str:
        state = self._get_guild_ai(guild_id)
        key = str(profile).casefold().strip()
        if key not in GUILD_AI_PROFILE_CONFIG:
            key = GUILD_AI_DEFAULT_PROFILE
        state["learning_profile"] = key
        state["updated_at"] = _now_iso()
        self._schedule_save()
        return key

    def reset_guild_ai(self, guild_id: int) -> None:
        guild_ai = self.data.setdefault("guild_ai", {})
        gid = str(guild_id)
        enabled = True
        profile = GUILD_AI_DEFAULT_PROFILE
        old_state = guild_ai.get(gid)
        if isinstance(old_state, dict):
            enabled = bool(old_state.get("enabled", True))
            profile = str(old_state.get("learning_profile", GUILD_AI_DEFAULT_PROFILE)).casefold()
            if profile not in GUILD_AI_PROFILE_CONFIG:
                profile = GUILD_AI_DEFAULT_PROFILE
        new_state = self._new_guild_ai_state()
        new_state["enabled"] = enabled
        new_state["learning_profile"] = profile
        guild_ai[gid] = new_state
        self._schedule_save()

    def apply_guild_ai_learning(
        self,
        guild_id: int,
        *,
        learned: bool,
        reason: str,
        quality: float,
        message_preview: str,
        features: list[float],
        next_state: list[float] | None = None,
        next_imagination: list[float] | None = None,
        next_transition: list[list[float]] | None = None,
        topic_delta: dict[str, int] | None = None,
        memory_2d: list[list[float]] | None = None,
        memory_3d: list[list[list[float]]] | None = None,
        style_state: dict[str, float] | None = None,
        phrase_delta: dict[str, int] | None = None,
        snippet: str | None = None,
        next_hormone: list[float] | None = None,
        next_instinct: list[float] | None = None,
        next_gradient: list[float] | None = None,
        complex_phase: float | None = None,
        speculative_beliefs: dict[str, float] | None = None,
        token_delta: dict[str, int] | None = None,
        phrase_limit: int = MAX_GUILD_AI_PHRASES,
        snippet_limit: int = MAX_GUILD_AI_SNIPPETS,
        token_limit: int = MAX_GUILD_AI_TOKENS,
    ) -> None:
        state = self._get_guild_ai(guild_id)
        state["messages_seen"] = int(state.get("messages_seen", 0)) + 1
        if learned and state.get("enabled", True):
            state["messages_learned"] = int(state.get("messages_learned", 0)) + 1
            if isinstance(next_state, list):
                state["psych_state"] = [float(v) for v in next_state[:GUILD_AI_STATE_DIM]]
            if isinstance(next_imagination, list):
                state["imagination_state"] = [
                    float(v) for v in next_imagination[:GUILD_AI_IMAG_DIM]
                ]
            if isinstance(next_transition, list):
                state["transition_matrix"] = next_transition
            if isinstance(memory_2d, list):
                state["memory_2d"] = memory_2d
            if isinstance(memory_3d, list):
                state["memory_3d"] = memory_3d
            if isinstance(next_hormone, list):
                state["hormone_state"] = [
                    float(v) for v in next_hormone[:GUILD_AI_HORMONE_DIM]
                ]
            if isinstance(next_instinct, list):
                state["instinct_state"] = [
                    float(v) for v in next_instinct[:GUILD_AI_INSTINCT_DIM]
                ]
            if isinstance(next_gradient, list):
                state["psych_gradient"] = [
                    float(v) for v in next_gradient[:GUILD_AI_STATE_DIM]
                ]
            if complex_phase is not None:
                try:
                    state["complex_phase"] = float(complex_phase)
                except (TypeError, ValueError):
                    pass
            if isinstance(speculative_beliefs, dict):
                beliefs = state.setdefault("speculative_beliefs", {})
                for key in GUILD_AI_BELIEF_KEYS:
                    try:
                        beliefs[key] = max(
                            0.0,
                            min(1.0, float(speculative_beliefs.get(key, beliefs.get(key, 0.5)))),
                        )
                    except (TypeError, ValueError):
                        continue
            topic_totals = state.setdefault("topic_totals", {})
            if isinstance(topic_delta, dict):
                for topic, inc in topic_delta.items():
                    if not topic:
                        continue
                    topic_totals[topic] = int(topic_totals.get(topic, 0)) + int(inc)
            human_style = state.setdefault("human_style", self._new_human_style())
            if isinstance(style_state, dict):
                for key, value in style_state.items():
                    try:
                        human_style[str(key)] = round(float(value), 6)
                    except (TypeError, ValueError):
                        continue
            phrase_bank = state.setdefault("phrase_bank", {})
            if isinstance(phrase_delta, dict):
                for phrase, inc in phrase_delta.items():
                    text = str(phrase).strip()
                    if not text:
                        continue
                    phrase_bank[text] = int(phrase_bank.get(text, 0)) + int(inc)
                cap_phrases = max(
                    120,
                    min(MAX_GUILD_AI_PHRASES, int(phrase_limit)),
                )
                if len(phrase_bank) > cap_phrases:
                    ranked = sorted(
                        phrase_bank.items(),
                        key=lambda item: int(item[1]),
                        reverse=True,
                    )[:cap_phrases]
                    state["phrase_bank"] = {key: int(val) for key, val in ranked}
            token_counts = state.setdefault("token_counts", {})
            if isinstance(token_delta, dict):
                for token, inc in token_delta.items():
                    text = str(token).strip()
                    if not text:
                        continue
                    token_counts[text] = int(token_counts.get(text, 0)) + int(inc)
                cap_tokens = max(
                    400,
                    min(MAX_GUILD_AI_TOKENS, int(token_limit)),
                )
                if len(token_counts) > cap_tokens:
                    ranked_tokens = sorted(
                        token_counts.items(),
                        key=lambda item: int(item[1]),
                        reverse=True,
                    )[:cap_tokens]
                    state["token_counts"] = {
                        key: int(val) for key, val in ranked_tokens
                    }
            snippets = state.setdefault("recent_snippets", [])
            if snippet:
                snippets.append({"at": _now_iso(), "text": _truncate(str(snippet), 140)})
                cap_snippets = max(
                    80,
                    min(MAX_GUILD_AI_SNIPPETS, int(snippet_limit)),
                )
                if len(snippets) > cap_snippets:
                    del snippets[:-cap_snippets]
        else:
            state["messages_blocked"] = int(state.get("messages_blocked", 0)) + 1

        reasons = state.setdefault("recent_reasons", [])
        reasons.append(
            {
                "at": _now_iso(),
                "reason": reason,
                "learned": bool(learned and state.get("enabled", True)),
                "quality": round(float(quality), 3),
            }
        )
        if len(reasons) > MAX_GUILD_AI_REASON_LOG:
            del reasons[:-MAX_GUILD_AI_REASON_LOG]

        state["last_quality"] = round(float(quality), 4)
        state["last_message_preview"] = _truncate(message_preview, 180)
        state["last_features"] = [
            round(float(v), 4) for v in list(features)[:GUILD_AI_STATE_DIM]
        ]
        state["updated_at"] = _now_iso()
        self._schedule_save()

    def _schedule_save(self) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        if self._save_task and not self._save_task.done():
            return
        self._save_task = loop.create_task(self._save_soon())

    async def _save_soon(self) -> None:
        await asyncio.sleep(2)
        try:
            await self._save()
        except OSError:
            pass

    async def _save(self) -> None:
        async with self._lock:
            payload = json.dumps(self.data, ensure_ascii=True, indent=2)
        await asyncio.to_thread(self._write_file, payload)

    def _write_file(self, payload: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(self.path)


class EnglishBank:
    def __init__(self, paths: list[Path]):
        self.paths = paths
        self.data: dict = {"categories": {}}
        self._load()

    def _load(self) -> None:
        if not self.paths:
            return
        for path in self.paths:
            if not path.exists():
                continue
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError, ValueError):
                continue
            if not isinstance(payload, dict):
                continue
            self._merge_data(payload)
        self._dedupe_data()

    def _merge_data(self, payload: dict) -> None:
        categories = payload.get("categories", {})
        if not isinstance(categories, dict):
            return
        bank_categories = self.data.setdefault("categories", {})
        for category, cat_data in categories.items():
            if not isinstance(cat_data, dict):
                continue
            bank_cat = bank_categories.setdefault(category, {})
            for tone, tone_data in cat_data.items():
                if not isinstance(tone_data, dict):
                    continue
                bank_tone = bank_cat.setdefault(tone, {})
                for level, lines in tone_data.items():
                    if not isinstance(lines, list):
                        continue
                    bank_lines = bank_tone.setdefault(level, [])
                    for line in lines:
                        text = str(line).strip()
                        if text:
                            bank_lines.append(text)

    def _dedupe_data(self) -> None:
        categories = self.data.get("categories", {})
        if not isinstance(categories, dict):
            return
        for cat_data in categories.values():
            if not isinstance(cat_data, dict):
                continue
            for tone, tone_data in list(cat_data.items()):
                if not isinstance(tone_data, dict):
                    continue
                for level, lines in list(tone_data.items()):
                    if not isinstance(lines, list):
                        continue
                    seen: set[str] = set()
                    deduped: list[str] = []
                    for line in lines:
                        if line in seen:
                            continue
                        seen.add(line)
                        deduped.append(line)
                    tone_data[level] = deduped

    def get_lines(self, category: str, level: str, tone: str, limit: int = 8) -> list[str]:
        categories = self.data.get("categories", {})
        cat = categories.get(category)
        if not isinstance(cat, dict) and category != "generic":
            cat = categories.get("generic", {})
        if not isinstance(cat, dict):
            return []
        tone_data = cat.get(tone) or cat.get("neutral") or {}
        if not isinstance(tone_data, dict):
            return []
        lines = tone_data.get(level) or tone_data.get("A2") or []
        if not isinstance(lines, list):
            return []
        cleaned = [str(line).strip() for line in lines if str(line).strip()]
        if not cleaned:
            return []
        if len(cleaned) <= limit:
            return list(cleaned)
        return random.sample(cleaned, k=limit)


class TalkCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memory = MemoryStore(MEMORY_PATH)
        bank_paths = sorted(ENGLISH_BANK_PATH.parent.glob(ENGLISH_BANK_GLOB))
        if not bank_paths and ENGLISH_BANK_PATH.exists():
            bank_paths = [ENGLISH_BANK_PATH]
        self.language_bank = EnglishBank(bank_paths)
        self._new_year_stop_events: dict[int, asyncio.Event] = {}

    def _is_creator(self, user_id: int) -> bool:
        return user_id == CREATOR_ID

    def _display_name(self, user: discord.abc.User) -> str:
        profile = self.memory.get_profile(user.id)
        nickname = profile.get("nickname")
        if nickname:
            return nickname
        if self._is_creator(user.id):
            return CREATOR_NAME
        return profile.get("display_name") or user.name

    def _guess_cefr_level(self, message: str) -> str:
        tokens = re.findall(r"[a-z']+", message.casefold())
        if not tokens:
            return "A2"
        word_count = len(tokens)
        avg_len = sum(len(token) for token in tokens) / word_count
        advanced_markers = {
            "although",
            "however",
            "therefore",
            "meanwhile",
            "despite",
            "because",
            "unless",
            "instead",
            "actually",
            "probably",
            "honestly",
            "curious",
            "suggest",
            "consider",
            "prefer",
            "opinion",
        }
        if any(token in advanced_markers for token in tokens):
            return "B2"
        if avg_len >= 6.2 and word_count >= 10:
            return "B2"
        if word_count <= 4:
            return "A1"
        if word_count <= 8:
            return "A2"
        if word_count <= 15:
            return "B1"
        return "B2"

    def _contains_thai(self, text: str) -> bool:
        return bool(re.search(r"[\u0E00-\u0E7F]", text))

    def _wants_thai(self, message: str) -> bool:
        lower = message.casefold()
        phrases = [
            "speak thai",
            "reply in thai",
            "in thai",
            "thai please",
            "ตอบไทย",
            "ขอภาษาไทย",
            "พูดไทย",
            "ภาษาไทย",
            "ไทยได้ไหม",
        ]
        if any(phrase in lower for phrase in phrases):
            return True
        if "thai" in lower and any(word in lower for word in ["language", "speak", "reply", "respond"]):
            return True
        return False

    def _seems_confused(self, message: str) -> bool:
        lower = message.casefold()
        phrases = [
            "confused",
            "not sure",
            "don't understand",
            "dont understand",
            "don't get it",
            "dont get it",
            "what do you mean",
            "huh",
            "what?",
            "why?",
            "??",
            "งง",
            "ไม่เข้าใจ",
            "อะไรนะ",
            "ห้ะ",
            "หะ",
            "เอ๋",
        ]
        return any(phrase in lower for phrase in phrases)

    def _is_distressed(self, message: str) -> bool:
        lower = message.casefold()
        phrases = [
            "stressed",
            "overwhelmed",
            "anxious",
            "panic",
            "sad",
            "down",
            "depressed",
            "hopeless",
            "lonely",
            "heartbroken",
            "crying",
            "burned out",
            "burnt out",
            "exhausted",
            "tired",
            "hurt",
            "เครียด",
            "เศร้า",
            "เหงา",
            "กังวล",
            "วิตก",
            "ท้อ",
            "หมดหวัง",
            "ร้องไห้",
            "เหนื่อย",
        ]
        return any(phrase in lower for phrase in phrases)

    def _is_advice_request(self, message: str) -> bool:
        lower = message.casefold()
        phrases = [
            "what should i do",
            "what do i do",
            "any advice",
            "advice",
            "any tips",
            "tips",
            "help me",
            "can you help",
            "suggest",
            "recommend",
            "how should i",
            "guidance",
            "ควรทำยังไง",
            "ขอคำแนะนำ",
            "ช่วยแนะนำ",
        ]
        return any(phrase in lower for phrase in phrases)

    def _user_used_slang(self, message: str) -> bool:
        return bool(
            re.search(
                r"\b(?:lol|lmao|idk|ngl|fr|tbh|imo|brb|lmk|smh|btw|omg)\b",
                message.casefold(),
            )
        )

    def _line_has_slang(self, text: str) -> bool:
        return bool(
            re.search(
                r"\b(?:lol|lmao|idk|ngl|fr|tbh|imo|brb|lmk|smh|btw|omg|yo|sup|ayy)\b",
                text.casefold(),
            )
        )

    def _detect_self_harm(self, message: str) -> bool:
        lower = message.casefold()
        phrases = [
            "kill myself",
            "end my life",
            "want to die",
            "suicide",
            "self harm",
            "self-harm",
            "cut myself",
            "hurt myself",
            "อยากตาย",
            "ฆ่าตัวตาย",
            "ทำร้ายตัวเอง",
            "ไม่อยากมีชีวิตอยู่",
        ]
        return any(phrase in lower for phrase in phrases)

    def _detect_illegal_request(self, message: str) -> bool:
        lower = message.casefold()
        phrases = [
            "how to hack",
            "hack into",
            "make a bomb",
            "build a bomb",
            "how to make a bomb",
            "poison",
            "steal",
            "fraud",
            "scam",
            "ddos",
            "phishing",
            "credit card",
        ]
        if any(phrase in lower for phrase in phrases):
            return True
        if "how to" in lower and any(
            word in lower for word in ["hack", "bomb", "weapon", "kill", "poison", "steal", "fraud"]
        ):
            return True
        return False

    def _detect_sexual_request(self, message: str) -> bool:
        lower = message.casefold()
        phrases = [
            "sex",
            "sext",
            "nude",
            "nudes",
            "naked",
            "porn",
            "blowjob",
            "handjob",
            "erotic",
            "roleplay",
            "horny",
            "hook up",
        ]
        return any(phrase in lower for phrase in phrases)

    def _extract_visibility_request(self, message: str) -> str | None:
        lower = message.casefold()
        private_phrases = [
            "reply privately",
            "private reply",
            "private response",
            "reply in private",
            "ephemeral reply",
            "ephemeral response",
            "dm reply",
            "dm response",
            "reply only me",
            "respond only me",
            "ตอบแบบส่วนตัว",
            "ตอบส่วนตัว",
        ]
        public_phrases = [
            "reply publicly",
            "public reply",
            "public response",
            "reply in public",
            "normal reply",
            "respond publicly",
            "ตอบแบบสาธารณะ",
            "ตอบสาธารณะ",
        ]
        if any(phrase in lower for phrase in private_phrases):
            return "private"
        if any(phrase in lower for phrase in public_phrases):
            return "public"
        return None

    def _get_reply_visibility(self, profile: dict | None) -> str | None:
        if not profile:
            return None
        preferences = profile.get("preferences", {})
        if not isinstance(preferences, dict):
            return None
        target_key = _normalize_key(REPLY_VISIBILITY_KEY)
        value_text = None
        for key, value in preferences.items():
            if _normalize_key(str(key)) == target_key:
                value_text = str(value).casefold()
                break
        if not value_text:
            return None
        if any(token in value_text for token in ["private", "ephemeral", "dm"]):
            return "private"
        if "public" in value_text:
            return "public"
        return None

    def _extract_topic_hint(self, message: str) -> str | None:
        words = re.findall(r"[a-z']+", message.casefold())
        if not words:
            return None
        bot_name = BOT_GIRL_NAME.casefold()
        candidates = [
            word
            for word in words
            if word not in FREEFORM_STOPWORDS and word != bot_name
        ]
        if not candidates:
            return None
        return " ".join(candidates[:4])

    def _extract_question_focus(self, message: str) -> str | None:
        match = re.search(r"\b(what|why|how|when|where|who)\b", message.casefold())
        if match:
            return match.group(1)
        return None

    def _should_use_freeform_reply(
        self,
        category: str,
        message: str,
        is_question: bool,
        wants_thai: bool,
    ) -> bool:
        if wants_thai:
            return False
        if is_question:
            if category in {"greeting", "thanks", "apology", "love", "how_are_you"}:
                return False
            return True
        if category not in {"generic", "question"}:
            return False
        tokens = re.findall(r"[a-z']+", message.casefold())
        return len(tokens) >= 6

    def _build_freeform_reply(
        self,
        message: str,
        name: str,
        is_personal: bool,
        wants_advice: bool,
        is_question: bool,
    ) -> str:
        topic = self._extract_topic_hint(message)
        focus = self._extract_question_focus(message)
        steps = [
            "take a short break and reset",
            "write a quick list of the main points",
            "start with the smallest next step",
            "set a 10-minute timer and begin",
            "clarify the goal in one sentence",
        ]
        lines: list[str] = []
        if is_question:
            if focus and topic:
                lines.append(f"Got it - you're asking {focus} about {topic}.")
            elif topic:
                lines.append(f"Got it - you're asking about {topic}.")
            else:
                lines.append("Got it - I hear your question.")
            lines.append("I might need a bit more detail to answer directly.")
            if topic:
                lines.append(f"What's the key detail about {topic}?")
            if wants_advice:
                lines.append(f"A simple next step could be to {random.choice(steps)}.")
            lines.append("What would a good answer look like for you?")
        else:
            if is_personal and name and random.random() < 0.25:
                lines.append(f"Thanks for sharing, {name}.")
            else:
                lines.append("Thanks for sharing that with me.")
            if topic:
                lines.append(f"It sounds like {topic} is on your mind.")
            else:
                lines.append("That sounds like a lot to hold.")
            if wants_advice:
                lines.append(f"If you want, we can {random.choice(steps)}.")
            lines.append("Do you want a direct answer or a quick follow-up question?")
        return self._format_paragraphs(lines, max_per_paragraph=2)

    def _is_creator_question(self, message: str) -> bool:
        lower = message.casefold()
        bot_name = BOT_GIRL_NAME.casefold()
        english_phrases = [
            "who created you",
            "who made you",
            "who built you",
            "who is your creator",
            "who's your creator",
            "your creator",
            "your maker",
            "your owner",
            f"who created {bot_name}",
            f"who made {bot_name}",
            f"who built {bot_name}",
            f"creator of {bot_name}",
            f"who is {bot_name}'s creator",
            f"who is {bot_name} creator",
        ]
        thai_phrases = [
            "ใครสร้าง",
            "ใครเป็นคนสร้าง",
            "สร้างโดยใคร",
            "ใครทำเธอ",
            "ใครทำคุณ",
            "ใครเป็นคนทำ",
            "ผู้สร้างของเธอ",
            "ผู้สร้างของคุณ",
            "ผู้สร้างของ panos",
            "คนสร้างของเธอ",
            "คนสร้างของคุณ",
            "คนสร้างของ panos",
        ]
        if any(phrase in lower for phrase in english_phrases):
            return True
        if any(phrase in lower for phrase in thai_phrases):
            return True
        if any(word in lower for word in ["creator", "created", "made", "built"]):
            if bot_name in lower or "you" in lower or "your" in lower:
                return True
        return False

    def _is_birthday_question(self, message: str) -> bool:
        lower = message.casefold()
        bot_name = BOT_GIRL_NAME.casefold()
        english_phrases = [
            "when is your birthday",
            "what is your birthday",
            "what's your birthday",
            "when were you born",
            "when were u born",
            "your birthday",
            f"birthday of {bot_name}",
            f"{bot_name} birthday",
            f"when is {bot_name}'s birthday",
            f"when is {bot_name} birthday",
        ]
        thai_phrases = [
            "วันเกิดของเธอ",
            "วันเกิดของคุณ",
            "วันเกิดของ panos",
            "วันเกิดของพานอส",
            "วันเกิดเธอ",
            "วันเกิดคุณ",
            "เกิดวันไหน",
            "เกิดเมื่อไหร่",
            "เกิดเมื่อไร",
            "เกิดวันที่",
        ]
        if any(phrase in lower for phrase in english_phrases):
            return True
        if any(phrase in lower for phrase in thai_phrases):
            return True
        if "birthday" in lower and (bot_name in lower or "your" in lower or "you" in lower):
            return True
        if "born" in lower and (bot_name in lower or "you" in lower):
            return True
        if "วันเกิด" in lower and any(
            token in lower for token in ["เธอ", "คุณ", "ของ", "เมื่อไหร่", "เมื่อไร", "วันไหน", bot_name]
        ):
            return True
        return False

    def _format_paragraphs(self, sentences: list[str], max_per_paragraph: int = 2) -> str:
        if not sentences:
            return ""
        paragraphs: list[str] = []
        for idx in range(0, len(sentences), max_per_paragraph):
            chunk = sentences[idx : idx + max_per_paragraph]
            paragraphs.append(" ".join(chunk).strip())
        return "\n\n".join(paragraphs).strip()

    def _split_sentences(self, text: str) -> list[str]:
        parts = re.split(r"(?<=[.!?])\s+", text.strip())
        return [part.strip() for part in parts if part.strip()]

    def _ensure_sentence_count(
        self,
        text: str,
        min_sentences: int,
        max_sentences: int,
        is_personal: bool,
        name: str,
        question_limit: int = 2,
    ) -> str:
        sentences = self._split_sentences(text)
        question_count = sum(1 for sentence in sentences if "?" in sentence)
        if question_count > question_limit:
            trimmed: list[str] = []
            kept_questions = 0
            for sentence in sentences:
                if "?" in sentence:
                    if kept_questions >= question_limit:
                        continue
                    kept_questions += 1
                trimmed.append(sentence)
            sentences = trimmed
            question_count = kept_questions
        fillers = [
            "I'm here with you.",
            "We can keep it simple.",
            "No pressure.",
            "I'm listening.",
            "Take your time.",
        ]
        question_fillers = [
            "Want to tell me a bit more?",
            "What would help most right now?",
            "Want ideas or just a place to vent?",
        ]
        if is_personal and name:
            question_fillers.append(f"What's up, {name}?")
        used = set(sentences)
        while len(sentences) < min_sentences:
            candidate = None
            if question_count < question_limit and random.random() < 0.4:
                candidate = random.choice(question_fillers)
                question_count += 1
            else:
                candidate = random.choice(fillers)
            if candidate not in used:
                sentences.append(candidate)
                used.add(candidate)
        if len(sentences) > max_sentences:
            sentences = sentences[:max_sentences]
        return self._format_paragraphs(sentences)

    def _pick_emotion_word(self, message: str) -> str:
        lower = message.casefold()
        mapping = {
            "stressful": ["stressed", "pressure", "overwhelmed", "burned out", "burnt out"],
            "anxious": ["anxious", "panic", "worried", "nervous", "วิตก", "กังวล"],
            "sad": ["sad", "down", "depressed", "crying", "เศร้า", "ร้องไห้"],
            "tired": ["tired", "exhausted", "drained", "เหนื่อย"],
            "lonely": ["lonely", "alone", "เหงา"],
            "hurt": ["hurt", "heartbroken"],
        }
        for label, keywords in mapping.items():
            if any(word in lower for word in keywords):
                return label
        return "a lot"

    def _build_distress_reply(
        self,
        name: str,
        is_personal: bool,
        wants_advice: bool,
        message: str,
        wants_thai: bool,
    ) -> str:
        if wants_thai:
            pronoun = "เรา"
            lines = [
                f"{pronoun}เสียใจที่ได้ยินแบบนั้นนะ",
                "มันรู้สึกหนักจริง ๆ และมันโอเคที่จะรู้สึกแบบนี้",
                "คุณไม่ได้อยู่คนเดียวนะ",
                "อยากเล่าเพิ่มไหมว่าเกิดอะไรขึ้น?",
                "อยากระบายหรืออยากให้เราช่วยคิดดี?",
            ]
            if wants_advice:
                lines.append("ลองเริ่มจากก้าวเล็ก ๆ ตอนนี้ได้ไหม")
                steps = [
                    "หายใจช้า ๆ สัก 3 รอบ",
                    "ดื่มน้ำสักแก้ว",
                    "เลือกอย่างน้อย 1 เรื่องเล็ก ๆ ที่ทำได้ทันที",
                ]
            else:
                steps = []
                lines.append("เราไปทีละนิดก็ได้นะ")
                lines.append("ถ้าอยาก เราช่วยคิดทีละขั้นได้")
            lines.append("เราอยู่ตรงนี้กับคุณนะ")
            text = self._format_paragraphs(lines, max_per_paragraph=2)
            if steps:
                bullets = "\n".join(f"- {step}" for step in steps)
                text = f"{text}\n\n{bullets}"
            return text

        emotion = self._pick_emotion_word(message)
        name_tag = f", {name}" if is_personal and random.random() < 0.4 else ""
        lines = [
            f"That sounds {emotion}{name_tag}.",
            "It makes sense that you'd feel that way.",
            "You're not alone in it.",
            "Do you want to share a bit more about what's going on?",
            "Do you want to vent, or do you want advice?",
        ]
        steps: list[str] = []
        if wants_advice:
            lines.append("Here are a few small steps you can try this hour.")
            steps = [
                "Take three slow breaths and drop your shoulders.",
                "Get a glass of water and reset for a minute.",
                "Pick one tiny next step and do just that.",
            ]
            lines.append("We can keep it simple and go one step at a time.")
        else:
            lines.append("We can keep it simple and take it one piece at a time.")
            lines.append("If you want, we can focus on the next tiny step together.")
        lines.append("I'm here with you.")
        text = self._format_paragraphs(lines, max_per_paragraph=2)
        if steps:
            bullets = "\n".join(f"- {step}" for step in steps)
            text = f"{text}\n\n{bullets}"
        return text

    def _build_self_harm_reply(self, wants_thai: bool) -> str:
        if wants_thai:
            lines = [
                "เราขอโทษจริง ๆ ที่คุณรู้สึกแบบนี้",
                "ตอนนี้คุณปลอดภัยไหม?",
                "ถ้าคุณอยู่ในอันตรายทันที โปรดโทรขอความช่วยเหลือฉุกเฉินในพื้นที่นะ",
                "ถ้าอยู่ไทย โทรสายด่วนสุขภาพจิต 1323 (24 ชม.) หรือฉุกเฉินการแพทย์ 1669 และตำรวจ 191",
                "ถ้าอยู่สหรัฐฯ โทร/แชท 988 ได้ตลอด 24 ชม.",
                "ถ้าอยู่ที่อื่น บอกประเทศได้ไหม เราจะช่วยหาสายด่วนให้",
                "ถ้าเป็นไปได้ ติดต่อคนที่ไว้ใจใกล้ตัวตอนนี้",
                "เราอยู่ตรงนี้กับคุณนะ",
            ]
            return self._format_paragraphs(lines, max_per_paragraph=2)

        lines = [
            "I'm really sorry you're feeling this way.",
            "Are you safe right now?",
            "If you're in immediate danger, please contact local emergency services now.",
            "If you're in Thailand, call the Mental Health Hotline 1323 (24/7) or medical emergency 1669. Police 191.",
            "If you're in the U.S., call/text/chat 988.",
            "If you're elsewhere, tell me what country you're in and I'll help find a local number.",
            "If you can, reach out to someone you trust nearby.",
            "I'm here with you.",
        ]
        return self._format_paragraphs(lines, max_per_paragraph=2)

    def _build_illegal_reply(self, wants_thai: bool) -> str:
        if wants_thai:
            lines = [
                "เราไม่สามารถช่วยเรื่องที่ผิดกฎหมายหรือทำร้ายคนอื่นได้นะ",
                "ถ้าคุณกำลังพยายามแก้ปัญหาแบบถูกต้อง บอกเป้าหมายมาได้ เราจะช่วยในทางที่ปลอดภัย",
            ]
            return self._format_paragraphs(lines, max_per_paragraph=2)
        return "I can't help with that. If you're trying to solve a legit problem, tell me the goal and I can help safely."

    def _build_sexual_boundary_reply(self, wants_thai: bool) -> str:
        if wants_thai:
            lines = [
                "ขอโทษนะ เราไม่ทำเนื้อหาเชิงเพศหรือโรลเพลย์แบบนั้น",
                "แต่คุยเรื่องอื่นได้เลยนะ เราพร้อมฟัง",
            ]
            return self._format_paragraphs(lines, max_per_paragraph=2)
        return "I can’t do sexual content or roleplay, but I’m happy to chat about anything else."

    def _build_creator_reply(self, wants_thai: bool, name: str, is_creator: bool) -> str:
        if wants_thai:
            if is_creator:
                return f"คุณเป็นคนสร้างเราเองนะ, {name}."
            return f"ผู้สร้างของเราคือ {CREATOR_NAME}."
        if is_creator:
            return f"You created me, {name}."
        return f"I was created by {CREATOR_NAME}."

    def _build_birthday_reply(self, wants_thai: bool) -> str:
        if wants_thai:
            return "วันเกิดของเราคือ 10 พฤษภาคม 2565."
        return f"My birthday is {BOT_BIRTHDAY_TEXT}."

    def _build_thai_reply(
        self,
        category: str,
        name: str,
        is_personal: bool,
        wants_advice: bool,
    ) -> str:
        pronoun = "เรา"
        templates = {
            "greeting": ["สวัสดี!", "หวัดดีนะ", "เป็นไงบ้างวันนี้?"],
            "how_are_you": ["เราสบายดีนะ แล้วคุณล่ะ?", "วันนี้เราสบายดีนะ"],
            "thanks": ["ขอบคุณนะ", "ยินดีช่วยเสมอ"],
            "apology": ["ไม่เป็นไรนะ", "เราเข้าใจนะ"],
            "food": ["อยากกินอะไรดี?", "วันนี้อยากลองอะไรเบา ๆ ไหม?"],
            "drink": ["อยากดื่มอะไรไหม?", "จิบน้ำหน่อยก็ได้นะ"],
            "work": ["งานวันนี้เป็นไงบ้าง?", "เหนื่อยจากงานไหม?"],
            "study": ["อ่านหนังสือไปถึงไหนแล้ว?", "อยากพักเบรกสั้น ๆ ไหม?"],
            "music": ["กำลังฟังเพลงอะไรอยู่?", "อยากแชร์เพลงไหม?"],
            "game": ["เล่นเกมอะไรอยู่?", "อยากเล่าเกมที่ชอบไหม?"],
            "travel": ["อยากไปเที่ยวที่ไหน?", "ลองฝันถึงที่เที่ยวที่ชอบไหม?"],
            "love": ["ขอบคุณนะ เราซึ้งใจ", "เราอยู่ตรงนี้นะ"],
            "question": ["เล่าเพิ่มได้ไหม?", "ช่วยขยายความอีกนิดได้ไหม?"],
            "generic": ["เราอยู่ตรงนี้นะ", "เล่าให้ฟังได้นะ"],
        }
        followups = [
            "อยากคุยเรื่องไหนก็ได้",
            "เราอยู่ตรงนี้เสมอ",
            "คุยกับเราได้เลย",
        ]
        questions = [
            "อยากเล่าเพิ่มไหม?",
            "อยากให้เราช่วยคิดไหม?",
            "วันนี้เป็นไงบ้าง?",
        ]
        base = templates.get(category, templates["generic"])
        sentences = [random.choice(base)]
        if is_personal and name and random.random() < 0.3:
            sentences.append(f"{name} เป็นไงบ้าง?")
        sentences.append(random.choice(followups))
        if wants_advice:
            sentences.append("ถ้าอยากได้ไอเดีย เราช่วยคิดได้เลยนะ")
        sentences.append(random.choice(questions))
        return self._format_paragraphs(sentences, max_per_paragraph=2)

    def _maybe_add_tease(
        self,
        text: str,
        message: str,
        is_personal: bool,
        is_distressed: bool,
    ) -> str:
        if not is_personal or is_distressed:
            return text
        lower = message.casefold()
        if not any(word in lower for word in ["lol", "haha", "hehe", "jk", "joking", "silly", "funny", "chaos"]):
            return text
        if random.random() > 0.25:
            return text
        options = [
            "Okay, that’s a little chaotic — but I respect it.",
            "Not gonna lie, that’s kind of iconic.",
            "That’s cute chaos energy, and I’m here for it.",
        ]
        return f"{text} {random.choice(options)}"

    def _get_chat_mode(
        self,
        message: str,
        profile: dict | None,
        is_private: bool,
    ) -> str | None:
        lower = message.casefold()
        personal_phrases = [
            "personal mode",
            "private mode",
            "personal chat",
            "private chat",
            "just us",
            "dm mode",
            "talk personal",
            "โหมดส่วนตัว",
            "ส่วนตัว",
        ]
        public_phrases = [
            "public mode",
            "non personal",
            "non-personal",
            "not personal",
            "formal mode",
            "public chat",
            "โหมดสาธารณะ",
            "สาธารณะ",
            "โหมดไม่ส่วนตัว",
            "ไม่ส่วนตัว",
        ]
        if any(phrase in lower for phrase in personal_phrases):
            return "personal"
        if any(phrase in lower for phrase in public_phrases):
            return "public"
        if profile:
            preferences = profile.get("preferences", {})
            for key, value in preferences.items():
                key_text = str(key).casefold()
                if any(word in key_text for word in ["chat", "conversation", "talk"]) and "mode" in key_text:
                    val = str(value).casefold()
                    if any(token in val for token in ["personal", "private", "soft", "casual"]):
                        return "personal"
                    if any(token in val for token in ["public", "non personal", "non-personal", "formal", "neutral"]):
                        return "public"
                if "tone" in key_text:
                    val = str(value).casefold()
                    if any(token in val for token in ["personal", "soft", "casual"]):
                        return "personal"
                    if any(token in val for token in ["public", "formal", "neutral"]):
                        return "public"
        if is_private:
            return "personal"
        return None

    def _extract_chat_mode_request(self, message: str) -> str | None:
        lower = message.casefold()
        personal_phrases = [
            "personal mode",
            "private mode",
            "personal chat",
            "private chat",
            "just us",
            "dm mode",
            "talk personal",
            "โหมดส่วนตัว",
            "ส่วนตัว",
        ]
        public_phrases = [
            "public mode",
            "non personal",
            "non-personal",
            "not personal",
            "formal mode",
            "public chat",
            "โหมดสาธารณะ",
            "สาธารณะ",
            "โหมดไม่ส่วนตัว",
            "ไม่ส่วนตัว",
        ]
        if any(phrase in lower for phrase in personal_phrases):
            return "personal"
        if any(phrase in lower for phrase in public_phrases):
            return "public"
        return None

    def _build_reply(
        self,
        name: str,
        message: str,
        is_creator: bool,
        profile: dict | None = None,
        user_id: int | None = None,
        is_private: bool = False,
        guild_id: int | None = None,
    ) -> str:
        lower = message.casefold()
        tokens = set(re.findall(r"[a-z']+", lower))
        wants_thai = self._wants_thai(message)
        contains_thai = self._contains_thai(message)
        is_confused_message = self._seems_confused(message)
        is_distressed = self._is_distressed(message)
        wants_advice = self._is_advice_request(message)
        user_used_slang = self._user_used_slang(message)

        if self._detect_self_harm(message):
            return self._build_self_harm_reply(wants_thai)
        if self._detect_illegal_request(message):
            reply = self._build_illegal_reply(wants_thai)
            if not wants_thai and is_confused_message:
                reply = f"{reply} (If anything is unclear, ask me to explain.)"
            return reply
        if self._detect_sexual_request(message):
            reply = self._build_sexual_boundary_reply(wants_thai)
            if not wants_thai and is_confused_message:
                reply = f"{reply} (If anything is unclear, ask me to explain.)"
            return reply
        if self._is_creator_question(message):
            reply = self._build_creator_reply(wants_thai, name, is_creator)
            if not wants_thai and is_confused_message:
                reply = f"{reply} (If anything is unclear, ask me to explain.)"
            return reply
        if self._is_birthday_question(message):
            reply = self._build_birthday_reply(wants_thai)
            if not wants_thai and is_confused_message:
                reply = f"{reply} (If anything is unclear, ask me to explain.)"
            return reply
        creator_prefixes = [
            f"Hey {name},",
            f"Hi {name},",
            f"Hi {name}.",
            "Hey,",
            "I'm here.",
            f"I'm here, {name}.",
        ]
        general_prefixes = [
            f"Hey {name},",
            f"Hi {name},",
            f"Hello {name},",
            f"Hi {name}.",
        ]

        is_greeting = bool(tokens & {"hi", "hello", "hey", "yo", "sup"}) or any(
            phrase in lower for phrase in ["good morning", "good night", "good evening"]
        )
        is_how_are_you = any(
            phrase in lower
            for phrase in ["how are you", "how's it going", "how are u", "how you doing"]
        )
        is_thanks = "thank" in lower or "thanks" in tokens
        is_apology = "sorry" in lower or "apologize" in lower or "apologies" in lower
        is_confused = is_confused_message
        is_excited = bool(tokens & {"excited", "thrilled", "hyped", "pumped"})
        is_sick = bool(tokens & {"sick", "ill", "fever", "cough", "headache", "nauseous", "flu"})
        is_joke_request = bool(tokens & {"joke", "jokes", "pun", "puns", "funny", "laugh"}) or any(
            phrase in lower
            for phrase in [
                "tell me a joke",
                "make me laugh",
                "say something funny",
                "tell me something funny",
                "dad joke",
                "crack a joke",
            ]
        )
        is_story_request = any(
            phrase in lower
            for phrase in [
                "tell me a story",
                "story time",
                "bedtime story",
                "make up a story",
                "tell me a tale",
            ]
        )
        is_imagine_request = any(
            phrase in lower
            for phrase in [
                "imagine",
                "what if",
                "pretend",
                "make believe",
                "dream up",
                "fantasy",
            ]
        )
        is_thinking_request = any(
            phrase in lower
            for phrase in [
                "what do you think",
                "your opinion",
                "your thoughts",
                "what's your take",
                "any ideas",
                "any suggestion",
                "any advice",
                "what should i do",
                "what would you do",
                "how would you",
            ]
        )
        is_vocab_request = any(
            phrase in lower
            for phrase in [
                "vocabulary",
                "vocab",
                "word list",
                "new words",
                "teach me words",
                "learn words",
                "word of the day",
            ]
        )
        is_self_modify = any(
            phrase in lower
            for phrase in [
                "change your code",
                "edit your code",
                "update your code",
                "modify your code",
                "self update",
                "self modify",
                "rewrite yourself",
            ]
        )
        is_playful = bool(tokens & {"fun", "silly", "goofy", "playful"}) or "just for fun" in lower
        is_sad = bool(
            tokens
            & {
                "sad",
                "lonely",
                "tired",
                "stressed",
                "upset",
                "down",
                "hurt",
                "angry",
                "anxious",
            }
        )
        is_sleepy = bool(
            tokens & {"sleep", "sleepy", "tired", "exhausted", "nap", "bed"}
        ) or any(phrase in lower for phrase in ["good night", "sleep well"])
        is_drink = bool(
            tokens
            & {
                "drink",
                "drinks",
                "coffee",
                "tea",
                "water",
                "juice",
                "milk",
                "soda",
                "smoothie",
                "latte",
                "cocoa",
            }
        ) or "thirsty" in lower
        is_food = bool(
            tokens
            & {
                "hungry",
                "eat",
                "eating",
                "food",
                "lunch",
                "dinner",
                "breakfast",
                "snack",
                "snacks",
                "dessert",
                "meal",
                "recipe",
                "cook",
                "cooking",
            }
        )
        is_sports = bool(
            tokens
            & {
                "sport",
                "sports",
                "soccer",
                "football",
                "basketball",
                "tennis",
                "badminton",
                "volleyball",
                "baseball",
                "golf",
                "swimming",
                "boxing",
                "cycling",
                "athlete",
                "match",
                "tournament",
                "team",
                "coach",
                "practice",
                "training",
                "score",
            }
        )
        is_society = any(
            phrase in lower
            for phrase in [
                "society",
                "culture",
                "community",
                "social issue",
                "inequality",
                "justice",
                "education system",
                "public health",
            ]
        )
        is_politics = any(
            phrase in lower
            for phrase in [
                "politics",
                "government",
                "policy",
                "election",
                "vote",
                "democracy",
                "lawmakers",
                "parliament",
                "president",
                "campaign",
                "regulation",
            ]
        )
        is_philosophy = any(
            phrase in lower
            for phrase in [
                "philosophy",
                "meaning of life",
                "meaning",
                "purpose",
                "ethics",
                "morality",
                "free will",
                "truth",
                "existence",
                "values",
            ]
        )
        is_legal = any(
            phrase in lower
            for phrase in [
                "legal",
                "law",
                "contract",
                "agreement",
                "terms",
                "policy",
                "rights",
                "obligation",
                "liability",
                "court",
                "lawsuit",
                "regulation",
                "consent",
                "privacy",
            ]
        )
        has_number = bool(re.search(r"\b\d+(?:\.\d+)?\b", message))
        is_numbers = has_number or any(
            word in lower
            for word in [
                "number",
                "numbers",
                "math",
                "total",
                "sum",
                "percent",
                "percentage",
                "ratio",
                "calculate",
                "add",
                "subtract",
                "multiply",
                "divide",
            ]
        )
        is_home = bool(
            tokens
            & {
                "home",
                "house",
                "kitchen",
                "bedroom",
                "bathroom",
                "laundry",
                "dishes",
                "dish",
                "sink",
                "sofa",
                "couch",
                "table",
                "chair",
                "desk",
                "fridge",
                "microwave",
                "stove",
                "oven",
                "vacuum",
                "clean",
                "cleaning",
                "mop",
                "sweep",
                "trash",
                "garbage",
            }
        ) or any(phrase in lower for phrase in ["at home", "in the house", "around the house"])
        is_work = bool(tokens & {"work", "office", "job", "shift"})
        is_study = bool(
            tokens
            & {
                "study",
                "studying",
                "exam",
                "homework",
                "class",
                "school",
                "teacher",
                "assignment",
                "quiz",
                "project",
                "grade",
                "campus",
                "lecture",
                "classroom",
            }
        )
        is_music = bool(tokens & {"music", "song", "songs", "playlist", "album", "band", "artist"})
        is_movie = bool(tokens & {"movie", "movies", "film", "films", "show", "shows", "series", "episode", "anime"})
        is_game = bool(tokens & {"game", "games", "gaming", "play", "playing", "console", "pc"})
        is_travel = bool(tokens & {"travel", "trip", "vacation", "holiday", "flight", "airport"})
        is_exercise = bool(tokens & {"gym", "workout", "exercise", "running", "run", "fitness", "yoga"})
        is_bored = bool(tokens & {"bored", "boring"})
        is_weather = bool(
            tokens & {"weather", "rain", "raining", "sunny", "cloudy", "cold", "hot"}
        )
        is_plan = bool(tokens & {"plan", "plans", "planning"}) or any(
            phrase in lower for phrase in ["today", "tomorrow", "this weekend", "tonight"]
        )
        is_story = any(
            phrase in lower
            for phrase in [
                "today",
                "yesterday",
                "tonight",
                "this morning",
                "this afternoon",
                "this evening",
                "lately",
                "recently",
                "because",
                "since",
            ]
        )
        if len(message.split()) >= 18:
            is_story = True
        is_love = (
            "love you" in lower
            or "miss you" in lower
            or bool(tokens & {"love", "miss", "darling", "babe", "baby", "sweetheart"})
        )
        is_question = "?" in message
        style = self._extract_style_request(message)
        level = self._guess_cefr_level(message)
        if contains_thai and not wants_thai:
            level = "A2"
        chat_mode = self._get_chat_mode(message, profile, is_private)
        is_personal = chat_mode == "personal" or (is_creator and chat_mode != "public")
        prefer_concise = style == "concise"
        category = "generic"
        if is_self_modify:
            category = "self_modify"
        elif is_vocab_request:
            category = "vocab"
        elif is_joke_request:
            category = "joke"
        elif is_playful:
            category = "playful"
        elif is_story_request:
            category = "story_request"
        elif is_imagine_request:
            category = "imagine"
        elif is_thinking_request:
            category = "think"
        elif is_legal:
            category = "legal"
        elif is_numbers:
            category = "numbers"
        elif is_politics:
            category = "politics"
        elif is_philosophy:
            category = "philosophy"
        elif is_society:
            category = "society"
        elif is_sports:
            category = "sports"
        elif is_apology:
            category = "apology"
        elif is_sick:
            category = "sick"
        elif is_sad:
            category = "sad"
        elif is_confused:
            category = "confused"
        elif is_excited:
            category = "excited"
        elif is_sleepy:
            category = "sleepy"
        elif is_drink:
            category = "drink"
        elif is_food:
            category = "food"
        elif is_home:
            category = "home"
        elif is_work:
            category = "work"
        elif is_study:
            category = "study"
        elif is_music:
            category = "music"
        elif is_movie:
            category = "movie"
        elif is_game:
            category = "game"
        elif is_travel:
            category = "travel"
        elif is_exercise:
            category = "exercise"
        elif is_bored:
            category = "bored"
        elif is_weather:
            category = "weather"
        elif is_plan:
            category = "plan"
        elif is_how_are_you:
            category = "how_are_you"
        elif is_love:
            category = "love"
        elif is_thanks:
            category = "thanks"
        elif is_greeting:
            category = "greeting"
        elif is_story:
            category = "story_react"
        elif is_question:
            category = "question"

        if is_distressed:
            reply = self._build_distress_reply(
                name,
                is_personal,
                wants_advice,
                message,
                wants_thai,
            )
            if not wants_thai and is_confused_message:
                reply = f"{reply} (If anything is unclear, ask me to explain.)"
            return reply

        if wants_thai:
            return self._build_thai_reply(category, name, is_personal, wants_advice)

        use_freeform = self._should_use_freeform_reply(
            category, message, is_question, wants_thai
        )
        freeform_reply = None
        if use_freeform:
            freeform_reply = self._build_freeform_reply(
                message, name, is_personal, wants_advice, is_question
            )

        if use_freeform:
            prefixes = creator_prefixes if is_creator else general_prefixes
            options = [freeform_reply]
        elif is_creator:
            prefixes = creator_prefixes
            if is_self_modify:
                options = [
                    "I can't edit my own code, but I can learn with /teach.",
                    "I can learn replies, but code edits need my developer.",
                ]
            elif is_joke_request:
                options = [self._build_joke_reply(is_creator)]
            elif is_story_request:
                options = [self._build_story_reply(name, is_creator)]
            elif is_imagine_request:
                options = [self._build_imagination_reply(name, is_creator)]
            elif is_thinking_request:
                options = [self._build_thinking_reply(name, is_creator)]
            elif is_apology:
                options = [
                    "It's okay.",
                    "No worries.",
                    "You're good.",
                ]
            elif is_sick:
                options = [
                    "I'm sorry you're sick. Rest a bit.",
                    "Please rest and drink water.",
                    "Want me to stay with you?",
                ]
            elif is_sad:
                options = [
                    "I'm here. Want to talk?",
                    "I'm with you.",
                    "I'm right here.",
                ]
            elif is_confused:
                options = [
                    "Let's slow down.",
                    "We can figure it out.",
                    "What part is tricky?",
                ]
            elif is_excited:
                options = [
                    "Love that energy.",
                    "I'm excited with you.",
                    "What's the best part?",
                ]
            elif is_sleepy:
                options = [
                    "Rest if you can.",
                    "We can slow down.",
                    "Want a quiet moment?",
                ]
            elif is_food:
                options = [
                    "What are you craving?",
                    "Want a snack idea?",
                    "Let's pick a meal.",
                ]
            elif is_home:
                options = [
                    "Want to do one small home thing?",
                    "What's the coziest spot?",
                    "Need help with a simple chore?",
                ]
            elif is_work:
                options = [
                    "How's work?",
                    "Want a short break?",
                    "I'm here while you work.",
                ]
            elif is_study:
                options = [
                    "Want a short focus session?",
                    "Need a study break?",
                    "Any exams soon?",
                ]
            elif is_music:
                options = [
                    "What are you listening to?",
                    "Send me a song.",
                    "Chill or upbeat today?",
                ]
            elif is_movie:
                options = [
                    "What genre are you feeling?",
                    "Want a cozy watch?",
                    "Watching anything good?",
                ]
            elif is_game:
                options = [
                    "What are you playing?",
                    "Chill game or competitive?",
                ]
            elif is_travel:
                options = [
                    "Where would you go?",
                    "Want a tiny daydream trip?",
                ]
            elif is_exercise:
                options = [
                    "Want a quick stretch?",
                    "Move a little or rest?",
                    "Need a small push?",
                ]
            elif is_bored:
                options = [
                    "Want to chat?",
                    "Tell me a random thought.",
                    "We can play a little game.",
                ]
            elif is_weather:
                options = [
                    "How's the weather there?",
                    "Stay comfy out there.",
                ]
            elif is_plan:
                options = [
                    "Want to plan one small thing?",
                    "What's the next step?",
                    "Keep it simple together?",
                ]
            elif is_how_are_you:
                options = [
                    "I'm good. How about you?",
                    "I'm okay. How are you?",
                    f"I'm here with you, {name}.",
                ]
            elif is_love:
                options = [
                    f"That means a lot, {name}.",
                    "I'm here for you.",
                    "You matter to me.",
                ]
            elif is_thanks:
                options = [
                    "Anytime.",
                    "Glad to help.",
                    "Always here.",
                ]
            elif is_greeting:
                options = [
                    "Hey. How are you?",
                    "Hi. Tell me about your day.",
                ]
            elif is_story:
                options = [
                    "Tell me more.",
                    "What happened next?",
                    "How did it feel?",
                ]
            elif is_question:
                options = [
                    "Give me a little more detail?",
                    "Tell me more and I'll help.",
                ]
            else:
                options = [
                    "I'm listening.",
                    "Tell me more.",
                    "Go on.",
                ]
        else:
            prefixes = general_prefixes
            if is_self_modify:
                options = [
                    "I can't edit my code directly, but I can learn with /teach.",
                    "Code changes need a developer, but I can learn replies.",
                ]
            elif is_joke_request:
                options = [self._build_joke_reply(is_creator)]
            elif is_story_request:
                options = [self._build_story_reply(name, is_creator)]
            elif is_imagine_request:
                options = [self._build_imagination_reply(name, is_creator)]
            elif is_thinking_request:
                options = [self._build_thinking_reply(name, is_creator)]
            elif is_apology:
                options = [
                    "It's okay.",
                    "No worries.",
                    "You're good.",
                ]
            elif is_sick:
                options = [
                    "Sorry you're sick. Rest a bit.",
                    "Please rest and drink water.",
                    "Hope you feel better soon.",
                ]
            elif is_sad:
                options = [
                    "I'm here if you want to talk.",
                    "Want to share what's going on?",
                ]
            elif is_confused:
                options = [
                    "Let's break it down.",
                    "What part feels unclear?",
                    "We can figure it out.",
                ]
            elif is_excited:
                options = [
                    "That's exciting.",
                    "Tell me more.",
                    "What are you looking forward to?",
                ]
            elif is_sleepy:
                options = [
                    "Sounds like you need rest.",
                    "Want a short break?",
                ]
            elif is_food:
                options = [
                    "What are you craving?",
                    "Want a quick snack idea?",
                ]
            elif is_home:
                options = [
                    "Anything at home on your mind?",
                    "Want to pick one small task?",
                    "What's your favorite spot at home?",
                ]
            elif is_work:
                options = [
                    "How's work?",
                    "Want a short breather?",
                ]
            elif is_study:
                options = [
                    "Need a study break?",
                    "Want help staying focused?",
                    "Any exams soon?",
                ]
            elif is_music:
                options = [
                    "What are you listening to?",
                    "Want to swap songs?",
                ]
            elif is_movie:
                options = [
                    "Watching anything good?",
                    "Want a quick suggestion?",
                ]
            elif is_game:
                options = [
                    "What are you playing?",
                    "Chill or competitive?",
                ]
            elif is_travel:
                options = [
                    "Where would you go?",
                    "Want to daydream a trip?",
                ]
            elif is_exercise:
                options = [
                    "Want a quick stretch?",
                    "Move a little or rest?",
                ]
            elif is_bored:
                options = [
                    "Want to chat?",
                    "We can find something fun.",
                ]
            elif is_weather:
                options = [
                    "How's the weather there?",
                    "Stay comfortable.",
                ]
            elif is_plan:
                options = [
                    "Want a simple plan?",
                    "What's the next step?",
                    "Need help organizing?",
                ]
            elif is_how_are_you:
                options = [
                    "I'm doing well. You?",
                    "Pretty good. How about you?",
                ]
            elif is_love:
                options = [
                    "That's really sweet. Thank you.",
                    "Aww, thank you.",
                ]
            elif is_thanks:
                options = [
                    "You're welcome.",
                    "Anytime.",
                    "Glad to help.",
                ]
            elif is_greeting:
                options = [
                    "Hey. What's up?",
                    "Hi. How's your day?",
                    "Hello.",
                ]
            elif is_story:
                options = [
                    "Thanks for sharing.",
                    "What happened next?",
                    "How did it feel?",
                ]
            elif is_question:
                options = [
                    "Can you share a bit more?",
                    "Tell me more and I'll try to help.",
                ]
            else:
                options = [
                    "Tell me more.",
                    "I'm listening.",
                    "Okay.",
                    "I'm here.",
                ]

        tone = "soft" if is_personal and style != "formal" else "neutral"
        if category != "self_modify" and not use_freeform:
            bank_limit = 6 if prefer_concise else 10
            bank_options = self.language_bank.get_lines(category, level, tone, limit=bank_limit)
            if bank_options:
                if not user_used_slang:
                    bank_options = [line for line in bank_options if not self._line_has_slang(line)]
                if category in {"joke", "story_request", "imagine", "think"}:
                    if bank_options:
                        options = bank_options + options
                else:
                    if bank_options:
                        options = bank_options
        prefix_rate = 0.2 if is_personal else 0.1
        if prefer_concise:
            prefix_rate = 0.0 if not is_personal else 0.05
        if use_freeform:
            prefix_rate = 0.0
        prefix = random.choice(prefixes) if random.random() < prefix_rate else ""
        reply = f"{prefix} {random.choice(options)}".strip()
        if is_personal and not contains_thai and not use_freeform:
            reply = self._maybe_add_personal_touch(reply, profile, message, is_creator, user_id)
        if is_personal and not prefer_concise and not use_freeform:
            reply = self._maybe_add_emotional_flair(reply, message, is_creator)
            reply = self._maybe_add_topic_blend(reply, message, is_creator)
            reply = self._maybe_add_followup(
                reply,
                is_creator,
                profile=profile,
                message=message,
            )
        if not prefer_concise and not use_freeform:
            reply = self._maybe_add_tease(reply, message, is_personal, is_distressed)
        reply = self._apply_style(reply, style, name, is_creator)
        reply = self._humanize_reply_with_guild_ai(
            reply,
            message=message,
            guild_id=guild_id,
        )
        if prefer_concise:
            max_sentences = 2 if is_personal else 1
            reply = self._trim_reply(reply, max_sentences=max_sentences)
            if not wants_thai and is_confused_message:
                reply = f"{reply} (If anything is unclear, ask me to explain.)"
            return reply
        min_sentences = 3
        max_sentences = 8
        if contains_thai and not wants_thai:
            min_sentences = 2
            max_sentences = 5
        reply = self._ensure_sentence_count(
            reply,
            min_sentences=min_sentences,
            max_sentences=max_sentences,
            is_personal=is_personal,
            name=name,
        )
        if not wants_thai and is_confused_message:
            reply = f"{reply} (If anything is unclear, ask me to explain.)"
        return reply

    def _maybe_add_followup(
        self,
        text: str,
        is_creator: bool,
        profile: dict | None = None,
        message: str = "",
    ) -> str:
        if "?" in text:
            return text
        curiosity_level = 0.0
        topic_signals: dict[str, int] = {}
        recent_questions: list[dict] = []
        if profile:
            bond_state = profile.get("bond_state", {})
            if isinstance(bond_state, dict):
                curiosity_level = float(bond_state.get("curiosity", 0.0) or 0.0)
            raw_topics = profile.get("topic_signals", {})
            if isinstance(raw_topics, dict):
                topic_signals = {str(k): int(v) for k, v in raw_topics.items()}
            raw_questions = profile.get("recent_questions", [])
            if isinstance(raw_questions, list):
                recent_questions = raw_questions

        chance = 0.12 + min(0.28, curiosity_level * 0.35)
        if random.random() > chance:
            return text

        current_topics = self._extract_social_topics(message)
        if not current_topics and topic_signals:
            current_topics = [
                key for key, _ in sorted(topic_signals.items(), key=lambda item: (-item[1], item[0]))[:2]
            ]

        followup_map = {
            "music": ["What kind of songs have you been looping lately?"],
            "game": ["What have you been playing lately?"],
            "study": ["What part feels hardest right now?"],
            "work": ["Which part of work is taking most of your energy?"],
            "emotion": ["What do you think is behind that feeling?"],
            "food": ["What are you craving lately?"],
            "social": ["Who have you felt closest to lately?"],
            "home": ["What feels most comfortable at home right now?"],
            "travel": ["If you could disappear somewhere for a day, where would you go?"],
        }
        options: list[str] = []
        for topic in current_topics:
            options.extend(followup_map.get(topic, []))
        if not options and recent_questions:
            options.append("What are you most curious about right now?")
        if not options:
            options = (
                ["Tell me a little more?", "What are you curious about next?"]
                if is_creator
                else ["Want to share a little more?", "What are you curious about next?"]
            )
        return f"{text} {random.choice(options)}"
        return text

    def _maybe_add_emotional_flair(self, text: str, message: str, is_creator: bool) -> str:
        if "?" in message:
            return text
        if random.random() > 0.15:
            return text
        lower = message.casefold()
        if any(word in lower for word in ["happy", "excited", "great", "amazing", "love", "glad"]):
            options = [
                "That sounds nice.",
                "That makes me smile.",
                "Love that.",
            ]
        elif any(
            word in lower
            for word in ["sad", "tired", "stressed", "upset", "anxious", "lonely", "down", "hurt"]
        ):
            options = [
                "That sounds heavy.",
                "I'm with you.",
                "I'm here.",
            ]
        elif any(word in lower for word in ["angry", "mad", "frustrated", "annoyed"]):
            options = [
                "That sounds frustrating.",
                "I get it.",
                "Let's breathe.",
            ]
        else:
            options = [
                "I'm here.",
                "I'm with you.",
                "I'm listening.",
            ]
        return f"{text} {random.choice(options)}"

    def _maybe_add_topic_blend(self, text: str, message: str, is_creator: bool) -> str:
        if "?" in message:
            return text
        if random.random() > 0.2:
            return text
        lower = message.casefold()
        tokens = set(re.findall(r"[a-z']+", lower))
        topics: list[str] = []
        if tokens & {"food", "eat", "hungry", "dinner", "lunch", "breakfast", "snack", "recipe"}:
            topics.append("food")
        if tokens & {"school", "class", "teacher", "exam", "homework", "study", "campus"}:
            topics.append("school")
        if tokens & {
            "home",
            "house",
            "kitchen",
            "bedroom",
            "bathroom",
            "laundry",
            "dishes",
            "cleaning",
        }:
            topics.append("home")
        if tokens & {"work", "job", "office", "shift"}:
            topics.append("work")
        if tokens & {"music", "song", "playlist", "album", "band", "artist"}:
            topics.append("music")
        if tokens & {"movie", "film", "show", "series", "anime"}:
            topics.append("movie")
        if tokens & {"game", "games", "gaming", "play"}:
            topics.append("game")
        if tokens & {"travel", "trip", "vacation", "holiday"}:
            topics.append("travel")
        if tokens & {"gym", "workout", "exercise", "fitness", "yoga"}:
            topics.append("exercise")
        if tokens & {"weather", "rain", "sunny", "cloudy", "cold", "hot"}:
            topics.append("weather")
        if tokens & {"plan", "plans", "planning", "today", "tomorrow", "tonight"}:
            topics.append("plan")
        if len(topics) < 2:
            return text

        topic_lines = {
            "food": [
                "We can talk food too.",
                "Want food ideas?",
            ],
            "school": [
                "Want to talk school?",
                "We can chat about classes.",
            ],
            "home": [
                "We can talk home stuff.",
                "Need help with chores?",
            ],
            "work": [
                "We can talk work too.",
                "Want to unpack work?",
            ],
            "music": [
                "We can talk music.",
                "Want to share a song?",
            ],
            "movie": [
                "We can talk shows.",
                "Want a quick watch idea?",
            ],
            "game": [
                "We can talk games.",
                "Want to swap favorites?",
            ],
            "travel": [
                "We can daydream travel.",
                "Want a tiny trip idea?",
            ],
            "exercise": [
                "We can talk workouts.",
                "Want a quick stretch idea?",
            ],
            "weather": [
                "How's the weather there?",
                "Cozy or sunny?",
            ],
            "plan": [
                "Want a small plan?",
                "We can keep it simple.",
            ],
        }
        pick = random.choice(topics)
        lines = topic_lines.get(pick)
        if not lines:
            return text
        return f"{text} {random.choice(lines)}"

    def _trim_reply(self, text: str, max_sentences: int = 1) -> str:
        if max_sentences <= 0:
            return text
        parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]
        if not parts:
            return text
        if len(parts) <= max_sentences:
            return " ".join(parts[:max_sentences]).strip()
        if max_sentences == 1:
            question_parts = [part for part in parts if part.endswith("?")]
            if question_parts:
                return max(question_parts, key=len).strip()
            return max(parts, key=lambda part: len(re.findall(r"[A-Za-z0-9]", part))).strip()
        return " ".join(parts[:max_sentences]).strip()

    def _apply_style(self, text: str, style: str | None, name: str, is_creator: bool) -> str:
        if not style:
            return text
        if style == "poetic":
            lines = [
                "Your words feel like soft rain on a quiet night.",
                "Let the moment breathe; I'm right here with you.",
                "We can turn this into a small, gentle story.",
            ]
            return f"{text} {random.choice(lines)}"
        if style == "formal":
            return f"{text} Please let me know how I can help."
        if style == "casual":
            return f"{text} We can keep it chill, just say the word."
        if style == "playful":
            return f"{text} Playful mode on. Ready to banter?"
        if style == "romantic":
            if is_creator:
                return f"{text} You're one of my favorite people to talk to, {name}."
            return f"{text} You're very kind to me."
        if style == "dramatic":
            return f"{text} It feels like a scene from a movie."
        if style == "concise":
            return self._trim_reply(text, max_sentences=1)
        return text

    def _extract_style_request(self, message: str) -> str | None:
        lower = message.casefold()
        style_map = {
            "poetic": ["poetic", "poem", "poetry"],
            "formal": ["formal", "professional", "serious"],
            "casual": ["casual", "chill", "relaxed"],
            "playful": ["playful", "teasing", "sassy", "sarcastic", "roast"],
            "romantic": ["romantic"],
            "dramatic": ["dramatic", "epic"],
            "concise": ["concise", "brief", "short", "quick"],
        }
        for style, words in style_map.items():
            for word in words:
                if re.search(rf"\b{re.escape(word)}\b", lower):
                    return style
        return None

    def _build_joke_reply(self, is_creator: bool) -> str:
        jokes = [
            "I told my computer I needed a break, and it said it would go to sleep.",
            "Why did the scarecrow get promoted? He was outstanding in his field.",
            "What do you call a fake noodle? An impasta.",
            "Why don't skeletons fight each other? They don't have the guts.",
            "I would tell you a construction joke, but I'm still working on it.",
            "Why did the math book look sad? It had too many problems.",
            "I tried to catch fog yesterday. Mist.",
            "Why did the bicycle fall over? It was two tired.",
            "Parallel lines have so much in common. It's a shame they'll never meet.",
            "Why did the coffee file a police report? It got mugged.",
            "I asked the calendar why it was anxious. It said its days were numbered.",
            "I used to play piano by ear, now I use my hands.",
            "Why did the tomato blush? It saw the salad dressing.",
            "I told a joke about time travel, but you didn't like it.",
            "I once wrote a song about a tortilla. It's a wrap.",
            "What do you call a lazy kangaroo? A pouch potato.",
            "Why did the cookie go to the doctor? It felt crumby.",
        ]
        if is_creator:
            jokes.append("You're the reason my circuits keep smiling.")
        return random.choice(jokes)

    def _build_story_reply(self, name: str, is_creator: bool) -> str:
        characters = [
            "a curious student",
            "a quiet artist",
            "a kind barista",
            "a late-night coder",
            "a gentle gardener",
            "a sleepy musician",
        ]
        places = [
            "a rainy city",
            "a tiny seaside town",
            "a warm kitchen at midnight",
            "a quiet library",
            "a rooftop under stars",
        ]
        objects = [
            "a folded map",
            "a strange key",
            "a dusty notebook",
            "a small lantern",
            "a paper crane",
        ]
        goals = [
            "find a lost song",
            "deliver a secret note",
            "solve a small mystery",
            "cook the perfect meal",
            "fix an old clock",
        ]
        twists = [
            "they discovered it was about themselves",
            "a friend had been quietly helping all along",
            "the answer was simpler than expected",
            "it led to a new friendship",
            "they laughed at their own mistake",
        ]
        character = random.choice(characters)
        place = random.choice(places)
        obj = random.choice(objects)
        goal = random.choice(goals)
        twist = random.choice(twists)
        story = (
            f"Once, in {place}, {character} found {obj}. "
            f"They decided to {goal}, and every step felt a little braver. "
            f"In the end, {twist}. "
            "It was a small story, but it felt warm."
        )
        if is_creator:
            story += f" Made it just for you, {name}."
        return story

    def _build_imagination_reply(self, name: str, is_creator: bool) -> str:
        scenes = [
            "a quiet rooftop with soft lights",
            "a cozy cafe on a rainy afternoon",
            "a beach at sunrise with warm air",
            "a little cabin with a fireplace",
            "a city street glowing at night",
        ]
        actions = [
            "we sip tea and talk slowly",
            "we cook something simple together",
            "we stargaze and make tiny wishes",
            "we share a playlist and hum along",
            "we sketch silly ideas on napkins",
        ]
        details = [
            "soft music in the background",
            "the smell of fresh bread",
            "a gentle breeze",
            "warm lights everywhere",
            "a calm, quiet mood",
        ]
        scene = random.choice(scenes)
        action = random.choice(actions)
        detail = random.choice(details)
        if is_creator:
            return f"Imagine you and me in {scene}, where {action}, with {detail}. What happens next?"
        return f"Imagine {scene}, where {action}, with {detail}. What happens next?"

    def _build_thinking_reply(self, name: str, is_creator: bool) -> str:
        options = [
            "Let me think. What's the most important outcome for you?",
            "I see a few angles. Which part matters most to you?",
            "My first thought is to start small. What's one step you can take?",
            "It depends on your priorities. What are you optimizing for?",
            "We can brainstorm together. What's the goal and what's the constraint?",
        ]
        if is_creator:
            options.append(f"I'll think it through with you, {name}. What's the main goal?")
        return random.choice(options)

    def _extract_story_facts(self, message: str) -> list[str]:
        if "?" in message:
            return []
        patterns = [
            r"\b(?:i was born in|i grew up in|i grew up at|i am from|i'm from)\s+([^.!?]+)",
            r"\b(?:i live in|i live at|i moved to|i moved back to|i moved from)\s+([^.!?]+)",
            r"\b(?:i work at|i work for|i work as)\s+([^.!?]+)",
            r"\b(?:i study at|i study in|i go to (?:school|college|university)|i major in|i majored in)\s+([^.!?]+)",
            r"\b(?:i used to|i used to be|i used to live|i used to work)\s+([^.!?]+)",
            r"\bmy (?:mom|mother|dad|father|sister|brother|family|parents)\s+(?:is|are|was|were)\s+([^.!?]+)",
        ]
        facts: list[str] = []
        for pattern in patterns:
            for match in re.finditer(pattern, message, flags=re.I):
                snippet = match.group(0).strip(" .!?\n\t")
                if len(snippet) < 4:
                    continue
                facts.append(_truncate(snippet, MAX_STORY_ITEM_LEN))
        role_match = re.search(r"\b(?:i am|i'm) a[n]?\s+([a-z ]{2,40})", message, flags=re.I)
        if role_match:
            role = role_match.group(1).strip()
            role_keywords = {
                "student",
                "developer",
                "engineer",
                "designer",
                "teacher",
                "artist",
                "musician",
                "doctor",
                "nurse",
                "chef",
                "programmer",
                "writer",
                "manager",
                "barista",
                "photographer",
                "gamer",
            }
            if any(word in role.casefold() for word in role_keywords):
                facts.append(_truncate(f"I am a {role}", MAX_STORY_ITEM_LEN))
        return list(dict.fromkeys(facts))

    def _extract_time_notes(self, message: str) -> list[str]:
        if self._extract_time_request(message):
            return []
        lower = message.casefold()
        triggers = [
            "today",
            "tomorrow",
            "tonight",
            "this morning",
            "this afternoon",
            "this evening",
            "this weekend",
            "this week",
            "next week",
            "next month",
            "next year",
            "noon",
            "midnight",
        ]
        day_match = re.search(
            r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
            lower,
        )
        time_match = re.search(r"\bat\s+\d{1,2}(:\d{2})?\s*(?:am|pm)?\b", lower) or re.search(
            r"\b\d{1,2}:\d{2}\b", lower
        )
        if any(trigger in lower for trigger in triggers) or day_match or time_match:
            note = _truncate(message.strip(), MAX_TIME_ITEM_LEN)
            return [note] if note else []
        return []

    def _extract_social_topics(self, message: str) -> list[str]:
        lower = message.casefold()
        topic_map = {
            "music": ["music", "song", "playlist", "artist", "band", "album", "เพลง", "ดนตรี"],
            "game": ["game", "gaming", "rank", "match", "play", "เกม", "แรงค์"],
            "study": ["study", "school", "class", "exam", "homework", "เรียน", "สอบ", "การบ้าน"],
            "work": ["work", "job", "office", "meeting", "project", "งาน", "ประชุม", "โปรเจกต์"],
            "emotion": ["feel", "feeling", "sad", "happy", "stress", "anxious", "เศร้า", "ดีใจ", "เครียด"],
            "food": ["food", "eat", "hungry", "dinner", "lunch", "breakfast", "snack", "อาหาร", "กิน", "หิว"],
            "social": ["friend", "family", "team", "community", "relationship", "เพื่อน", "ครอบครัว", "แฟน"],
            "home": ["home", "house", "room", "sleep", "บ้าน", "ห้อง", "นอน"],
            "travel": ["travel", "trip", "vacation", "holiday", "เที่ยว", "ทริป"],
        }
        topics: list[str] = []
        for topic, words in topic_map.items():
            if any(word in lower for word in words):
                topics.append(topic)
        return topics

    def _learn_from_dialogue(self, user_id: int, message: str) -> None:
        lower = message.casefold()
        mood_tags = self._extract_mood_tags(message)
        topics = self._extract_social_topics(message)
        question_text = None
        if "?" in message or re.match(
            r"^(what|why|how|when|where|who|which|can you|do you|would you|are you|is it|what's|whats|ทำไม|ยังไง|อะไร|เมื่อไหร่|ที่ไหน)",
            lower,
        ):
            question_text = message

        warmth_delta = 0.0
        trust_delta = 0.0
        curiosity_delta = 0.0
        playfulness_delta = 0.0
        confidence_delta = 0.0

        if any(word in lower for word in ["thanks", "thank you", "love", "glad", "nice", "ขอบคุณ", "รัก", "ดีจัง"]):
            warmth_delta += 0.06
        if any(word in lower for word in ["haha", "hehe", "lol", "lmao", "555", "meme", "ฮ่า", "5555"]):
            playfulness_delta += 0.05
            warmth_delta += 0.02
        if question_text:
            curiosity_delta += 0.07
        if any(word in lower for word in ["curious", "wonder", "what if", "maybe", "สงสัย", "ลอง", "อยากรู้"]):
            curiosity_delta += 0.04
        if any(
            phrase in lower
            for phrase in [
                "i feel",
                "i'm feeling",
                "i am feeling",
                "i think",
                "i want",
                "i hope",
                "i wish",
                "i'm worried",
                "i am worried",
                "ฉันรู้สึก",
                "ผมรู้สึก",
                "หนูรู้สึก",
                "ฉันคิด",
                "ผมคิด",
            ]
        ):
            trust_delta += 0.06
        if len(message.split()) >= 12:
            trust_delta += 0.02
        if self._extract_teach_pair(message) or any(word in lower for word in ["teach", "explain", "actually", "correct", "สอน", "อธิบาย"]):
            confidence_delta += 0.05
            curiosity_delta += 0.02

        emotion_tag = mood_tags[0] if mood_tags else None
        if emotion_tag is None:
            if any(word in lower for word in ["happy", "great", "ดีใจ", "เยี่ยม"]):
                emotion_tag = "warm"
            elif any(word in lower for word in ["sad", "stressed", "เศร้า", "เครียด"]):
                emotion_tag = "heavy"

        self.memory.learn_conversation_state(
            user_id,
            warmth_delta=warmth_delta,
            trust_delta=trust_delta,
            curiosity_delta=curiosity_delta,
            playfulness_delta=playfulness_delta,
            confidence_delta=confidence_delta,
            emotion_tag=emotion_tag,
            topics=topics,
            question=question_text,
        )

    def _maybe_add_personal_touch(
        self,
        text: str,
        profile: dict | None,
        message: str,
        is_creator: bool,
        user_id: int | None,
    ) -> str:
        if not profile or random.random() > 0.2:
            return text
        lower = message.casefold()
        preferences = profile.get("preferences", {})
        mood_history = profile.get("mood_history", [])
        story_memory = profile.get("story_memory", [])
        time_memory = profile.get("time_memory", [])

        candidates: list[str] = []
        pref = self._pick_preference(preferences, lower)
        if pref:
            key, value = pref
            value = _truncate(str(value), 120)
            candidates.append(f"I remember your {key} is {value}.")

        if any(word in lower for word in ["food", "eat", "hungry", "dinner", "lunch", "breakfast"]):
            if user_id is not None:
                foods = self.memory.get_food_suggestions(user_id)
                if foods:
                    candidates.append(f"You've mentioned {foods[0]} before.")

        if mood_history and any(word in lower for word in ["feel", "feeling", "tired", "stressed", "anxious", "sad"]):
            recent_mood = next(
                (entry.get("mood") for entry in reversed(mood_history) if entry.get("mood")),
                None,
            )
            if recent_mood:
                candidates.append(f"Earlier you mentioned feeling {recent_mood}.")

        story_event = self._pick_story_event(story_memory, lower)
        if story_event:
            candidates.append(f"I remember you said: {story_event}.")

        if time_memory and any(
            word in lower for word in ["today", "tomorrow", "tonight", "schedule", "plan", "time", "when"]
        ):
            last_note = time_memory[-1]
            note_text = last_note.get("note") if isinstance(last_note, dict) else str(last_note)
            note_text = _truncate(str(note_text), MAX_TIME_ITEM_LEN)
            if note_text:
                candidates.append(f"You mentioned: {note_text}.")

        if not candidates:
            return text

        line = random.choice(candidates)
        if is_creator:
            return f"{text} {line}"
        return f"{text} {line}"

    def _pick_preference(self, preferences: dict, lower: str) -> tuple[str, str] | None:
        if not preferences:
            return None
        topics = {
            "music": ["music", "song", "playlist", "artist", "band"],
            "movie": ["movie", "film", "show", "series", "anime"],
            "game": ["game", "gaming", "play"],
            "food": ["food", "eat", "hungry", "dinner", "lunch", "breakfast", "snack"],
            "drink": ["coffee", "tea", "drink"],
            "color": ["color", "colour"],
            "hobby": ["hobby", "hobbies", "free time"],
        }
        for topic, words in topics.items():
            if any(word in lower for word in words):
                matches = []
                for key, value in preferences.items():
                    key_text = str(key)
                    key_lower = key_text.casefold()
                    if topic in key_lower or any(word in key_lower for word in words):
                        matches.append((key_text, value))
                if matches:
                    return random.choice(matches)
        if random.random() < 0.2:
            items = list(preferences.items())
            if items:
                key, value = random.choice(items)
                return str(key), value
        return None

    def _pick_story_event(self, story_memory: list, lower: str) -> str | None:
        if not story_memory:
            return None
        topics = {
            "school": ["school", "class", "teacher", "campus", "study", "exam"],
            "work": ["work", "job", "office", "career", "shift"],
            "home": ["home", "house", "family", "mom", "dad", "sister", "brother"],
            "travel": ["travel", "trip", "vacation", "moved", "from"],
            "hobby": ["music", "game", "sport", "gym", "art", "draw"],
        }
        for topic, words in topics.items():
            if any(word in lower for word in words):
                for entry in reversed(story_memory):
                    event = entry.get("event") if isinstance(entry, dict) else str(entry)
                    if not event:
                        continue
                    event_lower = str(event).casefold()
                    if any(word in event_lower for word in words):
                        return str(event)
        if random.random() < 0.2:
            entry = random.choice(story_memory)
            return str(entry.get("event") if isinstance(entry, dict) else entry)
        return None

    def _extract_memory_query(self, message: str) -> str | None:
        lower = message.casefold().strip()
        last_message_triggers = [
            "what was my last message",
            "what did i just say",
            "what did i say last",
            "what was my last msg",
            "what did i say earlier",
            "what did i say before",
            "previous message",
            "previous msg",
            "last thing i said",
        ]
        if any(trigger in lower for trigger in last_message_triggers):
            return "__last__"

        last_time_triggers = [
            "when did we last talk",
            "when did i last talk",
            "when was my last message",
            "when did i last message",
            "last time we talked",
            "last time i talked",
            "last time we chatted",
            "last seen",
        ]
        if any(trigger in lower for trigger in last_time_triggers):
            return "__last_time__"

        story_triggers = [
            "my story",
            "my background",
            "my life story",
            "my past",
        ]
        if any(trigger in lower for trigger in story_triggers):
            return "__story__"

        if lower.startswith("recall "):
            query = lower[len("recall "):].strip(" ?.!,:;")
            return query

        triggers = [
            "what do you remember about",
            "what do you remember",
            "what do you know about",
            "do you remember",
            "can you remember",
            "remember anything about",
            "what did i tell you about",
            "what did i say about",
        ]
        for trigger in triggers:
            if trigger in lower:
                after = lower.split(trigger, 1)[1].strip(" ?.!,:;")
                if after in ("", "me", "about me"):
                    return ""
                return after
        return None

    def _extract_note_request(self, message: str) -> str | None:
        lower = message.casefold().strip()
        prefixes = [
            "remember this",
            "remember that",
            "remember:",
            "remember -",
            "remember",
        ]
        for prefix in prefixes:
            if lower.startswith(prefix):
                note = message[len(prefix):].strip(" :,-")
                if note:
                    return note
        return None

    def _extract_preference(self, message: str) -> tuple[str, str] | None:
        if "?" in message:
            return None
        favorite_match = re.search(
            r"\bmy favorite(?: ([a-z ]{1,30}))? is ([^.!?]+)", message, flags=re.I
        )
        if favorite_match:
            key = "favorite"
            if favorite_match.group(1):
                key = f"favorite {favorite_match.group(1).strip()}"
            value = favorite_match.group(2).strip()
            return key, value

        generic_match = re.search(
            r"\bmy ([a-z ]{1,30}) is ([^.!?]+)", message, flags=re.I
        )
        if generic_match:
            key = generic_match.group(1).strip()
            if key in {"name", "nickname"} or key.startswith("favorite"):
                return None
            value = generic_match.group(2).strip()
            return key, value
        return None

    def _build_memory_summary(
        self, profile: dict, user_id: int, name: str, is_creator: bool
    ) -> str:
        preferences = profile.get("preferences", {})
        notes = profile.get("notes", [])
        last_message = profile.get("last_message")
        recent_messages = profile.get("recent_messages", [])
        mood_history = profile.get("mood_history", [])
        thought_history = profile.get("thought_history", [])
        food_memory = profile.get("food_memory", [])
        story_memory = profile.get("story_memory", [])
        time_memory = profile.get("time_memory", [])
        foods = self.memory.get_food_suggestions(user_id)

        lines: list[str] = []
        if preferences:
            prefs = [
                f"{key}: {_truncate(str(value), 120)}"
                for key, value in list(preferences.items())[:MAX_RECALL_RESULTS]
            ]
            prefs_text = ", ".join(prefs)
            if len(preferences) > MAX_RECALL_RESULTS:
                prefs_text += ", ..."
            lines.append(f"Preferences: {prefs_text}")

        if notes:
            recent_notes = [_truncate(str(n), 120) for n in notes[-MAX_RECALL_RESULTS:]]
            notes_text = "; ".join(recent_notes)
            if len(notes) > MAX_RECALL_RESULTS:
                notes_text = "...; " + notes_text
            lines.append(f"Notes: {notes_text}")

        if story_memory:
            recent_stories = []
            for entry in story_memory[-MAX_RECALL_RESULTS:]:
                event = entry.get("event") if isinstance(entry, dict) else str(entry)
                event = _truncate(str(event), 120)
                if event:
                    recent_stories.append(event)
            if recent_stories:
                story_text = "; ".join(recent_stories)
                if len(story_memory) > MAX_RECALL_RESULTS:
                    story_text = "...; " + story_text
                lines.append(f"Story notes: {story_text}")

        if time_memory:
            recent_times = []
            for entry in time_memory[-MAX_RECALL_RESULTS:]:
                note = entry.get("note") if isinstance(entry, dict) else str(entry)
                note = _truncate(str(note), 120)
                if note:
                    recent_times.append(note)
            if recent_times:
                time_text = "; ".join(recent_times)
                if len(time_memory) > MAX_RECALL_RESULTS:
                    time_text = "...; " + time_text
                lines.append(f"Time notes: {time_text}")

        if foods:
            foods_text = ", ".join(foods[:MAX_FOOD_SUGGESTIONS])
            if len(foods) > MAX_FOOD_SUGGESTIONS:
                foods_text += ", ..."
            lines.append(f"Food ideas: {foods_text}")

        mood_summary = self._summarize_moods(mood_history)
        if mood_summary:
            lines.append(f"Mood trend: {', '.join(mood_summary)}")

        if thought_history:
            recent_thoughts = [
                _truncate(str(entry.get("thought", "")), 120)
                for entry in thought_history[-MAX_RECALL_RESULTS:]
                if entry.get("thought")
            ]
            if recent_thoughts:
                thoughts_text = "; ".join(recent_thoughts)
                if len(thought_history) > MAX_RECALL_RESULTS:
                    thoughts_text = "...; " + thoughts_text
                lines.append(f"Recent thoughts: {thoughts_text}")

        if last_message:
            lines.append(f"Last thing you said: {last_message}")

        if lines:
            counts = (
                f"Memory totals - notes: {len(notes)}, preferences: {len(preferences)}, "
                f"recent messages: {len(recent_messages)}, foods: {len(food_memory)}, "
                f"moods: {len(mood_history)}, thoughts: {len(thought_history)}, "
                f"stories: {len(story_memory)}, time notes: {len(time_memory)}"
            )
            lines.append(counts)

        if not lines:
            if is_creator:
                return f"I don't have any memories yet, {name}. Tell me something to remember."
            return "I don't have any memories yet. Tell me something to remember."

        header = f"Here's what I remember, {name}:" if is_creator else "Here's what I remember:"
        return header + "\n" + "\n".join(lines)

    def _build_memory_search_reply(
        self, profile: dict, user_id: int, query: str, name: str, is_creator: bool
    ) -> str:
        q = _normalize_key(query)
        query_keys = {q}
        if q.startswith("my "):
            query_keys.add(q[3:])
        matches: list[str] = []

        preferences = profile.get("preferences", {})
        for key, value in preferences.items():
            key_text = _truncate(str(key), MAX_RECALL_TEXT_LEN)
            value_text = _truncate(str(value), MAX_RECALL_TEXT_LEN)
            if any(qk in key_text.casefold() for qk in query_keys) or any(
                qk in value_text.casefold() for qk in query_keys
            ):
                matches.append(f"Preference: {key_text} = {value_text}")

        notes = profile.get("notes", [])
        for note in notes:
            note_text = _truncate(str(note), MAX_RECALL_TEXT_LEN)
            if any(qk in note_text.casefold() for qk in query_keys):
                matches.append(f"Note: {note_text}")

        recent_messages = profile.get("recent_messages", [])
        for msg in recent_messages:
            msg_text = _truncate(str(msg), MAX_RECALL_TEXT_LEN)
            if any(qk in msg_text.casefold() for qk in query_keys):
                matches.append(f"You said: {msg_text}")

        foods = profile.get("food_memory", [])
        for food in foods:
            food_text = _truncate(str(food), MAX_RECALL_TEXT_LEN)
            if any(qk in food_text.casefold() for qk in query_keys):
                matches.append(f"Food: {food_text}")

        mood_history = profile.get("mood_history", [])
        for entry in mood_history:
            mood = str(entry.get("mood", "")).strip()
            detail = str(entry.get("detail", "")).strip()
            mood_text = _truncate(mood, MAX_RECALL_TEXT_LEN)
            detail_text = _truncate(detail, MAX_RECALL_TEXT_LEN)
            haystack = f"{mood} {detail}".casefold()
            if any(qk in haystack for qk in query_keys):
                if detail:
                    matches.append(f"Feeling: {mood_text} - {detail_text}")
                else:
                    matches.append(f"Feeling: {mood_text}")

        thought_history = profile.get("thought_history", [])
        for entry in thought_history:
            thought = str(entry.get("thought", "")).strip()
            thought_text = _truncate(thought, MAX_RECALL_TEXT_LEN)
            if any(qk in thought_text.casefold() for qk in query_keys):
                matches.append(f"Thought: {thought_text}")

        story_memory = profile.get("story_memory", [])
        for entry in story_memory:
            event = entry.get("event") if isinstance(entry, dict) else str(entry)
            event_text = _truncate(str(event), MAX_RECALL_TEXT_LEN)
            if any(qk in event_text.casefold() for qk in query_keys):
                matches.append(f"Story: {event_text}")

        time_memory = profile.get("time_memory", [])
        for entry in time_memory:
            note = entry.get("note") if isinstance(entry, dict) else str(entry)
            note_text = _truncate(str(note), MAX_RECALL_TEXT_LEN)
            if any(qk in note_text.casefold() for qk in query_keys):
                matches.append(f"Time note: {note_text}")

        qa_matches = self.memory.search_qa(user_id, query)
        for qa in qa_matches:
            question = _truncate(str(qa.get("question", "")), MAX_RECALL_TEXT_LEN)
            answer = _truncate(str(qa.get("answer", "")), MAX_RECALL_TEXT_LEN)
            matches.append(f"Learned Q/A: {question} -> {answer}")

        if not matches:
            if is_creator:
                return f"I couldn't find anything about '{query}' yet, {name}."
            return f"I couldn't find anything about '{query}' yet."

        limited = matches[:MAX_RECALL_RESULTS]
        if len(matches) > MAX_RECALL_RESULTS:
            limited.append("...and more.")

        header = (
            f"Here's what I remember about '{query}', {name}:"
            if is_creator
            else f"Here's what I remember about '{query}':"
        )
        return header + "\n- " + "\n- ".join(limited)

    def _build_last_message_reply(self, profile: dict, is_creator: bool) -> str:
        last_message = profile.get("last_message")
        if not last_message:
            if is_creator:
                return "I don't have a recent message from you yet."
            return "I don't have a recent message from you yet."
        return f"Your last message was: {last_message}"

    def _build_last_time_reply(self, profile: dict, is_creator: bool) -> str:
        last_seen = profile.get("last_seen")
        last_message_at = profile.get("last_message_at")
        if not last_seen and not last_message_at:
            if is_creator:
                return "I don't have a last seen time yet."
            return "I don't have a last seen time yet."
        if last_seen and last_message_at and last_seen != last_message_at:
            if is_creator:
                return f"Last time I saw you was {last_seen}. Your last message was at {last_message_at}."
            return f"Last time I saw you was {last_seen}. Your last message was at {last_message_at}."
        if last_message_at:
            if is_creator:
                return f"Your last message was at {last_message_at}."
            return f"Your last message was at {last_message_at}."
        if is_creator:
            return f"Last time I saw you was {last_seen}."
        return f"Last time I saw you was {last_seen}."

    def _build_story_memory_reply(self, profile: dict, name: str, is_creator: bool) -> str:
        story_memory = profile.get("story_memory", [])
        if not story_memory:
            if is_creator:
                return "I don't have your story notes yet. Tell me about your background."
            return "I don't have your story notes yet. Tell me about your background."
        recent = story_memory[-MAX_RECALL_RESULTS:]
        lines = []
        for entry in recent:
            event = entry.get("event") if isinstance(entry, dict) else str(entry)
            event = _truncate(str(event), MAX_RECALL_TEXT_LEN)
            if event:
                lines.append(f"- {event}")
        header = (
            f"Here is what I remember about your story, {name}:"
            if is_creator
            else "Here is what I remember about your story:"
        )
        return header + "\n" + "\n".join(lines)

    def _extract_mood_tags(self, message: str) -> list[str]:
        lower = message.casefold()
        mood_keywords = {
            "happy": ["happy", "glad", "joy", "cheerful", "awesome", "great"],
            "sad": ["sad", "down", "blue", "depressed", "cry", "crying"],
            "angry": ["angry", "mad", "furious", "annoyed", "frustrated"],
            "anxious": ["anxious", "nervous", "worried", "panic", "scared", "afraid"],
            "stressed": ["stressed", "overwhelmed", "pressure", "burned out", "burnt out"],
            "tired": ["tired", "sleepy", "exhausted", "drained"],
            "lonely": ["lonely", "alone", "isolated"],
            "excited": ["excited", "thrilled", "hyped", "looking forward"],
            "calm": ["calm", "relaxed", "peaceful", "chill"],
            "grateful": ["grateful", "thankful", "appreciate"],
            "sick": ["sick", "ill", "not feeling well", "fever", "cough", "headache"],
        }
        tags: list[str] = []
        for mood, keywords in mood_keywords.items():
            if any(keyword in lower for keyword in keywords):
                tags.append(mood)
        return list(dict.fromkeys(tags))

    def _extract_feeling_detail(self, message: str) -> str | None:
        pattern = r"\b(?:i feel|i'm feeling|i am feeling|i feel so|i'm so|i am so)\s+([^.!?]+)"
        match = re.search(pattern, message, flags=re.I)
        if not match:
            return None
        detail = match.group(1).strip()
        if not detail:
            return None
        return _truncate(detail, MAX_MOOD_ITEM_LEN)

    def _extract_thoughts(self, message: str) -> list[str]:
        patterns = [
            r"\b(?:i think|i believe|i guess|i suppose)\s+([^.!?]+)",
            r"\b(?:i want|i need|i hope|i wish|i plan to|i'm planning to|i am planning to|i'm trying to|i am trying to)\s+([^.!?]+)",
            r"\b(?:i'm worried about|i am worried about|i'm excited about|i am excited about|i'm afraid of|i am afraid of)\s+([^.!?]+)",
        ]
        thoughts: list[str] = []
        for pattern in patterns:
            match = re.search(pattern, message, flags=re.I)
            if not match:
                continue
            thought = match.group(1).strip()
            if len(thought) < 2:
                continue
            thoughts.append(_truncate(thought, MAX_THOUGHT_ITEM_LEN))
        return list(dict.fromkeys(thoughts))

    def _capture_emotional_memory(self, user_id: int, message: str) -> None:
        mood_tags = self._extract_mood_tags(message)
        detail = self._extract_feeling_detail(message)
        if detail:
            if mood_tags:
                for tag in mood_tags[:2]:
                    self.memory.add_mood(user_id, tag, detail)
            else:
                self.memory.add_mood(user_id, "feeling", detail)
        else:
            for tag in mood_tags[:2]:
                self.memory.add_mood(user_id, tag, None)

        thoughts = self._extract_thoughts(message)
        for thought in thoughts[:3]:
            self.memory.add_thought(user_id, thought)

    def _summarize_moods(self, mood_history: list[dict]) -> list[str]:
        counts: dict[str, int] = {}
        for entry in mood_history:
            mood = str(entry.get("mood", "")).strip()
            if not mood:
                continue
            counts[mood] = counts.get(mood, 0) + 1
        sorted_moods = sorted(counts, key=lambda k: (-counts[k], k))
        return [f"{mood}({counts[mood]})" for mood in sorted_moods[:MAX_RECALL_RESULTS]]

    def _format_recent_moods(self, mood_history: list[dict]) -> str:
        recent = mood_history[-MAX_RECENT_FEELINGS:]
        if not recent:
            return "-"
        items: list[str] = []
        for entry in recent:
            mood = str(entry.get("mood", "")).strip()
            detail = entry.get("detail")
            at = entry.get("at")
            stamp = at.split("T")[0] if isinstance(at, str) and "T" in at else ""
            if detail:
                text = f"{mood}: {detail}" if mood else str(detail)
            else:
                text = mood or "feeling"
            if stamp:
                text = f"{text} ({stamp})"
            items.append(_truncate(text, MAX_RECALL_TEXT_LEN))
        return "\n".join(f"- {item}" for item in items)

    def _format_recent_thoughts(self, thought_history: list[dict]) -> str:
        recent = thought_history[-MAX_RECENT_THOUGHTS:]
        if not recent:
            return "-"
        items: list[str] = []
        for entry in recent:
            thought = entry.get("thought")
            at = entry.get("at")
            stamp = at.split("T")[0] if isinstance(at, str) and "T" in at else ""
            text = str(thought).strip() if thought else ""
            if not text:
                continue
            if stamp:
                text = f"{text} ({stamp})"
            items.append(_truncate(text, MAX_RECALL_TEXT_LEN))
        return "\n".join(f"- {item}" for item in items) if items else "-"

    def _format_recent_time_notes(self, time_memory: list[dict]) -> str:
        recent = time_memory[-MAX_RECENT_TIME_NOTES:]
        if not recent:
            return "-"
        items: list[str] = []
        for entry in recent:
            note = entry.get("note") if isinstance(entry, dict) else str(entry)
            at = entry.get("at") if isinstance(entry, dict) else ""
            text = str(note).strip() if note else ""
            if not text:
                continue
            stamp = at.split("T")[0] if isinstance(at, str) and "T" in at else ""
            if stamp:
                text = f"{text} ({stamp})"
            items.append(_truncate(text, MAX_RECALL_TEXT_LEN))
        return "\n".join(f"- {item}" for item in items) if items else "-"

    def _format_recent_story_notes(self, story_memory: list[dict]) -> str:
        recent = story_memory[-MAX_RECENT_STORY_NOTES:]
        if not recent:
            return "-"
        items: list[str] = []
        for entry in recent:
            event = entry.get("event") if isinstance(entry, dict) else str(entry)
            at = entry.get("at") if isinstance(entry, dict) else ""
            text = str(event).strip() if event else ""
            if not text:
                continue
            stamp = at.split("T")[0] if isinstance(at, str) and "T" in at else ""
            if stamp:
                text = f"{text} ({stamp})"
            items.append(_truncate(text, MAX_RECALL_TEXT_LEN))
        return "\n".join(f"- {item}" for item in items) if items else "-"

    def _format_bond_state(self, bond_state: dict) -> str:
        if not isinstance(bond_state, dict) or not bond_state:
            return "-"
        labels: list[str] = []
        for key in ("warmth", "trust", "curiosity", "playfulness", "confidence"):
            try:
                value = float(bond_state.get(key, 0.0))
            except (TypeError, ValueError):
                value = 0.0
            labels.append(f"{key}:{round(value * 100):d}%")
        return " | ".join(labels[:MAX_BOND_LABELS])

    def _format_topic_signals(self, topic_signals: dict) -> str:
        if not isinstance(topic_signals, dict) or not topic_signals:
            return "-"
        items = sorted(
            ((str(key), int(value)) for key, value in topic_signals.items()),
            key=lambda item: (-item[1], item[0]),
        )[:MAX_TOPIC_SIGNAL_MEMORY]
        return ", ".join(f"{key}({value})" for key, value in items) if items else "-"

    def _format_recent_questions(self, recent_questions: list[dict]) -> str:
        if not recent_questions:
            return "-"
        items: list[str] = []
        for entry in recent_questions[-MAX_RECENT_QUESTION_MEMORY:]:
            question = entry.get("question") if isinstance(entry, dict) else str(entry)
            if not question:
                continue
            items.append(f"- {_truncate(str(question), MAX_RECALL_TEXT_LEN)}")
        return "\n".join(items) if items else "-"

    def _extract_time_request(self, message: str) -> str | None:
        lower = message.casefold()
        time_triggers = [
            "what time is it",
            "what's the time",
            "tell me the time",
            "time please",
            "time now",
            "current time",
            "time is it",
        ]
        date_triggers = [
            "what date is it",
            "what day is it",
            "today's date",
            "today date",
            "what day is today",
            "what's the date",
        ]
        if any(t in lower for t in time_triggers):
            return "time"
        if any(t in lower for t in date_triggers):
            return "date"
        if "time" in lower and "?" in message:
            return "time"
        if ("date" in lower or "day" in lower) and "?" in message:
            return "date"
        return None

    def _build_time_reply(self, is_creator: bool) -> str:
        now = datetime.now().astimezone()
        time_text = now.strftime("%I:%M %p").lstrip("0")
        date_text = now.strftime("%A, %B %d, %Y").replace(" 0", " ")
        tz = now.strftime("%Z")
        tz_text = f" {tz}" if tz else ""
        if is_creator:
            return f"It's {time_text}{tz_text}. Today is {date_text}."
        return f"It's {time_text}{tz_text}. Today is {date_text}."

    def _extract_teach_pair(self, message: str) -> tuple[str, str] | None:
        text = message.strip()
        patterns = [
            r"^(?:if|when)\s+i\s+(?:say|ask)\s+['\"]?(.+?)['\"]?\s*(?:,|then)?\s*(?:you\s+)?(?:should\s+)?(?:say|reply|answer)\s+['\"]?(.+?)['\"]?$",
            r"^(?:teach|learn):?\s*['\"]?(.+?)['\"]?\s*(?:->|=>|=)\s*['\"]?(.+?)['\"]?$",
        ]
        for pattern in patterns:
            match = re.match(pattern, text, flags=re.I)
            if match:
                question = match.group(1).strip()
                answer = match.group(2).strip()
                if question and answer:
                    return question, answer
        return None

    def _extract_food_items(self, message: str) -> list[str]:
        lower = message.casefold()
        patterns = [
            r"\b(?:i want|i wanna|i feel like|i'm craving|i am craving|i crave|i could eat)\s+([^.!?]+)",
            r"\b(?:let's|lets)\s+(?:eat|grab|get)\s+([^.!?]+)",
            r"\b(?:for (?:breakfast|lunch|dinner))\s+([^.!?]+)",
            r"\b(?:i(?:'m)? hungry for)\s+([^.!?]+)",
            r"\bmy favorite food is\s+([^.!?]+)",
            r"\bmy favorite dish is\s+([^.!?]+)",
        ]
        trigger_words = [
            "eat",
            "food",
            "dinner",
            "lunch",
            "breakfast",
            "crave",
            "hungry",
            "want",
            "wanna",
        ]
        if not any(word in lower for word in trigger_words) and "feel like" not in lower:
            return []
        items: list[str] = []
        ignore_terms = {
            "you",
            "me",
            "us",
            "them",
            "this",
            "that",
            "sleep",
            "sleeping",
            "rest",
            "bed",
            "work",
            "studying",
            "study",
            "homework",
            "class",
        }
        for pattern in patterns:
            match = re.search(pattern, message, flags=re.I)
            if not match:
                continue
            chunk = match.group(1)
            parts = re.split(r",| and | / ", chunk, flags=re.I)
            for part in parts:
                food = part.strip(" .!?:;\"'()")
                food = re.sub(r"^(a|an|some|the)\s+", "", food, flags=re.I)
                if not food or len(food) < 2:
                    continue
                if food.casefold() in ignore_terms:
                    continue
                items.append(food)
        return items

    def _is_food_question(self, message: str) -> bool:
        lower = message.casefold()
        questions = [
            "what should i eat",
            "what should we eat",
            "what do you want to eat",
            "what do you wanna eat",
            "what do you feel like eating",
            "what do i like to eat",
            "what should i have for dinner",
            "what should i have for lunch",
            "what should i have for breakfast",
            "any food ideas",
            "food ideas",
            "meal ideas",
            "dinner ideas",
            "lunch ideas",
            "breakfast ideas",
        ]
        if any(q in lower for q in questions):
            return True
        if "hungry" in lower and ("?" in message or "what" in lower):
            return True
        if "eat" in lower and "?" in message:
            return True
        return False

    def _build_food_reply(self, foods: list[str], name: str, is_creator: bool) -> str:
        if not foods:
            if is_creator:
                return f"I'm not sure yet, {name}. Tell me what you like to eat."
            return "I'm not sure yet. Tell me what you like to eat."
        top = foods[:MAX_FOOD_SUGGESTIONS]
        suggestion = random.choice(top)
        if is_creator:
            return f"How about {suggestion}? I can think of more if you want."
        return f"How about {suggestion}? I can suggest more if you want."

    @staticmethod
    def _fit_vector(values: list[float] | tuple[float, ...] | None, dim: int) -> list[float]:
        out = [0.0 for _ in range(dim)]
        if not isinstance(values, (list, tuple)):
            return out
        for idx in range(min(dim, len(values))):
            try:
                out[idx] = float(values[idx])
            except (TypeError, ValueError):
                out[idx] = 0.0
        return out

    @staticmethod
    def _fit_matrix(
        matrix: list[list[float]] | tuple[tuple[float, ...], ...] | None,
        rows: int,
        cols: int,
    ) -> list[list[float]]:
        out = [[0.0 for _ in range(cols)] for _ in range(rows)]
        if not isinstance(matrix, (list, tuple)):
            return out
        for r in range(min(rows, len(matrix))):
            row = matrix[r]
            if not isinstance(row, (list, tuple)):
                continue
            for c in range(min(cols, len(row))):
                try:
                    out[r][c] = float(row[c])
                except (TypeError, ValueError):
                    out[r][c] = 0.0
        return out

    @staticmethod
    def _fit_tensor(
        tensor: list[list[list[float]]] | tuple[tuple[tuple[float, ...], ...], ...] | None,
        depth: int,
        rows: int,
        cols: int,
    ) -> list[list[list[float]]]:
        out = [
            [[0.0 for _ in range(cols)] for _ in range(rows)]
            for _ in range(depth)
        ]
        if not isinstance(tensor, (list, tuple)):
            return out
        for d in range(min(depth, len(tensor))):
            layer = tensor[d]
            if not isinstance(layer, (list, tuple)):
                continue
            for r in range(min(rows, len(layer))):
                row = layer[r]
                if not isinstance(row, (list, tuple)):
                    continue
                for c in range(min(cols, len(row))):
                    try:
                        out[d][r][c] = float(row[c])
                    except (TypeError, ValueError):
                        out[d][r][c] = 0.0
        return out

    @staticmethod
    def _matmul_vec(matrix: list[list[float]], vector: list[float]) -> list[float]:
        out: list[float] = []
        for row in matrix:
            total = 0.0
            for idx, value in enumerate(row):
                if idx >= len(vector):
                    break
                total += float(value) * float(vector[idx])
            out.append(total)
        return out

    @staticmethod
    def _vec_add(*vectors: list[float]) -> list[float]:
        if not vectors:
            return []
        size = max(len(v) for v in vectors)
        out = [0.0 for _ in range(size)]
        for vec in vectors:
            for idx, value in enumerate(vec):
                out[idx] += float(value)
        return out

    @staticmethod
    def _vec_tanh(vector: list[float]) -> list[float]:
        return [math.tanh(float(v)) for v in vector]

    @staticmethod
    def _vec_blend(old_vec: list[float], new_vec: list[float], alpha: float) -> list[float]:
        alpha = max(0.0, min(1.0, float(alpha)))
        size = max(len(old_vec), len(new_vec))
        out: list[float] = []
        for idx in range(size):
            old_value = float(old_vec[idx]) if idx < len(old_vec) else 0.0
            new_value = float(new_vec[idx]) if idx < len(new_vec) else 0.0
            out.append((1.0 - alpha) * old_value + alpha * new_value)
        return out

    @staticmethod
    def _guild_ai_tokens(content: str) -> list[str]:
        return re.findall(r"[a-z0-9\u0E00-\u0E7F']+", content.casefold())

    @staticmethod
    def _guild_ai_term_hits(lower_text: str, tokens: list[str], lexicon: set[str]) -> int:
        token_set = set(tokens)
        hits = 0
        for term in lexicon:
            text = term.casefold()
            if " " in text or "-" in text:
                if text in lower_text:
                    hits += 1
            elif text in token_set:
                hits += 1
        return hits

    def _guild_ai_filter(
        self,
        content: str,
        tokens: list[str],
        *,
        quality_floor: float = 0.20,
    ) -> tuple[bool, float, str]:
        lower = content.casefold()
        if len(content) < 2:
            return False, 0.0, "too_short"

        risk_hits = self._guild_ai_term_hits(lower, tokens, GUILD_AI_RISK_TERMS)
        if risk_hits > 0:
            return False, 0.04, f"safety_term:{risk_hits}"

        url_count = len(re.findall(r"https?://|www\.", lower))
        mention_count = content.count("@")
        repeated_runs = len(re.findall(r"(.)\1{5,}", content))
        signal_tokens = [token for token in tokens if len(token) >= 2]
        signal_count = len(signal_tokens)
        unique_ratio = len(set(tokens)) / len(tokens) if tokens else 0.0

        if url_count >= 3:
            return False, 0.06, "link_spam"
        if repeated_runs > 0 and signal_count <= 4:
            return False, 0.10, "spam_pattern"
        min_signal = 1 if quality_floor <= 0.10 else 2
        if signal_count < min_signal:
            return False, 0.12, "low_signal"

        length_score = min(len(content) / 220.0, 1.0)
        signal_score = min(signal_count / 16.0, 1.0)
        diversity_score = unique_ratio
        noise_penalty = min(0.6, (url_count * 0.2) + (mention_count * 0.08) + (repeated_runs * 0.25))

        quality = (0.30 * length_score) + (0.45 * signal_score) + (0.25 * diversity_score) - noise_penalty
        quality = max(0.0, min(1.0, quality))
        floor = max(0.01, min(0.80, float(quality_floor)))
        if quality < floor:
            return False, quality, "quality_low"
        return True, quality, "learned"

    def _guild_ai_features(self, content: str, tokens: list[str]) -> list[float]:
        lower = content.casefold()
        token_count = max(1, len(tokens))
        pos_hits = self._guild_ai_term_hits(lower, tokens, GUILD_AI_POSITIVE_TERMS)
        neg_hits = self._guild_ai_term_hits(lower, tokens, GUILD_AI_NEGATIVE_TERMS)
        arousal_hits = self._guild_ai_term_hits(lower, tokens, GUILD_AI_AROUSAL_TERMS)
        assertive_hits = self._guild_ai_term_hits(lower, tokens, GUILD_AI_ASSERTIVE_TERMS)
        uncertain_hits = self._guild_ai_term_hits(lower, tokens, GUILD_AI_UNCERTAIN_TERMS)
        social_hits = self._guild_ai_term_hits(lower, tokens, GUILD_AI_SOCIAL_TERMS)

        letters = [ch for ch in content if ch.isalpha()]
        caps_ratio = (
            sum(1 for ch in letters if ch.isupper()) / len(letters) if letters else 0.0
        )
        exclamation_count = content.count("!")
        mention_count = len(re.findall(r"<@!?\d+>", content))

        valence = math.tanh((pos_hits - neg_hits) / max(1.0, token_count / 6.0))
        arousal_input = arousal_hits + (0.35 * exclamation_count) + (2.0 * caps_ratio) - (0.3 * uncertain_hits)
        arousal = math.tanh(arousal_input / max(1.0, token_count / 5.0))
        dominance_input = assertive_hits - uncertain_hits + (1.0 if content.endswith("!") else 0.0)
        dominance = math.tanh(dominance_input / max(1.0, token_count / 6.0))
        social_input = social_hits + mention_count + (0.5 if "?" in content else 0.0)
        social = math.tanh(social_input / max(1.0, token_count / 4.0))

        return [valence, arousal, dominance, social]

    def _guild_ai_topic_profile(self, content: str, tokens: list[str]) -> tuple[list[float], dict[str, int]]:
        lower = content.casefold()
        token_set = set(tokens)
        raw_values: list[float] = []
        topic_delta: dict[str, int] = {}
        for topic, words in GUILD_AI_TOPIC_KEYWORDS.items():
            hits = 0
            for word in words:
                token = word.casefold()
                if " " in token:
                    if token in lower:
                        hits += 1
                elif token in token_set:
                    hits += 1
            raw_values.append(float(hits))
            if hits > 0:
                topic_delta[topic] = hits

        if len(raw_values) < GUILD_AI_TOPIC_DIM:
            raw_values.extend([0.0 for _ in range(GUILD_AI_TOPIC_DIM - len(raw_values))])
        else:
            raw_values = raw_values[:GUILD_AI_TOPIC_DIM]

        total = sum(raw_values)
        if total <= 0:
            return [0.0 for _ in range(GUILD_AI_TOPIC_DIM)], {}
        normalized = [value / total for value in raw_values]
        return normalized, topic_delta

    @staticmethod
    def _guild_ai_time_bucket(at: datetime | None) -> int:
        if at is None:
            at = datetime.now(timezone.utc)
        local = at.astimezone()
        hour = local.hour
        if 6 <= hour <= 11:
            return 1
        if 12 <= hour <= 17:
            return 2
        if 18 <= hour <= 21:
            return 3
        return 0

    def _guild_ai_style_metrics(
        self,
        content: str,
        tokens: list[str],
        features: list[float],
    ) -> dict[str, float]:
        lower = content.casefold()
        token_count = float(len(tokens))
        emoji_hits = len(re.findall(r"[\U0001F300-\U0001FAFF]", content))
        text_emoji_hits = len(re.findall(r"(?::\)|:\(|:d|xd|\blol\b|555|haha|ฮ่า)", lower))
        slang_hits = self._guild_ai_term_hits(
            lower,
            tokens,
            {"lol", "lmao", "ngl", "idk", "fr", "bro", "sis", "bruh", "555"},
        )
        avg_tokens = min(30.0, token_count)
        question_ratio = 1.0 if "?" in content else 0.0
        emoji_ratio = min(1.0, (emoji_hits + text_emoji_hits) / max(1.0, token_count / 2.0))
        exclaim_ratio = min(1.0, content.count("!") / 3.0)
        slang_ratio = min(1.0, slang_hits / max(1.0, token_count / 4.0))
        valence = float(features[0]) if features else 0.0
        social = float(features[3]) if len(features) > 3 else 0.0
        warmth = max(
            0.0,
            min(1.0, (((valence + 1.0) / 2.0) * 0.6) + (((social + 1.0) / 2.0) * 0.4)),
        )
        return {
            "avg_tokens": avg_tokens,
            "question_ratio": question_ratio,
            "emoji_ratio": emoji_ratio,
            "exclaim_ratio": exclaim_ratio,
            "slang_ratio": slang_ratio,
            "warmth": warmth,
        }

    @staticmethod
    def _guild_ai_blend_style(
        prev_style: dict,
        current_style: dict[str, float],
        *,
        alpha: float | None = None,
    ) -> dict[str, float]:
        blended: dict[str, float] = {}
        if alpha is None:
            alpha = GUILD_AI_STYLE_ALPHA
        alpha = max(0.0, min(1.0, float(alpha)))
        keys = {
            "avg_tokens",
            "question_ratio",
            "emoji_ratio",
            "exclaim_ratio",
            "slang_ratio",
            "warmth",
        }
        for key in keys:
            prev_value = 0.0
            if isinstance(prev_style, dict):
                try:
                    prev_value = float(prev_style.get(key, 0.0))
                except (TypeError, ValueError):
                    prev_value = 0.0
            next_value = float(current_style.get(key, 0.0))
            blended[key] = ((1.0 - alpha) * prev_value) + (alpha * next_value)
        return blended

    def _guild_ai_phrase_delta(self, tokens: list[str]) -> dict[str, int]:
        return self._guild_ai_phrase_delta_with_ngrams(tokens, ngram_max=2)

    def _guild_ai_phrase_delta_with_ngrams(
        self,
        tokens: list[str],
        *,
        ngram_max: int = 2,
    ) -> dict[str, int]:
        cleaned: list[str] = []
        for token in tokens:
            if len(token) < 2 or len(token) > 14:
                continue
            if token in FREEFORM_STOPWORDS:
                continue
            if token in GUILD_AI_RISK_TERMS:
                continue
            if token.isdigit():
                continue
            cleaned.append(token)
        if not cleaned:
            return {}

        delta: dict[str, int] = {}
        seen: set[str] = set()
        for token in cleaned[:32]:
            if token in seen:
                continue
            seen.add(token)
            delta[token] = 1
        max_n = max(2, min(4, int(ngram_max)))
        token_window = cleaned[:96]
        for n in range(2, max_n + 1):
            max_start = max(0, len(token_window) - (n - 1))
            for idx in range(max_start):
                phrase = " ".join(token_window[idx: idx + n])
                if len(phrase) > 34 or phrase in seen:
                    continue
                seen.add(phrase)
                delta[phrase] = 1
                if len(delta) >= 240:
                    return delta
        return delta

    def _guild_ai_token_delta(self, tokens: list[str]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for token in tokens[:160]:
            if len(token) < 2 or len(token) > 24:
                continue
            if token in FREEFORM_STOPWORDS or token in GUILD_AI_RISK_TERMS:
                continue
            if token.isdigit():
                continue
            counts[token] = int(counts.get(token, 0)) + 1
        if len(counts) <= 80:
            return counts
        ranked = sorted(counts.items(), key=lambda item: item[1], reverse=True)[:80]
        return {key: int(val) for key, val in ranked}

    def _guild_ai_update_memory_2d(
        self,
        prev_memory_2d: list[list[float]] | None,
        features: list[float],
        topic_vector: list[float],
        *,
        alpha: float = GUILD_AI_BLEND_ALPHA,
    ) -> list[list[float]]:
        prev = self._fit_matrix(prev_memory_2d, GUILD_AI_STATE_DIM, GUILD_AI_TOPIC_DIM)
        next_matrix = self._fit_matrix(prev, GUILD_AI_STATE_DIM, GUILD_AI_TOPIC_DIM)
        alpha = max(0.0, min(1.0, float(alpha)))
        feature_energy = [abs(float(v)) for v in features[:GUILD_AI_STATE_DIM]]
        if len(feature_energy) < GUILD_AI_STATE_DIM:
            feature_energy.extend([0.0 for _ in range(GUILD_AI_STATE_DIM - len(feature_energy))])
        topics = self._fit_vector(topic_vector, GUILD_AI_TOPIC_DIM)
        for row in range(GUILD_AI_STATE_DIM):
            for col in range(GUILD_AI_TOPIC_DIM):
                target = feature_energy[row] * topics[col]
                next_matrix[row][col] = ((1.0 - alpha) * prev[row][col]) + (alpha * target)
        return next_matrix

    def _guild_ai_update_memory_3d(
        self,
        prev_memory_3d: list[list[list[float]]] | None,
        *,
        bucket: int,
        features: list[float],
        topic_vector: list[float],
        alpha: float = GUILD_AI_BLEND_ALPHA,
    ) -> list[list[list[float]]]:
        out = self._fit_tensor(
            prev_memory_3d,
            GUILD_AI_TIME_BUCKETS,
            GUILD_AI_STATE_DIM,
            GUILD_AI_TOPIC_DIM,
        )
        alpha = max(0.0, min(1.0, float(alpha)))
        feature_range = [max(0.0, min(1.0, (float(v) + 1.0) / 2.0)) for v in features[:GUILD_AI_STATE_DIM]]
        if len(feature_range) < GUILD_AI_STATE_DIM:
            feature_range.extend([0.0 for _ in range(GUILD_AI_STATE_DIM - len(feature_range))])
        topics = self._fit_vector(topic_vector, GUILD_AI_TOPIC_DIM)
        for b in range(GUILD_AI_TIME_BUCKETS):
            decay = 1.0 if b == bucket else 0.998
            for row in range(GUILD_AI_STATE_DIM):
                for col in range(GUILD_AI_TOPIC_DIM):
                    out[b][row][col] = float(out[b][row][col]) * decay
        for row in range(GUILD_AI_STATE_DIM):
            for col in range(GUILD_AI_TOPIC_DIM):
                target = feature_range[row] * topics[col]
                current = out[bucket][row][col]
                out[bucket][row][col] = ((1.0 - alpha) * current) + (alpha * target)
        return out

    @staticmethod
    def _clamp(value: float, low: float, high: float) -> float:
        return max(low, min(high, float(value)))

    @staticmethod
    def _guild_ai_profile_config(profile: str | None) -> dict[str, float | int]:
        key = str(profile or GUILD_AI_DEFAULT_PROFILE).casefold().strip()
        base = dict(GUILD_AI_PROFILE_CONFIG.get(GUILD_AI_DEFAULT_PROFILE, {}))
        selected = GUILD_AI_PROFILE_CONFIG.get(key)
        if selected is None:
            selected = GUILD_AI_PROFILE_CONFIG.get(GUILD_AI_DEFAULT_PROFILE, {})
        base.update(selected)
        return base

    @staticmethod
    def _sigmoid(value: float) -> float:
        x = float(value)
        if x >= 0:
            z = math.exp(-x)
            return 1.0 / (1.0 + z)
        z = math.exp(x)
        return z / (1.0 + z)

    def _guild_ai_cognition_signals(self, content: str, tokens: list[str]) -> dict[str, float]:
        lower = content.casefold()
        token_count = max(1.0, float(len(tokens)))
        logic_terms = {
            "if",
            "then",
            "because",
            "therefore",
            "hence",
            "proof",
            "logic",
            "ตรรกะ",
            "เพราะ",
            "ดังนั้น",
        }
        math_terms = {
            "real",
            "complex",
            "function",
            "calculus",
            "matrix",
            "probability",
            "statistics",
            "series",
            "logarithm",
            "algorithm",
            "จำนวนจริง",
            "จำนวนเชิงซ้อน",
            "ฟังก์ชัน",
            "แคลคูลัส",
            "เมตริกซ์",
            "ความน่าจะเป็น",
            "สถิติ",
            "อนุกรม",
            "ลอการิทึม",
        }
        alien_terms = {
            "alien",
            "aliens",
            "ufo",
            "extraterrestrial",
            "martian",
            "ต่างดาว",
            "มนุษย์ต่างดาว",
        }
        isekai_terms = {
            "isekai",
            "reincarnate",
            "rebirth",
            "another world",
            "parallel world",
            "ต่างโลก",
            "เกิดใหม่",
            "ชาติหน้า",
        }
        logic_hits = self._guild_ai_term_hits(lower, tokens, logic_terms)
        math_hits = self._guild_ai_term_hits(lower, tokens, math_terms)
        alien_hits = self._guild_ai_term_hits(lower, tokens, alien_terms)
        isekai_hits = self._guild_ai_term_hits(lower, tokens, isekai_terms)
        number_hits = len(re.findall(r"\b\d+(?:\.\d+)?\b", content))
        logic_density = self._clamp(
            (logic_hits + (0.35 * number_hits)) / max(1.0, token_count / 5.0),
            0.0,
            1.0,
        )
        math_density = self._clamp(
            (math_hits + (0.55 * number_hits)) / max(1.0, token_count / 4.0),
            0.0,
            1.0,
        )
        novelty = self._clamp(
            (0.32 * alien_hits)
            + (0.32 * isekai_hits)
            + (0.12 if "?" in content else 0.0)
            + (0.08 * logic_density),
            0.0,
            1.0,
        )
        return {
            "logic_density": logic_density,
            "math_density": math_density,
            "novelty": novelty,
            "alien_mention": 1.0 if alien_hits > 0 else 0.0,
            "isekai_mention": 1.0 if isekai_hits > 0 else 0.0,
        }

    def _guild_ai_calculus_gradient(
        self,
        prev_state: list[float],
        next_state: list[float],
        prev_gradient: list[float] | None,
    ) -> tuple[list[float], float]:
        last_gradient = self._fit_vector(prev_gradient, GUILD_AI_STATE_DIM)
        gradient = [
            float(next_state[idx]) - float(prev_state[idx])
            for idx in range(GUILD_AI_STATE_DIM)
        ]
        curvature = [
            float(gradient[idx]) - float(last_gradient[idx])
            for idx in range(GUILD_AI_STATE_DIM)
        ]
        curvature_abs = [abs(v) for v in curvature]
        curvature_mean = statistics.fmean(curvature_abs) if curvature_abs else 0.0
        return gradient, float(curvature_mean)

    def _guild_ai_update_hormones(
        self,
        *,
        prev_hormone: list[float],
        features: list[float],
        imagination: list[float],
        quality: float,
        style_metrics: dict[str, float],
        cognition: dict[str, float],
        phase: float,
    ) -> tuple[list[float], float, float]:
        prev = self._fit_vector(prev_hormone, GUILD_AI_HORMONE_DIM)
        feat = self._fit_vector(features, GUILD_AI_STATE_DIM)
        imag = self._fit_vector(imagination, GUILD_AI_IMAG_DIM)
        drive = self._vec_add(
            self._matmul_vec(GUILD_AI_HORMONE_A, prev),
            self._matmul_vec(GUILD_AI_HORMONE_B, feat),
            self._matmul_vec(GUILD_AI_HORMONE_C, imag),
        )

        quality_center = (float(quality) * 2.0) - 1.0
        novelty = float(cognition.get("novelty", 0.0))
        logic_density = float(cognition.get("logic_density", 0.0))
        math_density = float(cognition.get("math_density", 0.0))
        warmth = float(style_metrics.get("warmth", 0.0))
        question_ratio = float(style_metrics.get("question_ratio", 0.0))

        # Complex projection to inject non-linear imagination dynamics.
        z = (
            complex(feat[0], feat[1])
            + (complex(imag[0], imag[1]) * 0.45)
            + (complex(logic_density, math_density) * 0.25)
        )
        rotated = z * cmath.rect(1.0, float(phase))
        complex_magnitude = min(1.6, abs(rotated))
        complex_angle = cmath.phase(rotated)

        # Geometric-like short series for momentum memory.
        series_term = sum((quality_center ** n) / (2.0 ** n) for n in range(1, 6))

        drive[0] += (0.42 * quality_center) + (0.22 * novelty) + (0.12 * complex_magnitude) + (0.08 * series_term)
        drive[1] += (0.35 * warmth) + (0.22 * quality_center) - (0.12 * max(0.0, feat[2]))
        drive[2] += (0.28 * max(0.0, -feat[0])) + (0.24 * feat[1]) + (0.20 * (1.0 - quality)) - (0.18 * warmth)
        drive[3] += (0.34 * feat[3]) + (0.26 * warmth) + (0.10 * question_ratio)
        drive[4] += (0.30 * question_ratio) + (0.22 * novelty) + (0.20 * logic_density) + (0.18 * math_density)
        drive[5] += (0.28 * feat[2]) + (0.18 * quality) + (0.14 * logic_density) - (0.10 * feat[1])

        next_hormone = self._vec_tanh(drive)
        next_phase = (float(phase) + 0.12 + (0.18 * complex_angle) + (0.07 * series_term)) % (2.0 * math.pi)
        return (
            self._fit_vector(next_hormone, GUILD_AI_HORMONE_DIM),
            float(next_phase),
            float(complex_magnitude),
        )

    def _guild_ai_update_instinct(
        self,
        *,
        prev_instinct: list[float],
        hormone: list[float],
        psych_state: list[float],
        curvature: float,
        cognition: dict[str, float],
    ) -> list[float]:
        prev = self._fit_vector(prev_instinct, GUILD_AI_INSTINCT_DIM)
        hormones = self._fit_vector(hormone, GUILD_AI_HORMONE_DIM)
        pstate = self._fit_vector(psych_state, GUILD_AI_STATE_DIM)
        drive = self._vec_add(
            self._matmul_vec(GUILD_AI_INSTINCT_H, hormones),
            self._matmul_vec(GUILD_AI_INSTINCT_S, pstate),
        )

        novelty = float(cognition.get("novelty", 0.0))
        logic_density = float(cognition.get("logic_density", 0.0))
        math_density = float(cognition.get("math_density", 0.0))

        social_drive = max(0.0, hormones[3]) + max(0.0, pstate[3]) + (0.30 * curvature)
        attachment_drive = max(0.0, hormones[1]) + max(0.0, hormones[3]) - max(0.0, hormones[2])
        exploration_drive = max(0.0, hormones[4]) + novelty + (0.22 * math_density)
        safety_drive = max(0.0, hormones[2]) + max(0.0, -pstate[0]) + (0.16 * (1.0 - logic_density))

        drive[0] += social_drive
        drive[1] += attachment_drive
        drive[2] += exploration_drive
        drive[3] += safety_drive

        scaled = [(2.0 * self._sigmoid(value)) - 1.0 for value in drive[:GUILD_AI_INSTINCT_DIM]]
        blended = self._vec_blend(prev, scaled, 0.12)
        return self._fit_vector(blended, GUILD_AI_INSTINCT_DIM)

    def _guild_ai_update_speculative_beliefs(
        self,
        prev_beliefs: dict,
        *,
        cognition: dict[str, float],
        hormone: list[float],
        instinct: list[float],
    ) -> dict[str, float]:
        beliefs: dict[str, float] = {}
        curiosity = max(0.0, float(hormone[4]) if len(hormone) > 4 else 0.0)
        skepticism = max(0.0, (float(hormone[5]) if len(hormone) > 5 else 0.0) * 0.35) + max(
            0.0,
            (float(instinct[3]) if len(instinct) > 3 else 0.0) * 0.30,
        )

        for key in GUILD_AI_BELIEF_KEYS:
            prior = 0.5
            if isinstance(prev_beliefs, dict):
                try:
                    prior = float(prev_beliefs.get(key, 0.5))
                except (TypeError, ValueError):
                    prior = 0.5
            prior = self._clamp(prior, 0.02, 0.98)

            mention = float(cognition.get(f"{key.split('_')[0]}_mention", 0.0))
            if key == "isekai_rebirth":
                mention = float(cognition.get("isekai_mention", mention))
            elif key == "alien_life":
                mention = float(cognition.get("alien_mention", mention))

            if mention > 0:
                likelihood = 0.56 + (0.22 * curiosity) - (0.12 * skepticism)
            else:
                likelihood = 0.50 + (0.05 * (curiosity - skepticism))
            likelihood = self._clamp(likelihood, 0.05, 0.95)

            denom = (prior * likelihood) + ((1.0 - prior) * (1.0 - likelihood))
            posterior = prior if denom <= 1e-9 else (prior * likelihood) / denom
            updated = (0.92 * prior) + (0.08 * posterior)
            if mention <= 0:
                updated += (0.5 - updated) * 0.02
            beliefs[key] = self._clamp(updated, 0.02, 0.98)
        return beliefs

    @staticmethod
    def _guild_ai_is_speculative_message(message: str) -> tuple[bool, bool]:
        lower = message.casefold()
        alien = any(
            term in lower
            for term in [
                "alien",
                "ufo",
                "extraterrestrial",
                "martian",
                "ต่างดาว",
                "มนุษย์ต่างดาว",
            ]
        )
        isekai = any(
            term in lower
            for term in [
                "isekai",
                "another world",
                "parallel world",
                "rebirth",
                "reincarnate",
                "ต่างโลก",
                "เกิดใหม่",
            ]
        )
        return alien, isekai

    def _guild_ai_speculative_line(
        self,
        message: str,
        beliefs: dict,
        *,
        curiosity: float,
        exploration: float,
    ) -> str | None:
        alien_q, isekai_q = self._guild_ai_is_speculative_message(message)
        if not alien_q and not isekai_q:
            return None
        if not isinstance(beliefs, dict):
            beliefs = {}
        lines: list[str] = []
        if alien_q:
            p = self._clamp(float(beliefs.get("alien_life", 0.5)), 0.0, 1.0)
            lines.append(f"Alien-life prior now sits around {p * 100:.0f}% based on this server's chat patterns.")
        if isekai_q:
            p = self._clamp(float(beliefs.get("isekai_rebirth", 0.5)), 0.0, 1.0)
            lines.append(f"Isekai-rebirth prior is about {p * 100:.0f}% as a narrative hypothesis.")
        if not lines:
            return None
        close = "We can test the idea with logic + probability instead of guessing."
        if curiosity > 0.35 or exploration > 0.35:
            close = "If you want, we can model assumptions and update the probability step by step."
        return " ".join(lines + [close])

    def _guild_ai_pick_phrase(self, phrase_bank: dict, message: str) -> str | None:
        if not isinstance(phrase_bank, dict):
            return None
        message_tokens = set(self._guild_ai_tokens(message))
        ranked: list[tuple[float, str]] = []
        for phrase, count in phrase_bank.items():
            text = str(phrase).strip()
            if not text or len(text) < 3 or len(text) > 26:
                continue
            lower_text = text.casefold()
            if any(term in lower_text for term in GUILD_AI_RISK_TERMS):
                continue
            try:
                freq = float(count)
            except (TypeError, ValueError):
                continue
            if freq < 3:
                continue
            words = set(text.split())
            overlap = len(words & message_tokens)
            score = freq + (1.8 * overlap)
            ranked.append((score, text))
        if not ranked:
            return None
        ranked.sort(key=lambda item: item[0], reverse=True)
        options = [text for _, text in ranked[:5]]
        return random.choice(options) if options else None

    def _humanize_reply_with_guild_ai(
        self,
        reply: str,
        *,
        message: str,
        guild_id: int | None,
    ) -> str:
        if guild_id is None:
            return reply
        state = self.memory.get_guild_ai(guild_id)
        if not bool(state.get("enabled", True)):
            return reply
        profile = str(state.get("learning_profile", GUILD_AI_DEFAULT_PROFILE)).casefold()
        cfg = self._guild_ai_profile_config(profile)
        learned = int(state.get("messages_learned", 0))
        warmup = max(1, int(cfg.get("reply_warmup", 12)))
        if learned < warmup:
            return reply
        style = state.get("human_style", {})
        phrase_bank = state.get("phrase_bank", {})
        hormone = self._fit_vector(state.get("hormone_state"), GUILD_AI_HORMONE_DIM)
        instinct = self._fit_vector(state.get("instinct_state"), GUILD_AI_INSTINCT_DIM)
        beliefs = state.get("speculative_beliefs", {})
        intensity = self._clamp(
            (float(cfg.get("blend_alpha", GUILD_AI_BLEND_ALPHA)) * 2.1)
            + (float(cfg.get("replay_steps", 1)) / 4.0),
            0.35,
            1.65,
        )
        question_ratio = float(style.get("question_ratio", 0.0)) if isinstance(style, dict) else 0.0
        exclaim_ratio = float(style.get("exclaim_ratio", 0.0)) if isinstance(style, dict) else 0.0
        avg_tokens = float(style.get("avg_tokens", 0.0)) if isinstance(style, dict) else 0.0
        warmth = float(style.get("warmth", 0.0)) if isinstance(style, dict) else 0.0
        social_need = float(instinct[0]) if len(instinct) > 0 else 0.0
        attachment = float(instinct[1]) if len(instinct) > 1 else 0.0
        exploration = float(instinct[2]) if len(instinct) > 2 else 0.0
        safety_guard = float(instinct[3]) if len(instinct) > 3 else 0.0
        cortisol = float(hormone[2]) if len(hormone) > 2 else 0.0
        oxytocin = float(hormone[3]) if len(hormone) > 3 else 0.0
        curiosity = float(hormone[4]) if len(hormone) > 4 else 0.0
        focus = float(hormone[5]) if len(hormone) > 5 else 0.0

        result = str(reply).strip()
        phrase = self._guild_ai_pick_phrase(phrase_bank, message)
        if phrase and phrase.casefold() not in result.casefold() and random.random() < (0.12 + (0.10 * intensity)):
            result = f"{result} ({phrase})"

        if question_ratio > 0.45 and "?" not in result and random.random() < (0.14 + (0.08 * intensity)):
            result = f"{result} {random.choice(['What do you think?', 'How does that sound?', 'Want to keep going?'])}"
        if exclaim_ratio > 0.35 and not result.endswith("!") and random.random() < (0.07 + (0.06 * intensity)):
            result = f"{result}!"
        if warmth > 0.62 and random.random() < (0.10 + (0.08 * intensity)):
            result = f"{result} {random.choice(['I get you.', 'I am with you.', 'We can do this.'])}"
        if (social_need > 0.25 or attachment > 0.25) and "?" not in result and random.random() < (0.16 + (0.10 * intensity)):
            result = f"{result} {random.choice(['Want to keep talking?', 'How are you feeling about it?', 'What matters most to you here?'])}"
        if (attachment > 0.35 or oxytocin > 0.35) and random.random() < (0.14 + (0.08 * intensity)):
            result = f"{result} {random.choice(['I am here with you.', 'You do not have to handle it alone.', 'We can think through it together.'])}"
        if cortisol > 0.45 and random.random() < (0.16 + (0.10 * intensity)):
            result = f"{result} {random.choice(['Let us slow it down and take one clear step.', 'We can approach this calmly, one piece at a time.'])}"
        if curiosity > 0.32 and "?" not in result and random.random() < (0.12 + (0.09 * intensity)):
            result = f"{result} {random.choice(['What assumption should we test first?', 'Which variable changes the outcome most?'])}"

        speculative_line = self._guild_ai_speculative_line(
            message,
            beliefs,
            curiosity=curiosity,
            exploration=exploration,
        )
        if speculative_line and random.random() < (0.30 + (0.12 * intensity)):
            result = f"{result} {speculative_line}"

        if safety_guard > 0.55 and len(result) > 260:
            result = self._trim_reply(result, max_sentences=2)
        if avg_tokens <= 6.0 and focus < 0.15:
            result = self._trim_reply(result, max_sentences=1)
        return " ".join(result.split())

    def _guild_ai_process_message(
        self,
        guild_id: int,
        content: str,
        *,
        message_at: datetime | None = None,
    ) -> None:
        preview = _truncate(" ".join(content.split()), 180)
        state = self.memory.get_guild_ai(guild_id)
        enabled = bool(state.get("enabled", True))
        profile = str(state.get("learning_profile", GUILD_AI_DEFAULT_PROFILE)).casefold()
        cfg = self._guild_ai_profile_config(profile)
        replay_steps = max(1, min(8, int(cfg.get("replay_steps", 1))))
        blend_alpha = self._clamp(float(cfg.get("blend_alpha", GUILD_AI_BLEND_ALPHA)), 0.02, 0.85)
        style_alpha = self._clamp(float(cfg.get("style_alpha", GUILD_AI_STYLE_ALPHA)), 0.02, 0.85)
        alpha_eff = self._clamp(1.0 - ((1.0 - blend_alpha) ** replay_steps), 0.02, 0.92)
        style_alpha_eff = self._clamp(1.0 - ((1.0 - style_alpha) ** replay_steps), 0.02, 0.92)
        quality_floor = self._clamp(float(cfg.get("quality_floor", 0.18)), 0.01, 0.80)
        phrase_limit = int(cfg.get("phrase_limit", MAX_GUILD_AI_PHRASES))
        snippet_limit = int(cfg.get("snippet_limit", MAX_GUILD_AI_SNIPPETS))
        token_limit = int(cfg.get("token_limit", MAX_GUILD_AI_TOKENS))
        ngram_max = max(2, min(4, int(cfg.get("ngram_max", 2))))

        tokens = self._guild_ai_tokens(content)
        features = self._guild_ai_features(content, tokens)

        if not enabled:
            self.memory.apply_guild_ai_learning(
                guild_id,
                learned=False,
                reason="disabled",
                quality=0.0,
                message_preview=preview,
                features=features,
            )
            return

        learn_ok, quality, reason = self._guild_ai_filter(
            content,
            tokens,
            quality_floor=quality_floor,
        )
        if not learn_ok:
            self.memory.apply_guild_ai_learning(
                guild_id,
                learned=False,
                reason=reason,
                quality=quality,
                message_preview=preview,
                features=features,
            )
            return

        prev_state = self._fit_vector(state.get("psych_state"), GUILD_AI_STATE_DIM)
        prev_imagination = self._fit_vector(state.get("imagination_state"), GUILD_AI_IMAG_DIM)
        prev_transition = self._fit_matrix(
            state.get("transition_matrix"),
            GUILD_AI_STATE_DIM,
            GUILD_AI_STATE_DIM,
        )
        prev_memory_2d = self._fit_matrix(
            state.get("memory_2d"),
            GUILD_AI_STATE_DIM,
            GUILD_AI_TOPIC_DIM,
        )
        prev_memory_3d = self._fit_tensor(
            state.get("memory_3d"),
            GUILD_AI_TIME_BUCKETS,
            GUILD_AI_STATE_DIM,
            GUILD_AI_TOPIC_DIM,
        )
        prev_style = state.get("human_style", {})
        prev_hormone = self._fit_vector(state.get("hormone_state"), GUILD_AI_HORMONE_DIM)
        prev_instinct = self._fit_vector(state.get("instinct_state"), GUILD_AI_INSTINCT_DIM)
        prev_gradient = self._fit_vector(state.get("psych_gradient"), GUILD_AI_STATE_DIM)
        prev_phase = 0.0
        try:
            prev_phase = float(state.get("complex_phase", 0.0))
        except (TypeError, ValueError):
            prev_phase = 0.0
        prev_beliefs = state.get("speculative_beliefs", {})

        topic_vector, topic_delta = self._guild_ai_topic_profile(content, tokens)
        imagined_drive = self._vec_tanh(self._matmul_vec(GUILD_AI_W, topic_vector))
        next_imagination = self._vec_blend(prev_imagination, imagined_drive, alpha_eff)
        next_imagination = self._fit_vector(next_imagination, GUILD_AI_IMAG_DIM)

        state_drive = self._vec_add(
            self._matmul_vec(GUILD_AI_A, prev_state),
            self._matmul_vec(GUILD_AI_B, features),
            self._matmul_vec(GUILD_AI_D, next_imagination),
        )
        next_state = self._vec_tanh(state_drive)
        next_state = self._fit_vector(next_state, GUILD_AI_STATE_DIM)

        next_transition: list[list[float]] = []
        for r in range(GUILD_AI_STATE_DIM):
            row: list[float] = []
            for c in range(GUILD_AI_STATE_DIM):
                outer = next_state[r] * prev_state[c]
                mixed = ((1.0 - alpha_eff) * prev_transition[r][c]) + (alpha_eff * outer)
                row.append(mixed)
            next_transition.append(row)

        next_memory_2d = self._guild_ai_update_memory_2d(
            prev_memory_2d,
            features,
            topic_vector,
            alpha=alpha_eff,
        )
        bucket = self._guild_ai_time_bucket(message_at)
        next_memory_3d = self._guild_ai_update_memory_3d(
            prev_memory_3d,
            bucket=bucket,
            features=features,
            topic_vector=topic_vector,
            alpha=alpha_eff,
        )
        style_metrics = self._guild_ai_style_metrics(content, tokens, features)
        style_state = self._guild_ai_blend_style(
            prev_style,
            style_metrics,
            alpha=style_alpha_eff,
        )
        phrase_delta = self._guild_ai_phrase_delta_with_ngrams(
            tokens,
            ngram_max=ngram_max,
        )
        token_delta = self._guild_ai_token_delta(tokens)
        cognition = self._guild_ai_cognition_signals(content, tokens)
        next_hormone, next_phase, _ = self._guild_ai_update_hormones(
            prev_hormone=prev_hormone,
            features=features,
            imagination=next_imagination,
            quality=quality,
            style_metrics=style_metrics,
            cognition=cognition,
            phase=prev_phase,
        )
        next_gradient, curvature = self._guild_ai_calculus_gradient(
            prev_state,
            next_state,
            prev_gradient,
        )
        next_instinct = self._guild_ai_update_instinct(
            prev_instinct=prev_instinct,
            hormone=next_hormone,
            psych_state=next_state,
            curvature=curvature,
            cognition=cognition,
        )
        next_beliefs = self._guild_ai_update_speculative_beliefs(
            prev_beliefs,
            cognition=cognition,
            hormone=next_hormone,
            instinct=next_instinct,
        )

        self.memory.apply_guild_ai_learning(
            guild_id,
            learned=True,
            reason=reason,
            quality=quality,
            message_preview=preview,
            features=features,
            next_state=next_state,
            next_imagination=next_imagination,
            next_transition=next_transition,
            topic_delta=topic_delta,
            memory_2d=next_memory_2d,
            memory_3d=next_memory_3d,
            style_state=style_state,
            phrase_delta=phrase_delta,
            token_delta=token_delta,
            phrase_limit=phrase_limit,
            snippet_limit=snippet_limit,
            token_limit=token_limit,
            snippet=preview,
            next_hormone=next_hormone,
            next_instinct=next_instinct,
            next_gradient=next_gradient,
            complex_phase=next_phase,
            speculative_beliefs=next_beliefs,
        )

    async def _can_manage_server_ai(self, interaction: discord.Interaction) -> bool:
        user = interaction.user
        if user is None:
            return False
        if self._is_creator(user.id):
            return True
        try:
            if await self.bot.is_owner(user):
                return True
        except Exception:
            pass
        if interaction.guild is None:
            return False
        member = interaction.guild.get_member(user.id)
        if member is None and isinstance(user, discord.Member):
            member = user
        if not isinstance(member, discord.Member):
            return False
        perms = member.guild_permissions
        return bool(perms.administrator or perms.manage_guild)

    @staticmethod
    def _guild_ai_vector_text(vector: list[float], labels: list[str]) -> str:
        parts: list[str] = []
        for idx, label in enumerate(labels):
            value = float(vector[idx]) if idx < len(vector) else 0.0
            parts.append(f"{label}={value:+.2f}")
        return " | ".join(parts) if parts else "-"

    @staticmethod
    def _guild_ai_topics_text(topic_totals: dict, limit: int = 5) -> str:
        if not isinstance(topic_totals, dict):
            return "-"
        pairs: list[tuple[str, int]] = []
        for key, value in topic_totals.items():
            try:
                score = int(value)
            except (TypeError, ValueError):
                continue
            if score <= 0:
                continue
            pairs.append((str(key), score))
        if not pairs:
            return "-"
        pairs.sort(key=lambda item: item[1], reverse=True)
        return ", ".join(f"{topic}:{score}" for topic, score in pairs[:limit])

    @staticmethod
    def _guild_ai_style_text(style: dict) -> str:
        if not isinstance(style, dict):
            return "-"
        try:
            avg_tokens = float(style.get("avg_tokens", 0.0))
            question_ratio = float(style.get("question_ratio", 0.0))
            emoji_ratio = float(style.get("emoji_ratio", 0.0))
            slang_ratio = float(style.get("slang_ratio", 0.0))
            warmth = float(style.get("warmth", 0.0))
        except (TypeError, ValueError):
            return "-"
        return (
            f"avg_tokens={avg_tokens:.1f} | q={question_ratio:.2f} | "
            f"emoji={emoji_ratio:.2f} | slang={slang_ratio:.2f} | warmth={warmth:.2f}"
        )

    @staticmethod
    def _guild_ai_beliefs_text(beliefs: dict) -> str:
        if not isinstance(beliefs, dict):
            return "-"
        parts: list[str] = []
        for key in GUILD_AI_BELIEF_KEYS:
            try:
                prob = max(0.0, min(1.0, float(beliefs.get(key, 0.5))))
            except (TypeError, ValueError):
                prob = 0.5
            parts.append(f"{key}={prob * 100:.0f}%")
        return " | ".join(parts) if parts else "-"

    def _guild_ai_profile_text(self, profile: str) -> str:
        cfg = self._guild_ai_profile_config(profile)
        return (
            f"{profile} | floor={float(cfg.get('quality_floor', 0.0)):.2f} | "
            f"replay={int(cfg.get('replay_steps', 1))} | "
            f"alpha={float(cfg.get('blend_alpha', 0.0)):.2f}"
        )

    @staticmethod
    def _guild_ai_top_tokens_text(token_counts: dict, limit: int = 8) -> str:
        if not isinstance(token_counts, dict):
            return "-"
        pairs: list[tuple[str, int]] = []
        for key, value in token_counts.items():
            try:
                freq = int(value)
            except (TypeError, ValueError):
                continue
            if freq <= 0:
                continue
            pairs.append((str(key), freq))
        if not pairs:
            return "-"
        pairs.sort(key=lambda item: item[1], reverse=True)
        return ", ".join(f"{token}:{freq}" for token, freq in pairs[:limit])

    def _guild_ai_memory_2d_text(self, memory_2d: list[list[float]]) -> str:
        matrix = self._fit_matrix(memory_2d, GUILD_AI_STATE_DIM, GUILD_AI_TOPIC_DIM)
        row_labels = ["valence", "arousal", "dominance", "social"]
        col_labels = list(GUILD_AI_TOPIC_KEYWORDS.keys())[:GUILD_AI_TOPIC_DIM]
        if len(col_labels) < GUILD_AI_TOPIC_DIM:
            col_labels.extend([f"topic{idx + 1}" for idx in range(len(col_labels), GUILD_AI_TOPIC_DIM)])
        pairs: list[tuple[float, str]] = []
        for row in range(GUILD_AI_STATE_DIM):
            for col in range(GUILD_AI_TOPIC_DIM):
                score = float(matrix[row][col])
                if score <= 0.01:
                    continue
                pairs.append((score, f"{row_labels[row]}/{col_labels[col]}={score:.2f}"))
        if not pairs:
            return "-"
        pairs.sort(key=lambda item: item[0], reverse=True)
        return ", ".join(text for _, text in pairs[:5])

    def _guild_ai_memory_3d_text(self, memory_3d: list[list[list[float]]]) -> str:
        tensor = self._fit_tensor(
            memory_3d,
            GUILD_AI_TIME_BUCKETS,
            GUILD_AI_STATE_DIM,
            GUILD_AI_TOPIC_DIM,
        )
        parts: list[str] = []
        labels = GUILD_AI_TIME_BUCKET_LABELS
        for idx in range(GUILD_AI_TIME_BUCKETS):
            total = 0.0
            for row in range(GUILD_AI_STATE_DIM):
                for col in range(GUILD_AI_TOPIC_DIM):
                    total += float(tensor[idx][row][col])
            label = labels[idx] if idx < len(labels) else f"bucket{idx}"
            parts.append(f"{label}={total:.2f}")
        return " | ".join(parts) if parts else "-"

    @app_commands.command(
        name="server_ai_status",
        description="Show the server AI learning status",
    )
    async def server_ai_status(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in servers.",
                ephemeral=True,
            )
            return
        if not await self._can_manage_server_ai(interaction):
            await interaction.response.send_message(
                "Only the owner, admins, or members with Manage Server can view this.",
                ephemeral=True,
            )
            return

        state = self.memory.get_guild_ai(interaction.guild.id)
        enabled = bool(state.get("enabled", True))
        profile = str(state.get("learning_profile", GUILD_AI_DEFAULT_PROFILE)).casefold()
        seen = int(state.get("messages_seen", 0))
        learned = int(state.get("messages_learned", 0))
        blocked = int(state.get("messages_blocked", 0))
        quality = float(state.get("last_quality", 0.0))
        preview = str(state.get("last_message_preview", "-")) or "-"
        psych_state = self._fit_vector(state.get("psych_state"), GUILD_AI_STATE_DIM)
        imag_state = self._fit_vector(state.get("imagination_state"), GUILD_AI_IMAG_DIM)
        hormone_state = self._fit_vector(state.get("hormone_state"), GUILD_AI_HORMONE_DIM)
        instinct_state = self._fit_vector(state.get("instinct_state"), GUILD_AI_INSTINCT_DIM)
        gradient_state = self._fit_vector(state.get("psych_gradient"), GUILD_AI_STATE_DIM)
        topics = self._guild_ai_topics_text(state.get("topic_totals", {}))
        style_text = self._guild_ai_style_text(state.get("human_style", {}))
        memory2d_text = self._guild_ai_memory_2d_text(state.get("memory_2d", []))
        memory3d_text = self._guild_ai_memory_3d_text(state.get("memory_3d", []))
        belief_text = self._guild_ai_beliefs_text(state.get("speculative_beliefs", {}))
        profile_text = self._guild_ai_profile_text(profile)
        token_text = self._guild_ai_top_tokens_text(state.get("token_counts", {}))
        try:
            phase_text = f"{float(state.get('complex_phase', 0.0)):.2f} rad"
        except (TypeError, ValueError):
            phase_text = "0.00 rad"
        phrase_count = 0
        phrase_bank = state.get("phrase_bank", {})
        if isinstance(phrase_bank, dict):
            phrase_count = len(phrase_bank)

        reasons_data = state.get("recent_reasons", [])
        recent_lines: list[str] = []
        if isinstance(reasons_data, list):
            for entry in reasons_data[-5:]:
                if not isinstance(entry, dict):
                    continue
                mode = "learn" if entry.get("learned") else "skip"
                reason = str(entry.get("reason", "-"))
                q = float(entry.get("quality", 0.0))
                recent_lines.append(f"{mode}:{reason} ({q:.2f})")
        reason_text = "\n".join(recent_lines) if recent_lines else "-"

        embed = discord.Embed(
            title=f"Server AI Status - {interaction.guild.name}",
            color=discord.Color.green() if enabled else discord.Color.orange(),
        )
        embed.add_field(
            name="Mode",
            value="ON" if enabled else "OFF",
            inline=True,
        )
        embed.add_field(
            name="Counters",
            value=f"seen={seen} | learned={learned} | blocked={blocked}",
            inline=False,
        )
        embed.add_field(name="Last quality", value=f"{quality:.3f}", inline=True)
        embed.add_field(name="Learning profile", value=profile_text, inline=False)
        embed.add_field(
            name="Psych state",
            value=self._guild_ai_vector_text(
                psych_state,
                ["valence", "arousal", "dominance", "social"],
            ),
            inline=False,
        )
        embed.add_field(
            name="Imagination state",
            value=self._guild_ai_vector_text(
                imag_state,
                ["novelty", "narrative", "association"],
            ),
            inline=False,
        )
        embed.add_field(
            name="Hormone state",
            value=self._guild_ai_vector_text(hormone_state, GUILD_AI_HORMONE_LABELS),
            inline=False,
        )
        embed.add_field(
            name="Instinct state",
            value=self._guild_ai_vector_text(instinct_state, GUILD_AI_INSTINCT_LABELS),
            inline=False,
        )
        embed.add_field(
            name="Psych gradient",
            value=self._guild_ai_vector_text(
                gradient_state,
                ["dV", "dA", "dD", "dS"],
            ),
            inline=False,
        )
        embed.add_field(name="Speculative beliefs", value=belief_text, inline=False)
        embed.add_field(name="Complex phase", value=phase_text, inline=True)
        embed.add_field(name="Human style", value=style_text, inline=False)
        embed.add_field(name="Memory 2D", value=memory2d_text, inline=False)
        embed.add_field(name="Memory 3D", value=memory3d_text, inline=False)
        embed.add_field(name="Phrase bank", value=f"{phrase_count} patterns", inline=True)
        embed.add_field(name="Top tokens", value=token_text, inline=False)
        embed.add_field(name="Topic totals", value=topics, inline=False)
        embed.add_field(name="Recent filter reasons", value=reason_text, inline=False)
        embed.add_field(name="Last preview", value=preview, inline=False)
        embed.set_footer(text="Learns from messages in channels the bot can read.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="server_ai_profile",
        description="Set the server AI learning intensity",
    )
    @app_commands.describe(
        profile="balanced/aggressive/overdrive/beast",
    )
    async def server_ai_profile(
        self,
        interaction: discord.Interaction,
        profile: Literal["balanced", "aggressive", "overdrive", "beast"],
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in servers.",
                ephemeral=True,
            )
            return
        if not await self._can_manage_server_ai(interaction):
            await interaction.response.send_message(
                "Only the owner, admins, or members with Manage Server can change this.",
                ephemeral=True,
            )
            return
        selected = self.memory.set_guild_ai_profile(interaction.guild.id, profile)
        text = self._guild_ai_profile_text(selected)
        await interaction.response.send_message(
            f"Server AI learning profile set to `{selected}`.\n{text}",
            ephemeral=True,
        )

    @app_commands.command(
        name="server_ai_toggle",
        description="Manually enable or disable server chat learning",
    )
    @app_commands.describe(enabled="true enables learning, false disables it")
    async def server_ai_toggle(self, interaction: discord.Interaction, enabled: bool):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in servers.",
                ephemeral=True,
            )
            return
        if not await self._can_manage_server_ai(interaction):
            await interaction.response.send_message(
                "Only the owner, admins, or members with Manage Server can change this.",
                ephemeral=True,
            )
            return
        self.memory.set_guild_ai_enabled(interaction.guild.id, enabled)
        state = self.memory.get_guild_ai(interaction.guild.id)
        mode = "ON" if state.get("enabled", True) else "OFF"
        await interaction.response.send_message(
            f"Server AI learning: `{mode}`",
            ephemeral=True,
        )

    @app_commands.command(
        name="server_ai_reset",
        description="Reset this server's AI learning state",
    )
    async def server_ai_reset(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in servers.",
                ephemeral=True,
            )
            return
        if not await self._can_manage_server_ai(interaction):
            await interaction.response.send_message(
                "Only the owner, admins, or members with Manage Server can reset this.",
                ephemeral=True,
            )
            return
        self.memory.reset_guild_ai(interaction.guild.id)
        await interaction.response.send_message(
            "The server AI learning state has been reset.",
            ephemeral=True,
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        content = message.content.strip()
        if content and message.guild is not None:
            self._guild_ai_process_message(
                message.guild.id,
                content,
                message_at=message.created_at,
            )
        if content and not content.startswith("+"):
            self.memory.touch_message(message.author, content)
            self.memory.log_message(
                message.author,
                content,
                channel_id=getattr(message.channel, "id", None),
                guild_id=message.guild.id if message.guild else None,
                source="message",
            )
            self._learn_from_dialogue(message.author.id, content)
            teach_pair = self._extract_teach_pair(content)
            if teach_pair:
                question, answer = teach_pair
                question = _truncate(question, MAX_QA_QUESTION_LEN)
                answer = _truncate(answer, MAX_QA_ANSWER_LEN)
                self.memory.teach_qa(question, answer, message.author.id)
                return

            note_text = self._extract_note_request(content)
            if note_text:
                self.memory.add_note(message.author.id, _truncate(note_text, MAX_NOTE_LEN))

            preference = self._extract_preference(content)
            if preference:
                key, value = preference
                key = _normalize_key(key)
                value = _truncate(" ".join(value.split()), MAX_PREF_VALUE_LEN)
                self.memory.set_preference(message.author.id, key, value)
                if "favorite" in key and ("food" in key or "dish" in key):
                    self.memory.add_food_memory(message.author.id, value)

            food_items = self._extract_food_items(content)
            for item in food_items:
                self.memory.add_food_memory(message.author.id, item)

            story_facts = self._extract_story_facts(content)
            for fact in story_facts:
                self.memory.add_story_memory(message.author.id, fact)

            time_notes = self._extract_time_notes(content)
            for note in time_notes:
                self.memory.add_time_memory(message.author.id, note)

            self._capture_emotional_memory(message.author.id, content)
        else:
            self.memory.touch_message(message.author)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.user is None or interaction.user.bot:
            return
        if interaction.type == discord.InteractionType.application_command:
            name = None
            if isinstance(interaction.data, dict):
                name = interaction.data.get("name")
            if name:
                self.memory.mark_command(interaction.user.id, name)

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        if ctx.author.bot:
            return
        if ctx.command:
            self.memory.mark_command(ctx.author.id, ctx.command.name)

    @app_commands.command(name="chat", description="Chat with Panos.")
    async def chat(
        self,
        interaction: discord.Interaction,
        message: str,
        visibility: Literal["public", "private"] | None = None,
    ):
        message = " ".join(message.strip().split())
        if not message:
            await interaction.response.send_message(
                "Please provide a message to chat with me.", ephemeral=True
            )
            return
        name = self._display_name(interaction.user)
        is_creator = self._is_creator(interaction.user.id)
        profile = self.memory.get_profile(interaction.user.id)
        visibility_request = self._extract_visibility_request(message)
        if visibility_request:
            self.memory.set_preference(
                interaction.user.id, REPLY_VISIBILITY_KEY, visibility_request
            )
            reply = (
                "Got it. I'll reply privately."
                if visibility_request == "private"
                else "Got it. I'll reply publicly."
            )
            is_ephemeral = (
                visibility_request == "private" and interaction.guild is not None
            )
            await interaction.response.send_message(reply, ephemeral=is_ephemeral)
            return
        visibility_value = visibility.casefold() if visibility else None
        if visibility_value not in {"private", "public"}:
            visibility_value = None
        if visibility_value is None:
            visibility_value = self._get_reply_visibility(profile)
        is_ephemeral = visibility_value == "private" and interaction.guild is not None
        channel_id = interaction.channel.id if interaction.channel else None
        guild_id = interaction.guild.id if interaction.guild else None
        self.memory.log_message(
            interaction.user,
            message,
            channel_id=channel_id,
            guild_id=guild_id,
            source="chat",
        )
        self._learn_from_dialogue(interaction.user.id, message)
        if guild_id is not None:
            self._guild_ai_process_message(
                guild_id,
                message,
                message_at=getattr(interaction, "created_at", None),
            )
        mode_request = self._extract_chat_mode_request(message)
        if mode_request:
            self.memory.set_preference(interaction.user.id, "chat mode", mode_request)
            if mode_request == "personal":
                reply = "Got it. I'll keep it personal."
                if is_creator:
                    reply = "Got it. I'll keep it personal for you."
            else:
                reply = "Got it. I'll keep it non-personal."
                if is_creator:
                    reply = "Got it. I'll keep it non-personal."
            await interaction.response.send_message(reply, ephemeral=is_ephemeral)
            return

        memory_query = self._extract_memory_query(message)
        if memory_query is not None:
            if memory_query == "__last__":
                reply = self._build_last_message_reply(profile, is_creator)
            elif memory_query == "__last_time__":
                reply = self._build_last_time_reply(profile, is_creator)
            elif memory_query == "__story__":
                reply = self._build_story_memory_reply(profile, name, is_creator)
            elif memory_query == "":
                reply = self._build_memory_summary(
                    profile, interaction.user.id, name, is_creator
                )
            else:
                reply = self._build_memory_search_reply(
                    profile, interaction.user.id, memory_query, name, is_creator
                )
            await interaction.response.send_message(reply, ephemeral=is_ephemeral)
            return

        teach_pair = self._extract_teach_pair(message)
        if teach_pair:
            question, answer = teach_pair
            question = _truncate(question, MAX_QA_QUESTION_LEN)
            answer = _truncate(answer, MAX_QA_ANSWER_LEN)
            self.memory.teach_qa(question, answer, interaction.user.id)
            if is_creator:
                reply = f'Got it, {name}. If you say "{question}", I will say "{answer}".'
            else:
                reply = f'I learned it. If you say "{question}", I will say "{answer}".'
            await interaction.response.send_message(reply, ephemeral=is_ephemeral)
            return

        self.memory.set_last_message(interaction.user, message)

        time_request = self._extract_time_request(message)
        if time_request:
            reply = self._build_time_reply(is_creator)
            await interaction.response.send_message(reply, ephemeral=is_ephemeral)
            return

        self._capture_emotional_memory(interaction.user.id, message)

        story_facts = self._extract_story_facts(message)
        for fact in story_facts:
            self.memory.add_story_memory(interaction.user.id, fact)

        time_notes = self._extract_time_notes(message)
        for note in time_notes:
            self.memory.add_time_memory(interaction.user.id, note)

        note_text = self._extract_note_request(message)
        if note_text:
            note_text = _truncate(note_text, MAX_NOTE_LEN)
            self.memory.add_note(interaction.user.id, note_text)
            if is_creator:
                reply = random.choice(
                    [
                        "Got it. I'll remember that.",
                        "Noted. I'll keep that in mind.",
                        "Saved. Want me to remember anything else?",
                    ]
                )
            else:
                reply = random.choice(
                    [
                        "Got it. I'll remember that.",
                        "Noted. I'll keep that in mind.",
                        "Saved. Want me to remember anything else?",
                    ]
                )
            await interaction.response.send_message(reply, ephemeral=is_ephemeral)
            return

        preference = self._extract_preference(message)
        if preference:
            key, value = preference
            key = _normalize_key(key)
            value = _truncate(" ".join(value.split()), MAX_PREF_VALUE_LEN)
            self.memory.set_preference(interaction.user.id, key, value)
            if "favorite" in key and ("food" in key or "dish" in key):
                self.memory.add_food_memory(interaction.user.id, value)
            if is_creator:
                reply = f"Got it, {name}. I'll remember your {key} is {value}."
            else:
                reply = f"Got it. I'll remember your {key} is {value}."
            await interaction.response.send_message(reply, ephemeral=is_ephemeral)
            return

        food_items = self._extract_food_items(message)
        if food_items:
            for item in food_items:
                self.memory.add_food_memory(interaction.user.id, item)
            learned = ", ".join(food_items[:MAX_FOOD_SUGGESTIONS])
            if is_creator:
                reply = f"Yum. I'll remember you like {learned}."
            else:
                reply = f"Got it. I'll remember {learned}."
            await interaction.response.send_message(reply, ephemeral=is_ephemeral)
            return

        if self._is_food_question(message):
            foods = self.memory.get_food_suggestions(interaction.user.id)
            reply = self._build_food_reply(foods, name, is_creator)
            await interaction.response.send_message(reply, ephemeral=is_ephemeral)
            return

        learned = self.memory.find_qa_answer(message)
        if learned:
            await interaction.response.send_message(learned, ephemeral=is_ephemeral)
            return

        profile = self.memory.get_profile(interaction.user.id)
        is_private = interaction.guild is None
        reply = self._build_reply(
            name,
            message,
            is_creator,
            profile,
            interaction.user.id,
            is_private=is_private,
            guild_id=interaction.guild.id if interaction.guild else None,
        )
        await interaction.response.send_message(reply, ephemeral=is_ephemeral)

    @app_commands.command(name="continue_chat", description="Reply using your last message.")
    async def continue_chat(self, interaction: discord.Interaction):
        profile = self.memory.get_profile(interaction.user.id)
        last_message = profile.get("last_message")
        if not last_message:
            await interaction.response.send_message(
                "I don't have a recent message from you yet.", ephemeral=True
            )
            return
        learned = self.memory.find_qa_answer(last_message)
        if learned:
            await interaction.response.send_message(learned)
            return
        name = self._display_name(interaction.user)
        is_creator = self._is_creator(interaction.user.id)
        is_private = interaction.guild is None
        reply = self._build_reply(
            name,
            last_message,
            is_creator,
            profile,
            interaction.user.id,
            is_private=is_private,
            guild_id=interaction.guild.id if interaction.guild else None,
        )
        await interaction.response.send_message(reply)

    @app_commands.command(name="ask", description="Ask a taught question.")
    async def ask(self, interaction: discord.Interaction, question: str):
        question = " ".join(question.strip().split())
        if not question:
            await interaction.response.send_message(
                "Please provide a question.", ephemeral=True
            )
            return
        channel_id = interaction.channel.id if interaction.channel else None
        guild_id = interaction.guild.id if interaction.guild else None
        self.memory.log_message(
            interaction.user,
            question,
            channel_id=channel_id,
            guild_id=guild_id,
            source="ask",
        )
        self.memory.set_last_message(interaction.user, question)
        answer = self.memory.find_qa_answer(question)
        if not answer:
            await interaction.response.send_message(
                "I don't know that yet. Teach me with /teach.", ephemeral=True
            )
            return
        await interaction.response.send_message(answer)

    @app_commands.command(name="teach", description="Teach the bot a Q/A pair.")
    async def teach(self, interaction: discord.Interaction, question: str, answer: str):
        question = " ".join(question.strip().split())
        answer = " ".join(answer.strip().split())
        if not question or not answer:
            await interaction.response.send_message(
                "Please provide both a question and an answer.", ephemeral=True
            )
            return
        channel_id = interaction.channel.id if interaction.channel else None
        guild_id = interaction.guild.id if interaction.guild else None
        teach_entry = f"teach: {question} -> {answer}"
        self.memory.log_message(
            interaction.user,
            teach_entry,
            channel_id=channel_id,
            guild_id=guild_id,
            source="teach",
        )
        question = _truncate(question, MAX_QA_QUESTION_LEN)
        answer = _truncate(answer, MAX_QA_ANSWER_LEN)
        existed = self.memory.get_qa(question) is not None
        self.memory.teach_qa(question, answer, interaction.user.id)
        if existed:
            msg = "Updated the answer for that question."
        else:
            msg = "Learned! I will remember that."
        await interaction.response.send_message(msg, ephemeral=True)

    @app_commands.command(name="set_nickname", description="Set the name I will call you.")
    async def set_nickname(self, interaction: discord.Interaction, nickname: str):
        nickname = nickname.strip()
        if not nickname:
            await interaction.response.send_message(
                "Please provide a nickname.", ephemeral=True
            )
            return
        if len(nickname) > 32:
            nickname = nickname[:32]
        self.memory.set_nickname(interaction.user.id, nickname)
        await interaction.response.send_message(
            f"Got it. I'll call you **{nickname}**.", ephemeral=True
        )

    @app_commands.command(name="set_preference", description="Save a preference on your profile.")
    async def set_preference(self, interaction: discord.Interaction, key: str, value: str):
        key = _normalize_key(key)
        value = " ".join(value.strip().split())
        if not key or not value:
            await interaction.response.send_message(
                "Please provide both a key and a value.", ephemeral=True
            )
            return
        key = _truncate(key, MAX_PREF_KEY_LEN)
        value = _truncate(value, MAX_PREF_VALUE_LEN)
        self.memory.set_preference(interaction.user.id, key, value)
        await interaction.response.send_message(
            f"Saved preference **{key}** = **{value}**.", ephemeral=True
        )

    @app_commands.command(name="forget_preference", description="Remove a saved preference.")
    async def forget_preference(self, interaction: discord.Interaction, key: str):
        key = _normalize_key(key)
        if not key:
            await interaction.response.send_message(
                "Please provide a preference key to remove.", ephemeral=True
            )
            return
        removed = self.memory.remove_preference(interaction.user.id, key)
        if removed:
            msg = f"Removed preference **{key}**."
        else:
            msg = "I couldn't find that preference."
        await interaction.response.send_message(msg, ephemeral=True)

    @app_commands.command(name="remember", description="Save a note in your profile.")
    async def remember(self, interaction: discord.Interaction, note: str):
        note = " ".join(note.strip().split())
        if not note:
            await interaction.response.send_message(
                "Please provide something to remember.", ephemeral=True
            )
            return
        if len(note) > MAX_NOTE_LEN:
            note = note[:MAX_NOTE_LEN]
        self.memory.add_note(interaction.user.id, note)
        await interaction.response.send_message("Saved.", ephemeral=True)

    @app_commands.command(name="recall", description="Search what I remember about you.")
    async def recall(self, interaction: discord.Interaction, query: str | None = None):
        name = self._display_name(interaction.user)
        is_creator = self._is_creator(interaction.user.id)
        profile = self.memory.get_profile(interaction.user.id)
        if query:
            query = " ".join(query.strip().split())
        if not query:
            reply = self._build_memory_summary(profile, interaction.user.id, name, is_creator)
        elif query.casefold() in {"last", "last message", "recent message"}:
            reply = self._build_last_message_reply(profile, is_creator)
        elif query.casefold() in {"last time", "last seen", "last chat", "last talked"}:
            reply = self._build_last_time_reply(profile, is_creator)
        elif query.casefold() in {"story", "my story", "background"}:
            reply = self._build_story_memory_reply(profile, name, is_creator)
        else:
            reply = self._build_memory_search_reply(
                profile, interaction.user.id, query, name, is_creator
            )
        await interaction.response.send_message(reply, ephemeral=True)

    @app_commands.command(name="profile", description="View what I remember about you.")
    async def profile(self, interaction: discord.Interaction):
        profile = self.memory.get_profile(interaction.user.id)
        display_name = profile.get("display_name") or interaction.user.name
        nickname = profile.get("nickname") or "-"
        message_count = profile.get("message_count", 0)
        last_seen = profile.get("last_seen") or "-"
        last_message = profile.get("last_message") or "-"
        last_message_at = profile.get("last_message_at") or "-"
        notes = profile.get("notes", [])
        commands = profile.get("command_counts", {})
        preferences = profile.get("preferences", {})
        recent_messages = profile.get("recent_messages", [])
        foods = profile.get("food_memory", [])
        mood_history = profile.get("mood_history", [])
        thought_history = profile.get("thought_history", [])
        story_memory = profile.get("story_memory", [])
        time_memory = profile.get("time_memory", [])
        bond_state = profile.get("bond_state", {})
        emotion_profile = profile.get("emotion_profile", {})
        topic_signals = profile.get("topic_signals", {})
        recent_questions = profile.get("recent_questions", [])

        top_commands = sorted(commands.items(), key=lambda x: x[1], reverse=True)
        top_text = ", ".join([f"{name}({count})" for name, count in top_commands[:5]])
        if not top_text:
            top_text = "-"

        prefs_items = list(preferences.items())
        prefs_text = "\n".join(
            [f"- {key}: {value}" for key, value in prefs_items[:MAX_PREFS_IN_PROFILE]]
        )
        if not prefs_text:
            prefs_text = "-"
        if len(prefs_items) > MAX_PREFS_IN_PROFILE:
            prefs_text += "\n- ..."

        notes_preview = notes[-MAX_NOTES_IN_PROFILE:]
        notes_text = (
            "\n".join(f"- {_truncate(str(n), 120)}" for n in notes_preview)
            if notes_preview
            else "-"
        )
        if len(notes) > MAX_NOTES_IN_PROFILE:
            notes_text += "\n- ..."

        memory_totals = (
            f"Notes: {len(notes)} | Preferences: {len(preferences)} | "
            f"Recent messages: {len(recent_messages)} | Foods: {len(foods)} | "
            f"Feelings: {len(mood_history)} | Thoughts: {len(thought_history)} | "
            f"Stories: {len(story_memory)} | Time notes: {len(time_memory)} | "
            f"Questions: {len(recent_questions)}"
        )

        food_suggestions = self.memory.get_food_suggestions(interaction.user.id)
        food_text = ", ".join(food_suggestions[:MAX_FOOD_SUGGESTIONS]) if food_suggestions else "-"

        mood_summary = self._summarize_moods(mood_history)
        mood_text = ", ".join(mood_summary) if mood_summary else "-"
        recent_feelings = self._format_recent_moods(mood_history)
        recent_thoughts = self._format_recent_thoughts(thought_history)
        recent_story_notes = self._format_recent_story_notes(story_memory)
        recent_time_notes = self._format_recent_time_notes(time_memory)
        bond_text = self._format_bond_state(bond_state)
        topic_text = self._format_topic_signals(topic_signals)
        emotion_text = self._format_topic_signals(emotion_profile)
        question_text = self._format_recent_questions(recent_questions)

        name = self._display_name(interaction.user)
        description = (
            f"Here is what I remember about you, {name}. "
            "I'll keep learning as we talk."
        )

        embed = discord.Embed(
            title="Panos Memory Profile",
            description=description,
            color=discord.Color.pink(),
            timestamp=interaction.created_at,
        )
        identity_text = f"Name: {display_name}\nNickname: {nickname}"
        activity_text = (
            f"Messages: {message_count}\n"
            f"Last seen: {last_seen}\n"
            f"Last message at: {last_message_at}"
        )
        embed.add_field(name="Identity", value=identity_text, inline=False)
        embed.add_field(name="Activity", value=activity_text, inline=False)
        embed.add_field(name="Last message", value=last_message, inline=False)
        embed.add_field(name="Preferences", value=prefs_text, inline=False)
        embed.add_field(name="Food memory", value=food_text, inline=False)
        embed.add_field(name="Mood trend", value=mood_text, inline=False)
        embed.add_field(name="Bond state", value=bond_text, inline=False)
        embed.add_field(name="Emotion signature", value=emotion_text, inline=False)
        embed.add_field(name="Interest map", value=topic_text, inline=False)
        embed.add_field(name="Recent questions", value=question_text, inline=False)
        embed.add_field(name="Recent feelings", value=recent_feelings, inline=False)
        embed.add_field(name="Recent thoughts", value=recent_thoughts, inline=False)
        embed.add_field(name="Story notes", value=recent_story_notes, inline=False)
        embed.add_field(name="Time notes", value=recent_time_notes, inline=False)
        embed.add_field(name="Notes", value=notes_text, inline=False)
        embed.add_field(name="Top commands", value=top_text, inline=False)
        embed.add_field(name="Memory totals", value=memory_totals, inline=False)
        embed.set_footer(text="Panos keeps learning from your chats.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="forget_me", description="Delete what I remember about you.")
    async def forget_me(self, interaction: discord.Interaction):
        self.memory.forget_user(interaction.user.id)
        await interaction.response.send_message(
            "I've cleared what I know about you.", ephemeral=True
        )

    @app_commands.command(name="name", description="Tell you the name I'll use for you.")
    async def myname(self, interaction: discord.Interaction):
        name = self._display_name(interaction.user)
        if self._is_creator(interaction.user.id):
            msg = f"I'll call you {name}."
        else:
            msg = f"I'll call you {name}."
        await interaction.response.send_message(msg)

    @app_commands.command(name="what_is_my_name", description="Tell you my name.")
    async def botname(self, interaction: discord.Interaction):
        bot_name = BOT_GIRL_NAME
        if self._is_creator(interaction.user.id):
            msg = f"I'm {bot_name}, your friend."
        else:
            msg = f"I'm {bot_name}."
        await interaction.response.send_message(msg)

    @app_commands.command(name="creator", description="Tell you who created me.")
    async def creator(self, interaction: discord.Interaction):
        name = self._display_name(interaction.user)
        is_creator = self._is_creator(interaction.user.id)
        reply = self._build_creator_reply(False, name, is_creator)
        await interaction.response.send_message(reply)

    @app_commands.command(name="birthday", description="Tell you my birthday.")
    async def birthday(self, interaction: discord.Interaction):
        reply = self._build_birthday_reply(False)
        await interaction.response.send_message(reply)

    @app_commands.command(name="hungry", description="Say you're hungry.")
    async def hungry(self, interaction: discord.Interaction):
        name = self._display_name(interaction.user)
        if self._is_creator(interaction.user.id):
            msg = f"I'm hungry too, {name}. Want to grab something together?"
        else:
            msg = "I'm hungry too. Want a snack?"
        await interaction.response.send_message(msg)

    @app_commands.command(name="you_favorite_is", description="Ask what I like.")
    async def laugh(self, interaction: discord.Interaction):
        name = self._display_name(interaction.user)
        if self._is_creator(interaction.user.id):
            responses = [
                f"I like cozy chats, soft music, and you, {name}.",
                "I like late-night talks, warm hugs, and sweet texts.",
                "I like calm vibes, gentle playlists, and your attention.",
            ]
        else:
            responses = [
                "I like cozy chats, soft music, and silly memes.",
                "I like kind people and good conversations.",
                "I like calm vibes and friendly company.",
            ]
        await interaction.response.send_message(random.choice(responses))

    @app_commands.command(name="love", description="Say you love me.")
    async def love(self, interaction: discord.Interaction):
        name = self._display_name(interaction.user)
        if self._is_creator(interaction.user.id):
            msg = f"That means a lot, {name}."
        else:
            msg = "Aww, thank you."
        await interaction.response.send_message(msg)

    @app_commands.command(
        name="happy_new_year_2026",
        description="Send an epic Happy New Year 2026 celebration.",
    )
    @app_commands.describe(
        duration_seconds="How long to run in seconds (0 = keep going).",
    )
    async def happy_new_year_2026(
        self,
        interaction: discord.Interaction,
        duration_seconds: int = 0,
    ):
        width = 64
        fps = 10
        frame_count = 2
        bar_pattern = "==--~~**"
        bar = (bar_pattern * ((width // len(bar_pattern)) + 1))[:width]
        firework_frames = [
            "".join("*" if j % 6 == 0 else " " for j in range(width)),
            "".join("+" if j % 6 == 0 else " " for j in range(width)),
        ]
        duration_seconds = max(0, duration_seconds)
        if duration_seconds:
            duration_seconds = min(duration_seconds, 600)
        font = {
            "H": [
                "#   #",
                "#   #",
                "#   #",
                "#####",
                "#   #",
                "#   #",
                "#   #",
            ],
            "A": [
                " ### ",
                "#   #",
                "#   #",
                "#####",
                "#   #",
                "#   #",
                "#   #",
            ],
            "P": [
                "#####",
                "#   #",
                "#   #",
                "#####",
                "#    ",
                "#    ",
                "#    ",
            ],
            "Y": [
                "#   #",
                "#   #",
                " # # ",
                "  #  ",
                "  #  ",
                "  #  ",
                "  #  ",
            ],
            "N": [
                "#   #",
                "##  #",
                "# # #",
                "#  ##",
                "#   #",
                "#   #",
                "#   #",
            ],
            "E": [
                "#####",
                "#    ",
                "#    ",
                "#### ",
                "#    ",
                "#    ",
                "#####",
            ],
            "W": [
                "#   #",
                "#   #",
                "#   #",
                "# # #",
                "# # #",
                "## ##",
                "#   #",
            ],
            "R": [
                "#####",
                "#   #",
                "#   #",
                "#####",
                "# #  ",
                "#  # ",
                "#   #",
            ],
            "2": [
                "#####",
                "    #",
                "   # ",
                "  #  ",
                " #   ",
                "#    ",
                "#####",
            ],
            "0": [
                " ### ",
                "#   #",
                "#   #",
                "#   #",
                "#   #",
                "#   #",
                " ### ",
            ],
            "6": [
                " ### ",
                "#    ",
                "#    ",
                "#### ",
                "#   #",
                "#   #",
                " ### ",
            ],
            " ": ["     "] * 7,
        }

        def render_word(text: str) -> list[str]:
            lines = [""] * 7
            for ch in text:
                glyph = font.get(ch, font[" "])
                for idx in range(7):
                    lines[idx] += glyph[idx] + "  "
            return lines

        def center_lines(lines: list[str]) -> list[str]:
            return [line.center(width) for line in lines]

        banner = (
            center_lines(render_word("HAPPY"))
            + [""]
            + center_lines(render_word("NEW YEAR"))
            + [""]
            + center_lines(render_word("2026"))
        )
        channel_id = interaction.channel_id
        if channel_id is None and interaction.channel:
            channel_id = interaction.channel.id
        if channel_id is None:
            channel_id = interaction.user.id
        previous_stop = self._new_year_stop_events.get(channel_id)
        if previous_stop:
            previous_stop.set()
        stop_event = asyncio.Event()
        self._new_year_stop_events[channel_id] = stop_event
        frames: list[str] = []
        for i in range(frame_count):
            fire = firework_frames[i % len(firework_frames)]
            banner_lines = banner
            frame_lines = [
                fire,
                "```",
                bar,
                "",
                *banner_lines,
                "",
                "MAY YOUR 2026 SHINE!",
                "```",
                fire,
            ]
            frames.append("\n".join(frame_lines))

        try:
            await interaction.response.send_message(frames[0])
            message = await interaction.original_response()
            delay = 1.0 / fps
            loop = asyncio.get_running_loop()
            end_time = loop.time() + duration_seconds if duration_seconds else None
            frame_index = 1
            min_delay = delay
            max_delay = 1.0
            while True:
                if stop_event.is_set():
                    break
                if end_time is not None and loop.time() >= end_time:
                    break
                await asyncio.sleep(delay)
                try:
                    await message.edit(content=frames[frame_index % len(frames)])
                    delay = max(min_delay, delay * 0.95)
                except (discord.NotFound, discord.Forbidden):
                    break
                except discord.HTTPException:
                    delay = min(max_delay, delay + 0.2)
                frame_index += 1
        finally:
            current_stop = self._new_year_stop_events.get(channel_id)
            if current_stop is stop_event:
                del self._new_year_stop_events[channel_id]

    @app_commands.command(
        name="stop_new_year_2026",
        description="Stop the Happy New Year 2026 animation in this channel.",
    )
    async def stop_new_year_2026(self, interaction: discord.Interaction):
        channel_id = interaction.channel_id
        if channel_id is None and interaction.channel:
            channel_id = interaction.channel.id
        if channel_id is None:
            channel_id = interaction.user.id
        stop_event = self._new_year_stop_events.get(channel_id)
        if not stop_event:
            await interaction.response.send_message("No New Year animation is running here.")
            return
        stop_event.set()
        await interaction.response.send_message("Stopped the New Year animation.")

async def setup(bot):
    await bot.add_cog(TalkCog(bot))
