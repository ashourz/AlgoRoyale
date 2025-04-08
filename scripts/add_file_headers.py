import time
import os
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Automatically detect project root and tests root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
WATCH_ROOT = PROJECT_ROOT / "src" / "algo_royale"

# Configure logger
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - [HEADER] %(message)s',
    level=logging.INFO
)
logger = logging.getLogger()

class AddFileHeaders(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        logger.info(f"📄 File modified: {event.src_path}")
        self.update_file_header(event.src_path)

    def on_created(self, event):
        if event.is_directory:
            return
        logger.info(f"🆕 File created: {event.src_path}")
        self.update_file_header(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return
        logger.info(f"🔀 File moved from {event.src_path} to {event.dest_path}")
        # Update the header for the new file location after move
        self.update_file_header(event.dest_path)

    def update_file_header(self, file_path):
        # Calculate the relative path from the WATCH_ROOT to the file
        relative_path = Path(file_path).relative_to(WATCH_ROOT)

        # Generate appropriate header based on file type
        if file_path.endswith(".py"):
            required_header = f"## {relative_path}\n"  # Python files get ## as the comment prefix
        elif file_path.endswith(".sql"):
            required_header = f"-- {relative_path}\n"  # SQL files get -- as the comment prefix
        else:
            return  # If it's neither .py nor .sql, no header will be added

        try:
            with open(file_path, 'r+') as file:
                lines = file.readlines()

                # Check if the first line starts with a comment
                if lines and lines[0].startswith("#") or lines[0].startswith("--"):
                    # If the first line is a comment, we can replace it with the correct header
                    if lines[0] != required_header:
                        lines[0] = required_header
                        file.seek(0)
                        file.writelines(lines)
                        logger.info(f"✅ Header added or updated for {file_path}")
                    else:
                        logger.info(f"🔑 Header already correct for {file_path}")
                else:
                    logger.info(f"⚠️ First line is not a comment, skipping header update for {file_path}")
                    
        except Exception as e:
            logger.error(f"❌ Failed to update header for {file_path}: {e}")

def start_watcher():
    path = WATCH_ROOT  # Set the directory you want to watch (can also set a subdirectory)
    event_handler = AddFileHeaders()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    
    logger.info("🔍 Watching for file changes... Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("🛑 Stopping the watcher...")

    observer.join()
    logger.info("🛑 Watcher stopped.")
    
if __name__ == "__main__":
    start_watcher()
