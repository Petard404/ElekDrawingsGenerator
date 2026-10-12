"""Drawing dimensions with defaults and an optional override file."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Every dimension in mm. Fields are added as milestones need them."""

    page_width_mm: float = 210.0
    page_height_mm: float = 297.0
    font_family: str = "Helvetica"
    default_stroke_mm: float = 0.25
    symbol_stroke_mm: float = 0.26
