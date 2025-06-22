import logging


class PipelineStage:
    def __init__(
        self, 
        logger: logging.Logger, 
        stage_name: str=None, 
        suppress: bool=True
    ) -> None:
        self.stage_name = stage_name
        self.suppress = suppress
        self.logger = logger

    def __enter__(self):
        # Optionally log entering the stage
        self.logger.info(f"Entering stage: {self.stage_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.logger.exception(f"Exception in stage '{self.stage_name}'")
            if self.suppress:
                return True  # suppresses the exception
        self.logger.info(f"Stage {self.stage_name} finished successfullly")
        return False  