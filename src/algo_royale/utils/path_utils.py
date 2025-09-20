from pathlib import Path


def get_project_root() -> Path:
    """Find the project root by searching for pyproject.toml upwards."""
    current = Path(__file__).absolute()  # Start from this file's location
    while True:
        if (current / "pyproject.toml").exists():
            return current
        if current.parent == current:  # Reached filesystem root
            raise FileNotFoundError(
                "Could not find pyproject.toml in any parent directory!"
            )
        current = current.parent  # Go up one level
