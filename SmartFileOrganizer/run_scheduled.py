"""
simple_scheduler.py - Just run this file, it will do everything!
"""

import schedule
import time
import json
import os
from datetime import datetime

def organize_now(folder):
    """Run the organizer"""
    print(f"\n{'='*60}")
    print(f"🟢 Starting organization at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 Folder: {folder}")
    print(f"{'='*60}\n")
    
    try:
        from file_organizer import organize_directory
        
        moved = 0
        skipped = 0
        errors = 0
        
        for event in organize_directory(folder):
            status = event.get("status", "")
            if status == "moved":
                print(f"✅ Moved: {event.get('file', '')} → {event.get('category', '')}")
                moved += 1
            elif status == "skipped":
                print(f"⚠️  Skipped: {event.get('file', '')} - {event.get('reason', '')}")
                skipped += 1
            elif status == "error":
                print(f"❌ Error: {event.get('file', '')} - {event.get('message', '')}")
                errors += 1
        
        print(f"\n{'='*60}")
        print(f"✅ Done! Moved: {moved} | Skipped: {skipped} | Errors: {errors}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")

def main():
    """Main function - just run this!"""
    
    print("""
╔════════════════════════════════════════════════════════╗
║       SmartFileOrganizer - Simple Scheduler           ║
║                                                        ║
║   This will run file organization at scheduled times  ║
║   Press Ctrl+C to stop                                ║
╚════════════════════════════════════════════════════════╝
    """)
    
    # Try to load schedule
    if not os.path.exists("scheduled_jobs.json"):
        print("❌ ERROR: No schedule found!")
        print("\n📝 How to fix:")
        print("1. Open the Streamlit app")
        print("2. Go to Schedule view")
        print("3. Enter folder path and times")
        print("4. Click 'Save Schedule'")
        print("5. Then run this script again!\n")
        input("Press Enter to exit...")
        return
    
    # Load schedule
    try:
        with open("scheduled_jobs.json", "r") as f:
            data = json.load(f)
        
        folder = data.get("folder", "")
        times = data.get("times", [])
        
        if not folder or not times:
            print("❌ ERROR: Schedule is empty!")
            print("Please configure it in the app first.\n")
            input("Press Enter to exit...")
            return
        
        # Check if folder exists
        if not os.path.exists(folder):
            print(f"❌ ERROR: Folder not found: {folder}")
            print("Please check the path and try again.\n")
            input("Press Enter to exit...")
            return
        
        # Schedule the jobs
        print(f"📂 Folder to organize: {folder}")
        print(f"⏰ Scheduled times:")
        for t in times:
            schedule.every().day.at(t).do(organize_now, folder=folder)
            print(f"   • {t}")
        
        print(f"\n{'='*60}")
        print("🟢 SCHEDULER IS RUNNING!")
        print("Keep this window open. Press Ctrl+C to stop.")
        print(f"{'='*60}\n")
        
        # Run forever
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
    
    except KeyboardInterrupt:
        print("\n\n🛑 Scheduler stopped. Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()