from abc import ABC, abstractmethod


class StageCoordinator(ABC):
    @abstractmethod
    async def run(self) -> bool:
        """
        Orchestrate the stage: load, prepare, process, write.
        """
        pass
