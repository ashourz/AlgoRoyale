import os
import re
import sys

IMPORT_LINE = "from algo_royale.logging.loggable import Loggable\n"


def file_needs_import(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping non-UTF8 file: {path}")
        return False

    if "Loggable" not in content:
        return False
    if re.search(r"from\s+algo_royale\.logging\.loggable\s+import\s+Loggable", content):
        return False
    return True


def add_import(path):
    with open(path, "r+", encoding="utf-8") as f:
        lines = f.readlines()
        # Find the last import line index
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith("import") or line.startswith("from"):
                insert_pos = i + 1
            # Also skip shebang and encoding lines if present
            elif line.startswith("#!") or line.startswith("# -*- coding:"):
                insert_pos = i + 1
            else:
                break
        lines.insert(insert_pos, IMPORT_LINE)
        f.seek(0)
        f.writelines(lines)
        f.truncate()


ALLOWED_DIRS = {"src", "tests"}


def main():
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    root_dir = os.path.abspath(root_dir)
    for subdir, _, files in os.walk(root_dir):
        # Normalize path to relative for checking
        rel_subdir = os.path.relpath(subdir, root_dir)
        # Skip if not in allowed dirs or their subdirs
        if not any(
            rel_subdir == d or rel_subdir.startswith(d + os.sep) for d in ALLOWED_DIRS
        ):
            continue
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(subdir, file)
                if file_needs_import(path):
                    print(f"Adding import to: {path}")
                    add_import(path)


if __name__ == "__main__":
    main("path/to/your/codebase")
