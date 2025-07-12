import os
import re

IMPORT_LINE = "from algo_royale.logging.loggable import Loggable\n"


def file_needs_import(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    # Check if Loggable is used anywhere in the file
    if "Loggable" not in content:
        return False
    # Check if import already exists
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


def main(root_dir="."):
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(subdir, file)
                if file_needs_import(path):
                    print(f"Adding import to: {path}")
                    add_import(path)


if __name__ == "__main__":
    main("path/to/your/codebase")
