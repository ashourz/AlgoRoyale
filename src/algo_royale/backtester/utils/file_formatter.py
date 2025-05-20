import shutil
from pathlib import Path
from typing import Union, List
from enum import Enum

from algo_royale.backtester.pipeline.enums.data_extension import DataExtension
from algo_royale.backtester.pipeline.enums.pipeline_stage import PipelineStage
from algo_royale.utils.path_utils import get_project_root


class FileFormatter:
    def __init__(self):
        self.base_dir = get_project_root()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_stage_path(self, stage: PipelineStage) -> Path:
        path = self.base_dir / stage.value / "data"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write_unprocessed_file(self, stage: PipelineStage, filename: str, content: str) -> Path:
        stage_path = self.get_stage_path(stage)
        file_path = stage_path / f"{filename}{DataExtension.UNPROCESSED}"
        with open(file_path, "w") as f:
            f.write(content)
        return file_path

    def mark_processing(self, file_path: Path) -> Path:
        if file_path.suffix != DataExtension.UNPROCESSED:
            raise ValueError(f"Expected a {DataExtension.UNPROCESSED} file.")
        processing_path = file_path.with_suffix(DataExtension.PROCESSING)
        file_path.rename(processing_path)
        return processing_path

    def mark_processed(self, file_path: Path) -> Path:
        if file_path.suffix != DataExtension.PROCESSING:
            raise ValueError(f"Expected a {DataExtension.PROCESSING} file.")
        processed_path = file_path.with_suffix(DataExtension.PROCESSED)
        file_path.rename(processed_path)
        return processed_path

    def mark_done(self, stage: PipelineStage):
        done_file = self.get_stage_path(stage).parent / f"{stage.value}{DataExtension.DONE}"
        done_file.touch()

    def is_done(self, stage: PipelineStage) -> bool:
        done_file = self.get_stage_path(stage).parent / f"{stage.value}{DataExtension.DONE}"
        return done_file.exists()

    def list_files_by_extension(self, stage: PipelineStage, extension: DataExtension) -> List[Path]:
        return list(self.get_stage_path(stage).glob(f"*{extension}"))

    def copy_to_next_stage(self, current_stage: PipelineStage, next_stage: PipelineStage):
        current_path = self.get_stage_path(current_stage)
        next_path = self.get_stage_path(next_stage)
        for file in current_path.glob(f"*{DataExtension.PROCESSED}"):
            destination = next_path / file.name.replace(DataExtension.PROCESSED, DataExtension.UNPROCESSED)
            shutil.copy(file, destination)
