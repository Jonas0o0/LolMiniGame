from dataclasses import dataclass, field
from src.models.BingoCell import BingoCell


@dataclass
class BingoGrid:
    player_discord_id: str
    cells: list[BingoCell] = field(default_factory=list)
