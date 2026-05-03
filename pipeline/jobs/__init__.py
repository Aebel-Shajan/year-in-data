from typing import Protocol

from pipeline.common.config import PipelineConfig
from pipeline.common.r2 import R2Client


class JobFn(Protocol):
    def __call__(self, r2: R2Client, config: PipelineConfig) -> None: ...
