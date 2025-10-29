import schedule
import time
import json
from file_organizer import organize_directory
import os

def run_job(folder):
    if os.path.exists(folder) and os.path.isdir(folder):
        print(f" Running organizer for {folder}")
        for event in organize_directory(folder):
            status = event["status"]
            if status == "moved":
                print(f"Moved {event['file']} → {event['category']}")
            elif status == "skipped":
                print(f"Skipped {event['file']} ({event['reason']})")
            elif status == "error":
                print(f"Error {event.get('file','')}: {event.get('message','')}")
        print("🎉 Organization complete!\n")
    else:
        print(f"Folder not found: {folder}")

# Load schedule
try:
    with open("scheduled_jobs.json", "r") as f:
        data = json.load(f)
        folder = data["folder"]
        times = data["times"]
except Exception as e:
    print("No scheduled jobs found or error reading file.")
    folder = None
    times = []

if folder and times:
    for t in times:
        schedule.every().day.at(t).do(run_job, folder=folder)
        print(f"Scheduled {folder} at {t}")

    print("🟢 Scheduler running... Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(10)
