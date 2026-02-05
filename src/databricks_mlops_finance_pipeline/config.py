from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineConfig:
    """Central configuration (keep it simple and override via env if needed)."""
    target_column: str = "y"
    date_column: str = "ds"
