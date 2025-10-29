import streamlit as st
import os
from file_organizer import organize_directory
from history_store import undo_last_operation
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="SmartFileOrganizer",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS  styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
* { font-family: 'Poppins', sans-serif; }
.stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.css-1d391kg { padding-top: 0rem; margin-top: 0rem; }

.main-container {
    background: white;
    border-radius: 20px;
    padding: 2rem;
    margin: 2rem auto;
    max-width: 900px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
}

h1 { font-size: 2.8rem; font-weight: 700; color: #4f46e5; text-align: center; margin-bottom: 0.3rem; }
.subtitle { text-align: center; font-weight: 400; font-size: 1.1rem; color: #374151; margin-bottom: 2rem; }

.stButton>button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
    padding: 0.7rem 2rem;
    font-weight: 600;
    width: 100%;
}

.log-container {
    background: #f9fafb;
    border-radius: 15px;
    padding: 1rem;
    height: 300px;
    overflow-y: scroll;
    margin-top: 1rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    font-family: monospace;
    font-size: 0.9rem;
    color: black;
}

.time-chip {
    display: inline-block;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 0.5rem 1rem;
    margin: 0.3rem;
    border-radius: 20px;
    font-size: 0.95rem;
    font-weight: 600;
}

.time-chip-container {
    background: #f9fafb;
    padding: 1rem;
    border-radius: 15px;
    margin: 1rem 0;
    min-height: 60px;
    border: 2px dashed #e5e7eb;
}

input[type="time"] {
    pointer-events: auto !important;
    font-size: 1rem;
    padding: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'stats' not in st.session_state:
    st.session_state.stats = {'moved': 0, 'skipped': 0, 'errors': 0}
if 'scheduled_times' not in st.session_state:
    st.session_state.scheduled_times = []
if 'scheduled_job' not in st.session_state:
    st.session_state.scheduled_job = {}

# Header
st.markdown("<div class='main-container'>", unsafe_allow_html=True)
st.title("🗂️ SmartFileOrganizer")
st.markdown("<p class='subtitle'>Organize your files effortlessly with AI-powered categorization</p>", unsafe_allow_html=True)

# Action selector
action = st.radio(
    "Choose Your Action:",
    ["📁 Organize Folder", "↩️ Undo Last Operation", "⏰ Schedule Organization"]
)

#  Organize the Folder
if action == "📁 Organize Folder":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    folder_path = st.text_input("📂 Folder Path", placeholder="e.g., C:\\Users\\YourName\\Downloads")
    if folder_path and not os.path.exists(folder_path):
        st.warning("⚠️ Path does not exist!")
    elif folder_path and not os.path.isdir(folder_path):
        st.warning("⚠️ Not a directory!")

    start_button = st.button("🚀 Start Organization")

    if start_button and folder_path and os.path.isdir(folder_path):
        st.session_state.stats = {'moved':0,'skipped':0,'errors':0}
        st.session_state.logs = []

        progress_bar = st.progress(0)
        log_area = st.empty()

        try:
            for event in organize_directory(folder_path):
                done = event.get("done",0)
                total = event.get("total",1)
                progress_bar.progress(done/total)

                status = event["status"]
                if status=="moved":
                    log_line = f"✅ Moved {event['file']} → {event['category']}"
                    st.session_state.stats['moved'] +=1
                elif status=="skipped":
                    log_line = f"⚠️ Skipped {event['file']} ({event['reason']})"
                    st.session_state.stats['skipped'] +=1
                elif status=="error":
                    log_line = f"❌ Error {event.get('file','')}: {event.get('message','')}"
                    st.session_state.stats['errors'] +=1
                else:
                    log_line = str(event)

                st.session_state.logs.append(log_line)
                log_area.markdown("<div class='log-container'>" + "<br>".join(st.session_state.logs) + "</div>", unsafe_allow_html=True)

            st.balloons()
        except Exception as e:
            st.error(f"Error: {str(e)}")

    st.markdown("</div>", unsafe_allow_html=True)

# Undo Last Operation Done
elif action == "↩️ Undo Last Operation":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.info("ℹ This will restore all files from the last operation to their original locations.")
    undo_button = st.button("↩️ Undo Last Operation")
    if undo_button:
        try:
            success = undo_last_operation()
            if success:
                st.success("✅ Files restored successfully!")
                st.balloons()
            else:
                st.warning("⚠️ Nothing to undo.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    st.markdown("</div>", unsafe_allow_html=True)

# Schedule Organization
elif action == "⏰ Schedule Organization":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    sched_folder = st.text_input("📂 Folder to Schedule", placeholder="e.g., D:\\RandomFolders")
    if sched_folder and not os.path.exists(sched_folder):
        st.warning("Path does not exist!")
    elif sched_folder and not os.path.isdir(sched_folder):
        st.warning(" Not a directory!")

    # Manual HH:MM input
    new_time_str = st.text_input("Enter time to schedule (HH:MM)", "23:18", help="24-hour format HH:MM")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add Time"):
            try:
                new_time = datetime.strptime(new_time_str.strip(), "%H:%M").time()
                formatted_time = new_time.strftime("%H:%M")
                if formatted_time not in st.session_state.scheduled_times:
                    st.session_state.scheduled_times.append(formatted_time)
                    st.session_state.scheduled_times.sort()
                    st.success(f"✅ Added {formatted_time}")
                else:
                    st.warning("⚠️ Time already added!")
            except ValueError:
                st.error("❌ Invalid time format! Use HH:MM 24-hour format.")

    with col2:
        if st.button("🗑️ Clear All Times"):
            st.session_state.scheduled_times = []
            st.success("✅ All times cleared!")

    # Display scheduled times
    if st.session_state.scheduled_times:
        st.markdown("<div class='time-chip-container'>", unsafe_allow_html=True)
        times_html = "".join([f"<span class='time-chip'>🕒 {t}</span>" for t in st.session_state.scheduled_times])
        st.markdown(times_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Remove individual time
        time_to_remove = st.selectbox("Select time to remove:", options=st.session_state.scheduled_times)
        if st.button("🗑️ Remove Selected Time"):
            st.session_state.scheduled_times.remove(time_to_remove)
            st.success(f"✅ Removed {time_to_remove}")
            st.rerun()

    # Save schedule to JSON
    if st.button("💾 Save Schedule"):
        if not sched_folder or not os.path.isdir(sched_folder):
            st.error("❌ Invalid folder path!")
        elif not st.session_state.scheduled_times:
            st.warning("⚠️ No times added!")
        else:
            st.session_state.scheduled_job = {"folder": sched_folder, "times": st.session_state.scheduled_times}
            with open("scheduled_jobs.json", "w") as f:
                json.dump(st.session_state.scheduled_job, f, indent=2)
            st.success(f"✅ Scheduled {sched_folder} at {len(st.session_state.scheduled_times)} time(s)")
            st.balloons()
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div style='text-align:center;margin-top:2rem;color:#1f2937;font-size:0.9rem'>Made with ❤️ Infotact Solutions | SmartFileOrganizer v2.0</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
