import sqlite3
import json

def backup_to_local(transactions, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(transactions, f, indent=2)

def restore_from_local(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

# Cloud backup stubs
def backup_to_cloud(transactions, provider="gdrive"):
    # Integrate with provider API (stub)
    pass

def schedule_backup(interval="daily"):
    # Use OS scheduler or background thread (stub)
    pass
