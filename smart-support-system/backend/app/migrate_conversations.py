import os
import json
import uuid
from datetime import datetime

# ---------------- Paths ---------------- #
BASE_DIR = os.path.dirname(__file__)
OLD_FILE = os.path.join(BASE_DIR, "services", "old_conversations.json")  # <-- put your old JSON here
NEW_FILE = os.path.join(BASE_DIR, "services", "conversations.json")  # New chat-style JSON

# ---------------- Helpers ---------------- #
def iso_now():
    return datetime.utcnow().isoformat()

def migrate_user_conversations(user, old_entries):
    """Convert old flat entries to new chat-style format."""
    new_chats = []
    for entry in old_entries:
        chat_id = str(uuid.uuid4())
        new_chat = {
            "id": chat_id,
            "title": entry.get("question", "New Chat")[:20] + ("..." if len(entry.get("question", "")) > 20 else ""),
            "messages": [
                {
                    "sender": "user",
                    "text": entry.get("question", ""),
                    "timestamp": entry.get("timestamp", iso_now()),
                    "product_id": entry.get("product_id", ""),
                    "sources": []  # old entries may not have separate sources per message
                },
                {
                    "sender": "assistant",
                    "text": entry.get("answer", ""),
                    "timestamp": entry.get("timestamp", iso_now()),
                    "product_id": entry.get("product_id", ""),
                    "sources": entry.get("sources", [])
                }
            ],
            "created_at": entry.get("timestamp", iso_now()),
            "updated_at": entry.get("timestamp", iso_now())
        }
        new_chats.append(new_chat)
    return new_chats

# ---------------- Main Migration ---------------- #
if not os.path.exists(OLD_FILE):
    print(f"Old conversation file not found: {OLD_FILE}")
    exit(1)

with open(OLD_FILE, "r") as f:
    old_data = json.load(f)

new_data = {}
for user, entries in old_data.items():
    new_data[user] = migrate_user_conversations(user, entries)

# Ensure services folder exists
os.makedirs(os.path.join(BASE_DIR, "services"), exist_ok=True)

with open(NEW_FILE, "w") as f:
    json.dump(new_data, f, indent=2)

print(f"Migration completed! New file saved at: {NEW_FILE}")
