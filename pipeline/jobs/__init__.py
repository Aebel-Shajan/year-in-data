from typing import Protocol

from pipeline.config import PipelineConfig
from pipeline.r2 import R2Client


class JobFn(Protocol):
    def __call__(self, r2: R2Client, config: PipelineConfig) -> None: ...
