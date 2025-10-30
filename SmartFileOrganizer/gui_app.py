import streamlit as st
import os
from file_organizer import organize_directory
from history_store import undo_last_operation
from datetime import datetime
import json
import plotly.express as px
import plotly.graph_objects as go
from analytics import *
from scanner import FolderScanner, deep_scan

# Page configuration
st.set_page_config(
    page_title="SmartFileOrganizer",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

#  CSS styling animated cards
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

* { 
    font-family: 'Poppins', sans-serif; 
}

.stApp { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
}

.css-1d391kg { 
    padding-top: 0rem; 
    margin-top: 0rem; 
}

.main-container {
    background: white;
    border-radius: 20px;
    padding: 2rem;
    margin: 2rem auto;
    max-width: 1200px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
}

h1 {
    font-size: 3rem;
    font-weight: 700;
    color: white;
    text-align: center;
    margin-bottom: 0.3rem;
    animation: fadeInDown 0.8s ease-out;
    -webkit-background-clip: unset;
    -webkit-text-fill-color: unset;
}

.subtitle { 
    text-align: center; 
    font-weight: 400; 
    font-size: 1.2rem; 
    color: white;
    margin-bottom: 3rem;
    animation: fadeIn 1s ease-out;
}

/* Glowing Card Grid */
.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1.5rem;
    margin: 3rem 0;
    padding: 1rem;
}

.option-card {
    background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
    border-radius: 20px;
    padding: 2rem 1.5rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    border: 2px solid transparent;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

.option-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    opacity: 0;
    transition: opacity 0.4s ease;
    border-radius: 20px;
    z-index: 0;
}

.option-card:hover::before {
    opacity: 0.1;
}

.option-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
    border: 2px solid #667eea;
}

.card-icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    position: relative;
    z-index: 1;
    animation: float 3s ease-in-out infinite;
    display: inline-block;
}

.option-card:hover .card-icon {
    animation: bounce 0.6s ease;
}

.card-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 0.5rem;
    position: relative;
    z-index: 1;
    transition: color 0.3s ease;
}

.option-card:hover .card-title {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.card-description {
    font-size: 0.9rem;
    color: #6b7280;
    position: relative;
    z-index: 1;
    line-height: 1.5;
}

/* Stats Cards */
.stat-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 15px;
    padding: 1.5rem;
    color: white;
    text-align: center;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    transition: transform 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
}

.stat-value {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.stat-label {
    font-size: 1rem;
    opacity: 0.9;
}

/* Animations */
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    25% { transform: translateY(-15px); }
    50% { transform: translateY(-7px); }
    75% { transform: translateY(-10px); }
}

@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes glow {
    0%, 100% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.3); }
    50% { box-shadow: 0 0 40px rgba(102, 126, 234, 0.6); }
}

/* Button Styles */
.stButton>button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
    padding: 0.7rem 2rem;
    font-weight: 600;
    width: 100%;
    border: none;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* Content Card */
.content-card {
    background: #f9fafb;
    border-radius: 20px;
    padding: 2rem;
    margin: 2rem 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    animation: fadeIn 0.5s ease-out;
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
    box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.time-chip-container {
    background: #f9fafb;
    padding: 1rem;
    border-radius: 15px;
    margin: 1rem 0;
    min-height: 60px;
    border: 2px dashed #e5e7eb;
}

.file-item {
    background: white;
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 10px;
    border-left: 4px solid #667eea;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

input[type="time"] {
    pointer-events: auto !important;
    font-size: 1rem;
    padding: 0.5rem;
}

.back-button {
    display: inline-block;
    margin-bottom: 1rem;
    color: #667eea;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.back-button:hover {
    color: #764ba2;
    transform: translateX(-5px);
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
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'home'
if 'scan_results' not in st.session_state:
    st.session_state.scan_results = None

# Main container
st.markdown("<div class='main-container'>", unsafe_allow_html=True)

# Header
st.title("🗂️ SmartFileOrganizer")
st.markdown("<p class='subtitle'>Organize your files effortlessly with intelligent automation</p>", unsafe_allow_html=True)

# HOME VIEW - Card Selection
if st.session_state.current_view == 'home':
    st.markdown("""
    <div class='card-grid'>
        <div class='option-card'>
            <div class='card-icon'>📁</div>
            <div class='card-title'>Organize Folder</div>
            <div class='card-description'>Automatically sort files by type</div>
        </div>
        <div class='option-card'>
            <div class='card-icon'>🔍</div>
            <div class='card-title'>Scan Folder</div>
            <div class='card-description'>Analyze folder contents deeply</div>
        </div>
        <div class='option-card'>
            <div class='card-icon'>↩️</div>
            <div class='card-title'>Undo Operation</div>
            <div class='card-description'>Restore to original state</div>
        </div>
        <div class='option-card'>
            <div class='card-icon'>⏰</div>
            <div class='card-title'>Schedule Tasks</div>
            <div class='card-description'>Automate at specific times</div>
        </div>
        <div class='option-card'>
            <div class='card-icon'>📊</div>
            <div class='card-title'>Analytics</div>
            <div class='card-description'>View insights & statistics</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Card click handlers using columns
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("📁 Organize", key="btn_organize", use_container_width=True):
            st.session_state.current_view = 'organize'
            st.rerun()
    with col2:
        if st.button("🔍 Scan", key="btn_scan", use_container_width=True):
            st.session_state.current_view = 'scan'
            st.rerun()
    with col3:
        if st.button("↩️ Undo", key="btn_undo", use_container_width=True):
            st.session_state.current_view = 'undo'
            st.rerun()
    with col4:
        if st.button("⏰ Schedule", key="btn_schedule", use_container_width=True):
            st.session_state.current_view = 'schedule'
            st.rerun()
    with col5:
        if st.button("📊 Analytics", key="btn_dashboard", use_container_width=True):
            st.session_state.current_view = 'dashboard'
            st.rerun()

# ORGANIZE VIEW
elif st.session_state.current_view == 'organize':
    if st.button("← Back to Home", key="back_organize"):
        st.session_state.current_view = 'home'
        st.rerun()
    
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("### 📁 Organize Folder")
    
    folder_path = st.text_input(" Folder Path", placeholder="e.g., C:\\Users\\YourName\\Downloads")

    if folder_path and not os.path.exists(folder_path):
        st.warning(" Path does not exist!")
    elif folder_path and not os.path.isdir(folder_path):
        st.warning(" Not a directory!")

    start_button = st.button(" Start Organization", key="start_org")

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
                    log_line = f" Moved {event['file']} → {event['category']}"
                    st.session_state.stats['moved'] +=1
                elif status=="skipped":
                    log_line = f" Skipped {event['file']} ({event['reason']})"
                    st.session_state.stats['skipped'] +=1
                elif status=="error":
                    log_line = f" Error {event.get('file','')}: {event.get('message','')}"
                    st.session_state.stats['errors'] +=1
                else:
                    log_line = str(event)

                st.session_state.logs.append(log_line)
                log_area.markdown("<div class='log-container'>" + "<br>".join(st.session_state.logs) + "</div>", unsafe_allow_html=True)

            st.balloons()
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# SCAN VIEW
elif st.session_state.current_view == 'scan':
    if st.button("← Back to Home", key="back_scan"):
        st.session_state.current_view = 'home'
        st.rerun()
    
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("### Deep Folder Scan")
    
    scan_folder = st.text_input(" Folder Path to Scan", placeholder="e.g., C:\\Users\\YourName\\Documents")

    if scan_folder and not os.path.exists(scan_folder):
        st.warning("Path does not exist!")
    elif scan_folder and not os.path.isdir(scan_folder):
        st.warning(" Not a directory!")

    col1, col2 = st.columns(2)
    with col1:
        scan_button = st.button(" Start Scan", key="start_scan", use_container_width=True)
    with col2:
        if st.session_state.scan_results:
            export_button = st.button("Export Results", key="export_scan", use_container_width=True)

    if scan_button and scan_folder and os.path.isdir(scan_folder):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(event):
            if event['status'] == 'scanning':
                progress = event['current'] / event['total']
                progress_bar.progress(progress)
                status_text.text(f"Scanning: {event['item']} ({event['current']}/{event['total']})")
        
        with st.spinner("Scanning folder..."):
            scanner = FolderScanner(scan_folder)
            results = scanner.scan(progress_callback)
            st.session_state.scan_results = results
        
        st.success(f" Scan completed in {results['scan_time']:.2f} seconds!")
        st.balloons()
    
    # Display results
    if st.session_state.scan_results:
        results = st.session_state.scan_results
        
        st.markdown("---")
        st.markdown("### Scan Results")
        
        # Quick Stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-value'>{results['total_files']:,}</div>
                <div class='stat-label'> Total Files</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-value'>{results['total_folders']:,}</div>
                <div class='stat-label'> Folders</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            scanner = FolderScanner(scan_folder)
            st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-value'>{scanner.format_size(results['total_size'])}</div>
                <div class='stat-label'> Total Size</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-value'>{len(results['file_types'])}</div>
                <div class='stat-label'> File Types</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Tabs for different views 
        tab1, tab2, tab3, tab4 = st.tabs([" Largest Files", " Duplicates", " Timeline", " Issues"])
        
        with tab1:
            st.markdown("#### Largest Files")
            if results['largest_files']:
                for idx, file in enumerate(results['largest_files'][:15], 1):
                    st.markdown(f"""
                    <div class='file-item'>
                        <strong>{idx}. {file['name']}</strong><br>
                         Size: {file['size_formatted']} |  Category: {file['category']}<br>
                         Path: <code>{file['path']}</code>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No files found.")
        
        with tab2:
            st.markdown("#### Potential Duplicates (by size)")
            if results['duplicate_candidates']:
                st.info(f"Found {len(results['duplicate_candidates'])} groups of files with identical sizes")
                for idx, dup_group in enumerate(results['duplicate_candidates'][:10], 1):
                    with st.expander(f"Group {idx}: {dup_group['count']} files of {dup_group['size_formatted']}"):
                        for file_path in dup_group['files']:
                            st.text(f" {file_path}")
            else:
                st.success("No duplicate candidates found!")
        
        with tab3:
            col_old, col_new = st.columns(2)
            
            with col_old:
                st.markdown("#### Oldest Files")
                if results['oldest_files']:
                    for file in results['oldest_files']:
                        modified_str = file['modified'].strftime('%Y-%m-%d %H:%M:%S')
                        st.markdown(f"- **{file['name']}**  \n  {modified_str}")
                else:
                    st.info("No files found.")
            
            with col_new:
                st.markdown("#### Newest Files")
                if results['newest_files']:
                    for file in results['newest_files']:
                        modified_str = file['modified'].strftime('%Y-%m-%d %H:%M:%S')
                        st.markdown(f"- **{file['name']}**  \n  {modified_str}")
                else:
                    st.info("No files found.")
        
        with tab4:
            if results['empty_folders']:
                st.warning(f"Found {len(results['empty_folders'])} empty folders")
                with st.expander("View empty folders"):
                    for folder in results['empty_folders']:
                        st.text(f" {folder}")
            else:
                st.success("No empty folders found!")
            
            if results['hidden_files'] > 0:
                st.info(f" Found {results['hidden_files']} hidden files")
            else:
                st.info(" No hidden files found")
            
            if results['errors']:
                st.error(f" Encountered {len(results['errors'])} errors during scan")
                with st.expander("View errors"):
                    for error in results['errors']:
                        st.text(error)
            else:
                st.success(" No errors encountered!")
    
    # Export functionality
    if st.session_state.scan_results and 'export_button' in locals() and export_button:
        scanner = FolderScanner(scan_folder)
        scanner.scan_results = st.session_state.scan_results
        success, message = scanner.export_results('scan_results.json')
        if success:
            st.success(f" Results exported to {message}")
            with open(message, 'r') as f:
                st.download_button(
                    label="Download JSON",
                    data=f.read(),
                    file_name="scan_results.json",
                    mime="application/json"
                )
        else:
            st.error(f"Export failed: {message}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# UNDO VIEW
elif st.session_state.current_view == 'undo':
    if st.button("← Back to Home", key="back_undo"):
        st.session_state.current_view = 'home'
        st.rerun()
    
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("### ↩ Undo Last Operation")
    st.info("ℹ This will restore all files from the last operation to their original locations.")
    
    undo_button = st.button("↩Undo Last Operation", key="undo_btn")
    if undo_button:
        try:
            success = undo_last_operation()
            if success:
                st.success(" Files restored successfully!")
                st.balloons()
            else:
                st.warning(" Nothing to undo.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# SCHEDULE VIEW - Replace this section in your app.py
elif st.session_state.current_view == 'schedule':
    if st.button("← Back to Home", key="back_schedule"):
        st.session_state.current_view = 'home'
        st.rerun()
    
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("### Schedule Organization")
    
    # Instructions
    st.info("""
     **How to use:**
    1. Enter folder path and times below
    2. Click 'Save Schedule'
    3. Run `python run_scheduled.py` in terminal
    4. Keep the terminal open - your schedule is running!
    """)
    
    # Configuration
    sched_folder = st.text_input(" Folder to Schedule", placeholder="e.g., D:\\TestFiles")

    if sched_folder and not os.path.exists(sched_folder):
        st.warning(" Path does not exist!")
    elif sched_folder and not os.path.isdir(sched_folder):
        st.warning(" Not a directory!")

    new_time_str = st.text_input("Enter time (HH:MM format)", "09:00", help="24-hour format like 09:00, 18:30")

    col1, col2 = st.columns(2)
    with col1:
        if st.button(" Add Time"):
            try:
                new_time = datetime.strptime(new_time_str.strip(), "%H:%M").time()
                formatted_time = new_time.strftime("%H:%M")
                if formatted_time not in st.session_state.scheduled_times:
                    st.session_state.scheduled_times.append(formatted_time)
                    st.session_state.scheduled_times.sort()
                    st.success(f" Added {formatted_time}")
                else:
                    st.warning(" Time already added!")
            except ValueError:
                st.error(" Invalid time! Use format like 09:00 or 18:30")

    with col2:
        if st.button("🗑️ Clear All"):
            st.session_state.scheduled_times = []
            st.success(" Cleared!")

    # Show scheduled times
    if st.session_state.scheduled_times:
        st.markdown("<div class='time-chip-container'>", unsafe_allow_html=True)
        times_html = "".join([f"<span class='time-chip'>🕒 {t}</span>" for t in st.session_state.scheduled_times])
        st.markdown(times_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        time_to_remove = st.selectbox("Remove a time:", options=st.session_state.scheduled_times)
        if st.button("🗑️ Remove"):
            st.session_state.scheduled_times.remove(time_to_remove)
            st.success(f"Removed {time_to_remove}")
            st.rerun()

    # Save button
    if st.button("Save Schedule", type="primary"):
        if not sched_folder or not os.path.isdir(sched_folder):
            st.error(" Please enter a valid folder path!")
        elif not st.session_state.scheduled_times:
            st.warning(" Please add at least one time!")
        else:
            st.session_state.scheduled_job = {
                "folder": sched_folder, 
                "times": st.session_state.scheduled_times
            }
            with open("scheduled_jobs.json", "w") as f:
                json.dump(st.session_state.scheduled_job, f, indent=2)
            
            st.success(" Schedule saved successfully!")
            st.balloons()
            
            # Show next steps
            st.markdown("---")
            st.markdown("###  Next Step: Start the Scheduler")
            st.code("python run_scheduled.py", language="bash")
            st.markdown("Run this command in your terminal to start scheduling!")
    
    # Show current schedule if exists
    if os.path.exists("scheduled_jobs.json"):
        st.markdown("---")
        st.markdown("### Current Schedule")
        try:
            with open("scheduled_jobs.json", "r") as f:
                current_schedule = json.load(f)
            
            st.markdown(f"**Folder:** `{current_schedule.get('folder', 'Not set')}`")
            st.markdown(f"**Times:** {', '.join(current_schedule.get('times', []))}")
        except:
            st.error("Error reading schedule file")
    
    st.markdown("</div>", unsafe_allow_html=True)

# DASHBOARD VIEW
elif st.session_state.current_view == 'dashboard':
    if st.button("← Back to Home", key="back_dashboard"):
        st.session_state.current_view = 'home'
        st.rerun()
    
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("### File Intelligence Dashboard")

    folder = st.text_input("Enter folder path to analyze:")
    if folder and os.path.exists(folder):
        df = scan_directory(folder)
        st.success(f"Analyzed {len(df)} files.")

        # File Type Distribution
        st.subheader(" File Type Distribution")
        file_type_data = get_file_type_distribution(df)
        fig = px.pie(values=file_type_data.values, names=file_type_data.index, title="File Type Distribution")
        st.plotly_chart(fig, use_container_width=True)

        # Folder Size Distribution
        st.subheader("Folder Size Overview (MB)")
        folder_sizes = get_folder_size_distribution(df)
        fig2 = px.bar(x=folder_sizes.index[:10], y=folder_sizes.values[:10], title="Top 10 Largest Folders")
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div style='text-align:center;margin-top:3rem;color:white;font-size:0.9rem;padding:1rem 0'>Made with ❤️ Infotact Solutions | SmartFileOrganizer</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)