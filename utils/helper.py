import os
from pathlib import Path

from algo_royale.logging.logger_env import LoggerEnv
from algo_royale.logging.logger_factory import LoggerType

logger = LoggerFactory.get_logger(LoggerType.TRADING, LoggerEnv.PROD)


def find_project_root(starting_directory, target_folder_name="AlgoRoyale"):
    """Keep going up one level until we find the target folder (AlgoRoyale)."""
    current_dir = Path(starting_directory).resolve()

    while current_dir.name != target_folder_name:
        current_dir = current_dir.parent
        if current_dir == current_dir.parent:
            return None
    return current_dir


def add_init_files(directory):
    """Recursively add __init__.py to all subdirectories."""
    for dirpath, dirnames, filenames in os.walk(directory):
        init_file_path = os.path.join(dirpath, "__init__.py")

        if "__init__.py" not in filenames:
            # Create the __init__.py file if it doesn't exist
            with open(init_file_path, "w") as init_file:
                init_file.write("# This is an init file for the directory: " + dirpath)
            logger.info(f"Created __init__.py in {dirpath}")
        else:
            # If the file exists, you can choose what to do.
            logger.info(f"__init__.py already exists in {dirpath}")
            # Optionally, you could overwrite or append if needed:
            # with open(init_file_path, 'a') as init_file:  # To append something
            #     init_file.write("\n# This is an additional comment for the existing file.")
            # print(f"Appended to __init__.py in {dirpath}")

            # with open(init_file_path, 'w') as init_file: # to overwrite something
            # init_file.write("# Overwritten content or new log for this directory")
            # print(f"Overwritten __init__.py in {dirpath}")


def main():
    # Find the project root directory (AlgoRoyale)
    script_dir = Path(__file__).resolve().parent
    project_root = find_project_root(script_dir)

    if project_root:
        logger.info(f"Project root found at: {project_root}")
        # Add __init__.py files in all subdirectories of the project root
        add_init_files(project_root)
    else:
        logger.info("Project root not found.")


if __name__ == "__main__":
    main()
