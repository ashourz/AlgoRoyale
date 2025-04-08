import os
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, DirCreatedEvent, FileMovedEvent, DirMovedEvent

"""
mirror_watcher.py

👀 Watches ./src/algo_royale/ for new Python files or folders and mirrors them into ./tests/algo_royale/
📁 Creates mirrored test folders with __init__.py and matching test_<filename>.py
🔁 Handles file renames, folder moves, and file type changes (e.g. .txt → .py)
📝 Creates __init__.py files in new folders if they don't exist

📦 Usage:
    From the root of your project:
        python scripts/mirror_watcher.py
    or (with poetry):
        poetry run python scripts/mirror_watcher.py

🛑 To stop the watcher:
    Press Ctrl+C

🗂 Example Project Layout:
    your_project/
    ├── scripts/
    │   └── mirror_watcher.py
    ├── tests/
    └── src/
        └── module/
            └── example.py
"""

# Automatically detect project root and tests root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
WATCH_ROOT = PROJECT_ROOT / "src" / "algo_royale"
TESTS_ROOT = PROJECT_ROOT / "tests" / "algo_royale"

# Configure logger
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - [MIRROR] %(message)s',
    level=logging.INFO
)
logger = logging.getLogger()

def is_python_file(path: str) -> bool:
    return path.endswith(".py") and not os.path.basename(path).startswith("test_")

def relative_path(path: str) -> Path:
    return Path(os.path.relpath(path, WATCH_ROOT))


class CreateTestDirectory(FileSystemEventHandler):
    def on_created(self, event):
        logger.info(f"📂 Created: {event.src_path}")
        if isinstance(event, DirCreatedEvent):
            self.handle_directory(event.src_path)
        elif isinstance(event, FileCreatedEvent):
            self.handle_file(event.src_path)

    def on_moved(self, event):
        logger.info(f"🔀 Moved: {event.src_path} → {event.dest_path}")
        src_rel = relative_path(event.src_path)
        dest_rel = relative_path(event.dest_path)

        # Ignore moves involving the tests folder itself
        if "tests" in src_rel.parts or "tests" in dest_rel.parts:
            logger.info("⛔ Ignored: Move event involving 'tests' folder.")
            return

        # Handle directory renames/moves
        if isinstance(event, DirMovedEvent):
            test_src = TESTS_ROOT / src_rel
            test_dest = TESTS_ROOT / dest_rel
            if test_src.exists():
                test_src.rename(test_dest)
                logger.info(f"📁 Renamed test directory: {test_src} → {test_dest}")

        # Handle file renames/moves
        elif isinstance(event, FileMovedEvent):
            old_is_py = is_python_file(event.src_path)
            new_is_py = is_python_file(event.dest_path)

            old_stem = Path(event.src_path).stem
            new_stem = Path(event.dest_path).stem

            test_dir = TESTS_ROOT / dest_rel.parent
            old_test = test_dir / f"test_{old_stem}.py"
            new_test = test_dir / f"test_{new_stem}.py"

            os.makedirs(test_dir, exist_ok=True)

            if old_is_py and new_is_py:
                if old_test.exists():
                    old_test.rename(new_test)
                    print(f"🔁 Renamed test file: {old_test} → {new_test}")
                else:
                    self.create_test_for_file(event.dest_path)
            elif not old_is_py and new_is_py:
                self.create_test_for_file(event.dest_path)

    def on_modified(self, event):
        # Handle cases like renaming from .txt to .py
        logger.info(f"🔧 Modified: {event.src_path}")
        if event.is_directory:
            return
        if is_python_file(event.src_path):
            self.create_test_for_file(event.src_path)


    def handle_directory(self, path: str):
        logger.info(f"📁 Handling directory creation: {path}")
        rel = relative_path(path)
        if "tests" in rel.parts:
            logger.info(f"⚠️ Skipping 'tests' folder: {path}")
            return
        src_dir = WATCH_ROOT / rel
        test_dir = TESTS_ROOT / rel
        os.makedirs(test_dir, exist_ok=True)

        for p in [src_dir, test_dir]:
            init = p / "__init__.py"
            if not init.exists():
                logger.info(f"📝 Creating __init__.py in {p}")
                init.touch()

    def handle_file(self, path: str):
        logger.info(f"📄 Handling file creation: {path}")
        if not is_python_file(path):
            logger.info(f"❌ Skipping non-Python file: {path}")
            return
        self.create_test_for_file(path)

    def create_test_for_file(self, path: str):
        logger.info(f"🧪 Creating test file for: {path}")
        rel = relative_path(path)
        if "tests" in rel.parts:
            logger.info(f"⚠️ Skipping test file creation (already inside 'tests'): {path}")
            return

        dir_rel = rel.parent
        file_stem = Path(path).stem
        test_file_name = f"test_{file_stem}.py"
        test_dir = TESTS_ROOT / dir_rel
        test_file = test_dir / test_file_name

        os.makedirs(test_dir, exist_ok=True)

        # Create __init__.py if needed
        init = test_dir / "__init__.py"
        if not init.exists():
            logger.info(f"📝 Creating __init__.py in {test_dir}")
            init.touch()

        if not test_file.exists():
            with open(test_file, "w") as f:
                logger.info(f"🖊 Writing test file: {test_file}")
                f.write(f"# tests for {rel}\n")


def start_watcher():
    logger.info("👀 Watching for file and folder changes... Press Ctrl+C to stop.")
    observer = Observer()
    handler = CreateTestDirectory()
    observer.schedule(handler, str(WATCH_ROOT), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    start_watcher()