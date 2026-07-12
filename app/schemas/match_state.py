from dataclasses import asdict, dataclass, field


@dataclass
class MatchHeroState:
    """Store hero state inside accumulated match state."""
    team: str | None
    sources: list = field(default_factory=list)
    first_seen_at: str | None = None
    last_seen_at: str | None = None
    was_visible: bool = False
    visible: bool = False
    last_seen_game_time: int | None = None
    last_seen_position: dict | None = None
    last_seen_location: str = 'unknown'
    last_seen_image: str | None = None

    def to_dict(self):
        """Return dict for Redis JSON storage."""
        return asdict(self)
