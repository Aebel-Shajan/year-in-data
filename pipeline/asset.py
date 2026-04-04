from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class Model:
    fn: Callable
    tag: str
    input_key: str
    output_key: str
    unit: str = ""
    label: str = ""
