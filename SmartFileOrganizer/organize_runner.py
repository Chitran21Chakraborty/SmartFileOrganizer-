import schedule
import time
from file_organizer import organize_directory
from datetime import datetime
import json
import os

# Load scheduled jobs
if not os.path.exists("scheduled_jobs.json"):
    print("No scheduled jobs found")
    exit()

with open("scheduled_jobs.json", "r") as f:
    job = json.load(f)

folder_path = job["folder"]
times_list = job["times"]

def job_func():
    print(f"Starting scheduled organization for {folder_path} at {datetime.now()}")
    for event in organize_directory(folder_path):
        print(event)

# Schedule all times
for t in times_list:
    schedule.every().day.at(t).do(job_func)

print(f"Scheduler running... Folder: {folder_path} | Times: {', '.join(times_list)}")

while True:
    schedule.run_pending()
    time.sleep(1)
