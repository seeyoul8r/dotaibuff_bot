from pydantic import BaseModel


class GameAdvice(BaseModel):
    """Structured Dota game advice."""
    macro_gaming: str
    build: str
    micro_gaming: str
