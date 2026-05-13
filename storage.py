import os
import json
from typing import List, Dict

SAVE_DIR = "saved_chats"

def _ensure_dir():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

def save_chat_session(title: str, history: List[Dict]) -> None:
    _ensure_dir()
    # Sanitize title for filename
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    if not safe_title:
        safe_title = "untitled"
    
    file_path = os.path.join(SAVE_DIR, f"{safe_title}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def get_saved_chats() -> List[str]:
    _ensure_dir()
    files = [f for f in os.listdir(SAVE_DIR) if f.endswith('.json')]
    # Return titles without .json extension
    return [f[:-5] for f in files]

def load_chat_session(title: str) -> List[Dict]:
    _ensure_dir()
    file_path = os.path.join(SAVE_DIR, f"{title}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
