import os
import shutil
import logging
from datetime import datetime
import uuid
from config import CATEGORIES, DEFAULT_CATEGORY
from history_store import save_history, undo_last_operation

#Logging Setup
LOG_FOLDER = "logs"
os.makedirs(LOG_FOLDER, exist_ok=True)
log_file = os.path.join(LOG_FOLDER, f"organizer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

#Category Helper
def get_category(extension):
    """Return category name for given file extension."""
    for category, extensions in CATEGORIES.items():
        if extension.lower() in extensions:
            return category
    return DEFAULT_CATEGORY

# Main Logic
def organize_directory(path):
    """
    Organizes files in any system folder.
    Yields dicts for GUI (Streamlit) progress:
        {"status": ..., "file": ..., "category": ..., "done": i, "total": n}
    """
    moved_files = []

    if not os.path.exists(path) or not os.path.isdir(path):
        yield {"status": "error", "message": f"Invalid path: {path}"}
        return

    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    total_files = len(files)
    if total_files == 0:
        yield {"status": "warning", "message": "No files found to organize."}
        return

    for i, file in enumerate(files):
        file_path = os.path.join(path, file)
        _, ext = os.path.splitext(file)
        if not ext:
            yield {"status": "skipped", "file": file, "reason": "No extension", "done": i + 1, "total": total_files}
            continue

        category = get_category(ext)
        category_folder = os.path.join(path, category)
        os.makedirs(category_folder, exist_ok=True)
        destination_path = os.path.join(category_folder, file)

        # Handle duplicates
        if os.path.exists(destination_path):
            base_name, extension = os.path.splitext(file)
            counter = 1
            while os.path.exists(destination_path):
                destination_path = os.path.join(category_folder, f"{base_name}_{counter}{extension}")
                counter += 1

        try:
            shutil.move(file_path, destination_path)
            moved_files.append({"from": file_path, "to": destination_path})
            yield {"status": "moved", "file": file, "category": category, "done": i + 1, "total": total_files}
        except Exception as e:
            yield {"status": "error", "file": file, "message": str(e), "done": i + 1, "total": total_files}

    if moved_files:
        run_id = str(uuid.uuid4())
        save_history(run_id, moved_files)
        yield {"status": "done", "moved": len(moved_files), "skipped": total_files - len(moved_files), "run_id": run_id}
