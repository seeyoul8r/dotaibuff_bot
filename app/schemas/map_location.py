from dataclasses import dataclass


@dataclass
class MapLocationPoint:
    """Store calibrated Dota map location point."""
    slug: str
    xpos: int
    ypos: int
    radius: int
    radius_y: int | None = None
    rotation: int = 0
