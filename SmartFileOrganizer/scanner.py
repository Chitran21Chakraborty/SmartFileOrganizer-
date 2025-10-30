# scanner.py
import os
import time
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime


class FolderScanner:
    def __init__(self, folder_path):
        self.folder_path = Path(folder_path)
        self.scan_results = None

    def format_size(self, size_bytes):
        """Convert bytes to human-readable format."""
        for unit in ['B','KB','MB','GB','TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} PB"

    def scan(self, progress_callback=None):
        """Deep scan folder and collect stats."""
        start_time = time.time()
        total_files = 0
        total_folders = 0
        total_size = 0
        file_types = defaultdict(int)
        categories = defaultdict(lambda: {"count": 0, "size": 0})
        largest_files = []
        oldest_files = []
        newest_files = []
        empty_folders = []
        hidden_files = 0
        errors = []
        duplicate_candidates = defaultdict(list)

        all_items = list(self.folder_path.rglob('*'))
        total_items = len(all_items)

        for idx, item in enumerate(all_items, 1):
            try:
                if item.is_file():
                    total_files += 1
                    size = item.stat().st_size
                    total_size += size
                    ext = item.suffix.lower() if item.suffix else "no_ext"
                    file_types[ext] += 1

                    # categorize files by extension type
                    cat_name = ext.strip('.') if ext != "no_ext" else "other"
                    categories[cat_name]["count"] += 1
                    categories[cat_name]["size"] += size

                    # track largest files
                    largest_files.append({
                        "name": item.name,
                        "size": size,
                        "size_formatted": self.format_size(size),
                        "path": str(item),
                        "category": cat_name
                    })

                    # track duplicates by size
                    duplicate_candidates[size].append(str(item))

                    # track oldest/newest - FIXED: Convert to datetime object
                    mtime = item.stat().st_mtime
                    modified_datetime = datetime.fromtimestamp(mtime)
                    
                    oldest_files.append({
                        "name": item.name, 
                        "modified": modified_datetime,
                        "timestamp": mtime  # Keep timestamp for sorting
                    })
                    newest_files.append({
                        "name": item.name, 
                        "modified": modified_datetime,
                        "timestamp": mtime  # Keep timestamp for sorting
                    })

                    # hidden file
                    if item.name.startswith('.') or item.name.startswith('~'):
                        hidden_files += 1

                elif item.is_dir():
                    total_folders += 1
                    if not any(item.iterdir()):
                        empty_folders.append(str(item))
                
                # progress callback
                if progress_callback:
                    progress_callback({
                        "status": "scanning", 
                        "current": idx, 
                        "total": total_items, 
                        "item": str(item.name)
                    })

            except Exception as e:
                errors.append(f"{str(item)}: {str(e)}")

        # post-process - Sort by timestamp
        largest_files.sort(key=lambda x: x["size"], reverse=True)
        oldest_files.sort(key=lambda x: x["timestamp"])
        newest_files.sort(key=lambda x: x["timestamp"], reverse=True)
        
        duplicate_candidates = [
            {
                "size": k, 
                "size_formatted": self.format_size(k), 
                "count": len(v), 
                "files": v
            }
            for k, v in duplicate_candidates.items() if len(v) > 1
        ]

        end_time = time.time()
        self.scan_results = {
            "total_files": total_files,
            "total_folders": total_folders,
            "total_size": total_size,
            "file_types": dict(file_types),
            "categories": dict(categories),
            "largest_files": largest_files,
            "oldest_files": oldest_files[:10],
            "newest_files": newest_files[:10],
            "empty_folders": empty_folders,
            "hidden_files": hidden_files,
            "errors": errors,
            "duplicate_candidates": duplicate_candidates,
            "scan_time": end_time - start_time
        }
        return self.scan_results

    def export_results(self, filename="scan_results.json"):
        """Export scan results to a JSON file."""
        if not self.scan_results:
            return False, "No scan results to export!"
        try:
            # Convert datetime objects to strings for JSON serialization
            export_data = self.scan_results.copy()
            
            # Convert datetime in oldest/newest files
            for file_list in ['oldest_files', 'newest_files']:
                for file_info in export_data[file_list]:
                    if isinstance(file_info.get('modified'), datetime):
                        file_info['modified'] = file_info['modified'].isoformat()
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, default=str)
            return True, filename
        except Exception as e:
            return False, str(e)


def deep_scan(folder_path, progress_callback=None):
    """Helper function for quick usage without creating FolderScanner instance."""
    scanner = FolderScanner(folder_path)
    return scanner.scan(progress_callback)