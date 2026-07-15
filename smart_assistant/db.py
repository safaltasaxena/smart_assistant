"""
db.py
-----
Thin Firestore wrapper.

Schema
------
Collection : users
Document   : {user_id}
Fields     : tasks   -> list[dict]   {id, title, time, urgency, created_at}
             events  -> list[dict]   {id, title, time, created_at}
             notes   -> list[str]

All writes use merge=True so partial updates never destroy sibling fields.
All reads return an empty list/dict when the document is missing.
"""

import os
import logging
import uuid
from datetime import datetime, timezone

from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    raise RuntimeError("GOOGLE_CLOUD_PROJECT not set in .env")

try:
    _db = firestore.Client(project=PROJECT_ID)
except Exception as exc:
    raise RuntimeError(f"Firestore init failed: {exc}") from exc


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ref(user_id: str):
    return _db.collection("users").document(user_id)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_id() -> str:
    return str(uuid.uuid4())[:8]


# ---------------------------------------------------------------------------
# Generic load / save (kept for backward compat with r.py / test scripts)
# ---------------------------------------------------------------------------

def load(user_id: str, key: str) -> list:
    doc = _ref(user_id).get()
    if doc.exists:
        return doc.to_dict().get(key, [])
    return []


def save(user_id: str, key: str, value) -> None:
    print("=" * 50)
    print("SAVE CALLED")
    print("User:", user_id)
    print("Key:", key)
    print("Value:", value)

    logger.info("SAVE user=%s key=%s", user_id, key)

    try:
        _ref(user_id).set({key: value}, merge=True)
        print("✅ SAVE SUCCESS")
    except Exception as e:
        print("❌ SAVE FAILED")
        print(type(e).__name__)
        print(e)
        raise


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def get_tasks(user_id: str) -> list[dict]:
    return load(user_id, "tasks")


def add_task(user_id: str, title: str, time: str, urgency: str) -> dict:
    task = {
        "id": make_id(),
        "title": title,
        "time": time,
        "urgency": urgency,
        "created_at": _now(),
    }
    tasks = get_tasks(user_id)
    tasks.append(task)
    save(user_id, "tasks", tasks)
    return task


def edit_task(user_id: str, task_id: str, **kwargs) -> dict | None:
    tasks = get_tasks(user_id)
    for t in tasks:
        if t.get("id") == task_id:
            t.update(kwargs)
            save(user_id, "tasks", tasks)
            return t
    return None


def delete_task(user_id: str, task_id: str) -> bool:
    tasks = get_tasks(user_id)
    new_tasks = [t for t in tasks if t.get("id") != task_id]
    if len(new_tasks) == len(tasks):
        return False
    save(user_id, "tasks", new_tasks)
    return True


# ---------------------------------------------------------------------------
# Events (meetings / study sessions)
# ---------------------------------------------------------------------------

def get_events(user_id: str) -> list[dict]:
    return load(user_id, "events")


def add_event(user_id: str, title: str, time: str, urgency: str) -> dict:
    event = {
        "id": make_id(),
        "title": title,
        "time": time,
        "urgency": urgency,
        "created_at": _now(),
    }
    events = get_events(user_id)
    events.append(event)
    save(user_id, "events", events)
    return event


def edit_event(user_id: str, event_id: str, **kwargs) -> dict | None:
    events = get_events(user_id)
    for e in events:
        if e.get("id") == event_id:
            e.update(kwargs)
            save(user_id, "events", events)
            return e
    return None


def delete_event(user_id: str, event_id: str) -> bool:
    events = get_events(user_id)
    new_events = [e for e in events if e.get("id") != event_id]
    if len(new_events) == len(events):
        return False
    save(user_id, "events", new_events)
    return True


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------

def get_notes(user_id: str) -> list[str]:
    return load(user_id, "notes")


def add_note(user_id: str, note: str) -> str:
    notes = get_notes(user_id)
    notes.append(note)
    save(user_id, "notes", notes)
    return note


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def get_all_times(user_id: str) -> list[str]:
    """Return every scheduled time (normalized strings) across tasks + events."""
    times: list[str] = []
    for item in get_tasks(user_id) + get_events(user_id):
        t = item.get("time")
        if t:
            times.append(t.strip().upper())
    return times


def get_item_at_time(user_id: str, time: str) -> dict | None:
    """
    Return the task/event scheduled at the given time.

    Returns:
        {
            "type": "task" | "event",
            "id": "...",
            "title": "...",
            "time": "...",
            "urgency": "...",
            "created_at": "..."
        }

    Returns None if nothing exists.
    """
    normalized = time.strip().upper()

    for task in get_tasks(user_id):
        if task.get("time", "").strip().upper() == normalized:
            return {
                "type": "task",
                **task,
            }

    for event in get_events(user_id):
        if event.get("time", "").strip().upper() == normalized:
            return {
                "type": "event",
                **event,
            }

    return None


def check_conflict(user_id: str, time: str) -> dict | None:
    """
    Return the conflicting task/event if one exists.
    Otherwise return None.
    """
    return get_item_at_time(user_id, time)