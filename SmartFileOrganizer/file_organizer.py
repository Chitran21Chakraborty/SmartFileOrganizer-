import os
import shutil
import logging
from datetime import datetime
from config import CATEGORIES, DEFAULT_CATEGORY

# Setup logging
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)
log_file = os.path.join(log_folder, f"organizer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def get_category(extension):
    """Return the folder name for a given file extension."""
    for category, extensions in CATEGORIES.items():
        if extension.lower() in extensions:
            return category
    return DEFAULT_CATEGORY

def organize_directory(path):
    """Scan the given directory and organize files into categorized folders."""
    if not os.path.exists(path):
        logging.error(f"Path does not exist: {path}")
        print("❌ Path does not exist!")
        return
    
    if not os.path.isdir(path):
        logging.error(f"Path is not a directory: {path}")
        print("❌ Path is not a directory!")
        return
    
    logging.info(f"Starting organization of: {path}")
    print(f"\n🚀 Starting SmartFileOrganizer...\n")
    
    files_moved = 0
    files_skipped = 0
    
    # Loop through each item in directory
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        
        # Skip folders and log files
        if os.path.isdir(file_path):
            continue
        
        # Skip log folder files
        if file_path.startswith(os.path.join(path, "logs")):
            continue
        
        # Find file extension
        _, ext = os.path.splitext(file)
        
        if not ext:
            logging.warning(f"Skipped file without extension: {file}")
            files_skipped += 1
            continue
        
        category = get_category(ext)
        
        # Create destination folder
        category_folder = os.path.join(path, category)
        os.makedirs(category_folder, exist_ok=True)
        
        destination_path = os.path.join(category_folder, file)
        
        # Handle duplicate filenames
        if os.path.exists(destination_path):
            base_name, extension = os.path.splitext(file)
            counter = 1
            while os.path.exists(destination_path):
                new_name = f"{base_name}_{counter}{extension}"
                destination_path = os.path.join(category_folder, new_name)
                counter += 1
            logging.info(f"Renamed duplicate: {file} → {os.path.basename(destination_path)}")
        
        # Move file
        try:
            shutil.move(file_path, destination_path)
            logging.info(f"Moved: {file} → {category}/")
            print(f"✅ Moved {file} → {category}/")
            files_moved += 1
        except Exception as e:
            logging.error(f"Error moving {file}: {e}")
            print(f"❌ Error moving {file}: {e}")
            files_skipped += 1
    
    # Summary
    print(f"\n{'-'*50}")
    print(f"📊 Organization Complete!")
    print(f"{'-'*50}")
    print(f"✅ Files moved: {files_moved}")
    print(f"⚠️  Files skipped: {files_skipped}")
    print(f"📝 Log saved: {log_file}")
    print(f"{'-'*50}\n")
    
    logging.info(f"Organization complete. Files moved: {files_moved}, Files skipped: {files_skipped}")

if __name__ == "__main__":
    print("🗂️  SmartFileOrganizer")
    target = input("\n📁 Enter folder path to organize: ").strip('"').strip("'")
    
    if target:
        organize_directory(target)
    else:
        print("❌ No path provided. Exiting...")
        logging.warning("No path provided by user")