"""
Regenerate config/schema.json from the ConfigFile Pydantic model.

  uv run python scripts/generate_config_schema.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.common.config import ConfigFile

ROOT = Path(__file__).parent.parent
schema_path = ROOT / "config" / "schema.json"
schema_path.write_text(json.dumps(ConfigFile.model_json_schema(), indent=2) + "\n")
print(f"Written {schema_path}")
