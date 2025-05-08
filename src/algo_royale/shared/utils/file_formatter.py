import os
import shutil
from pathlib import Path
from typing import Union
import uuid

class FileFormatter:
    def __init__(self, base_dir: Union[str, Path]):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_stage_path(self, stage_name: str) -> Path:
        path = self.base_dir / stage_name / "data"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write_temp_file(self, stage: str, filename: str, content: str):
        stage_path = self.get_stage_path(stage)
        temp_file = stage_path / f"{filename}.writing"
        with open(temp_file, "w") as f:
            f.write(content)
        final_file = temp_file.with_suffix('.csv')
        temp_file.rename(final_file)
        return final_file

    def mark_processing(self, file_path: Path) -> Path:
        if file_path.suffix == ".csv":
            processing_path = file_path.with_suffix(".processing")
            file_path.rename(processing_path)
            return processing_path
        raise ValueError("File must be a .csv before processing")

    def mark_done(self, stage: str):
        done_file = self.get_stage_path(stage).parent / f"{stage}.done"
        done_file.touch()

    def copy_to_next_stage(self, current_stage: str, next_stage: str):
        current_path = self.get_stage_path(current_stage)
        next_path = self.get_stage_path(next_stage)
        for file in current_path.glob("*.csv"):
            shutil.copy(file, next_path / file.name)

    def is_done(self, stage: str) -> bool:
        return (self.get_stage_path(stage).parent / f"{stage}.done").exists()

    def list_csv_files(self, stage: str):
        return list(self.get_stage_path(stage).glob("*.csv"))
