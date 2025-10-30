# 🗂️ SmartFileOrganizer

**SmartFileOrganizer** is an intelligent desktop utility built in Python that **scans, organizes, and analyzes files** within any directory.  
It categorizes files automatically based on their extensions, keeps an **undo history**, and provides **storage analytics and growth forecasting** using machine learning.

---

## 🚀 Key Features

✅ **Smart File Organization**
- Automatically sorts files into predefined categories (Images, Documents, Audio, etc.)  
- Detects duplicates and renames safely without overwriting.  
- Handles missing extensions and hidden files gracefully.

✅ **Undo Support**
- Every organization operation is saved in `history.json`.  
- You can revert the last operation safely and restore files to their original locations.

✅ **Deep Folder Scanning**
- Recursively scans directories, collecting detailed metadata about files.  
- Detects largest, oldest, and newest files.  
- Identifies empty folders, hidden files, and duplicate candidates.

✅ **Data Analytics & Forecasting**
- Visualizes file type and folder size distributions.  
- Tracks growth of files over time.  
- Uses **Linear Regression (Sklearn)** to predict future storage usage.

✅ **Streamlit Dashboard (GUI)**
- Interactive web-based interface for all operations:
  - Scan Folder  
  - Organize Folder  
  - Undo Last Operation  
  - Dashboard & Analytics Visualization

---

## 📁 Project Structure

SmartFileOrganizer/
│
├── file_organizer.py # Core logic: organizing files into categories
├── history_store.py # Undo and operation history persistence
├── scanner.py # Deep folder scanner for metadata
├── analytics.py # Data visualization and storage forecasting
├── gui_app.py # Streamlit-based graphical interface
├── config.py # Category definitions and configuration
├── logs/ # Folder where runtime logs are stored
├── history.json # Stores organization history
└── requirements.txt # Dependencies list



          ┌─────────────────────────┐
          │       User GUI          │
          │    (Streamlit App)      │
          └──────────┬──────────────┘
                     │
                     ▼
      ┌────────────────────────────┐
      │    file_organizer.py       │
      │   (Organize + Log + Undo)  │
      └──────────┬─────────────────┘
                 │
                 ▼
      ┌────────────────────────────┐
      │     history_store.py       │
      │   (Save + Undo History)    │
      └──────────┬─────────────────┘
                 │
                 ▼
      ┌────────────────────────────┐
      │       scanner.py           │
      │  (Collect Raw Metadata)    │
      └──────────┬─────────────────┘
                 │
                 ▼
      ┌────────────────────────────┐
      │       analytics.py         │
      │   (Visualize + Forecast)   │
      └────────────────────────────┘


📊 Example Workflow

1️⃣ User selects a folder in the Streamlit app.
2️⃣ scanner.py performs a deep scan → returns metadata → optional JSON export.
3️⃣ file_organizer.py organizes files → logs moves → saves run_id.
4️⃣ If user clicks Undo, history_store.py restores all moved files.
5️⃣ analytics.py reads scan data → generates charts and storage growth forecast.




🧪 Tech Stack
Category	Technologies
Language	Python 3.10+
Frontend	Streamlit
Data Analysis	Pandas, NumPy, Matplotlib, Scikit-learn
Filesystem	os, shutil, pathlib
Persistence	JSON (history), Logs (FileHandler)
