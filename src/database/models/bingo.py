from dataclasses import dataclass, field

from src.database.models.mini_game import MiniGame


@dataclass
class BingoCell:
    description: str
    riot_stat_to_check: str
    target_value: int
    is_checked: bool = False


@dataclass
class BingoGrid:
    player_discord_id: str
    cells: list[BingoCell] = field(default_factory=list)


class Bingo(MiniGame):
    __mapper_args__ = {
        "polymorphic_identity": "BINGO",
    }
