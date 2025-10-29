import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"

def save_history(run_id, moves_list):
    history = []

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []

    run_entry = {
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "moves": moves_list,
        "undone": False
    }

    history.append(run_entry)

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

def load_last_history():
    if not os.path.exists(HISTORY_FILE):
        return None

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            history = json.load(f)
            if not history:
                return None
            for run_entry in reversed(history):
                if not run_entry.get("undone", False):
                    return run_entry
            return None
        except json.JSONDecodeError:
            return None

def undo_last_operation():
    last_run = load_last_history()
    if not last_run:
        print("No history available to undo.")
        return False

    moves = last_run["moves"]
    errors = 0

    for move in reversed(moves):
        src = move["to"]
        dest = move["from"]

        if os.path.exists(src):
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                os.rename(src, dest)
            except Exception as e:
                print(f"Failed to undo {src} → {dest}: {e}")
                errors += 1

    # Mark run as undone
    with open(HISTORY_FILE, "r+", encoding="utf-8") as f:
        history = json.load(f)
        for run_entry in history:
            if run_entry["run_id"] == last_run["run_id"]:
                run_entry["undone"] = True
                break
        f.seek(0)
        json.dump(history, f, indent=4)
        f.truncate()

    print(f"✅ Undo complete with {errors} errors.")
    return True
