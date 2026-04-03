"""
Pipeline stage orchestration.

Stages run in order: bronze → silver → gold

  bronze — jobs fetch raw data → inbox, then bronze models archive inbox → bronze store
  silver — parse archived bronze → silver Parquet
  gold   — aggregate silver → gold Parquet + web JSON
"""

from __future__ import annotations

import importlib
import pkgutil
import traceback
from datetime import date
from types import ModuleType

import pipeline.models.bronze as _bronze_pkg  # type: ignore[import-untyped]
import pipeline.models.gold as _gold_pkg  # type: ignore[import-untyped]
import pipeline.models.silver as _silver_pkg  # type: ignore[import-untyped]
from pipeline import r2 as R2
from pipeline.config import Config, Secrets
from pipeline.r2 import R2Client


def run_bronze(r2: R2Client, secrets: Secrets, config: Config) -> list[str]:
    """Run all bronze models (fetch/collect → inbox → archive)."""
    bronze_mods = _discover(_bronze_pkg)
    return _run([
        (name, lambda m=mod: getattr(m, "materialize")(r2, secrets=secrets, config=config))
        for name, mod in bronze_mods
        if _source_enabled(getattr(mod, "SOURCE", None), config)
    ])


def run_silver(
    r2: R2Client,
    config: Config,
    start: date | None = None,
    end: date | None = None,
) -> list[str]:
    """Run all silver models, reading from archived bronze files."""
    silver_mods = _discover(_silver_pkg)
    return _run([
        (name, lambda m=mod: getattr(m, "materialize")(r2, start=start, end=end))
        for name, mod in silver_mods
    ])


def run_gold(
    r2: R2Client,
    start: date | None = None,
    end: date | None = None,
    dry_run: bool = False,
) -> list[str]:
    """Run all gold models."""
    gold_mods = _discover(_gold_pkg)
    return _run([
        (name, lambda m=mod: getattr(m, "materialize")(r2, start=start, end=end, dry_run=dry_run))
        for name, mod in gold_mods
    ])


# ── Internal helpers ──────────────────────────────────────────────────────────

def _discover(pkg: ModuleType) -> list[tuple[str, ModuleType]]:
    """Return (name, module) for every non-private module in a package."""
    return [
        (name, importlib.import_module(f"{pkg.__name__}.{name}"))
        for _, name, _ in pkgutil.iter_modules(pkg.__path__)
        if not name.startswith("_")
    ]


def _source_enabled(source: str | None, config: Config) -> bool:
    if source is None:
        return True
    return getattr(config, f"run_{source}", False)


def _run(jobs: list[tuple[str, object]]) -> list[str]:
    failures: list[str] = []
    for name, fn in jobs:
        print(f"── {name} ──────────────────────")
        try:
            fn()  # type: ignore[operator]
        except Exception:
            traceback.print_exc()
            failures.append(name)
    return failures
