from dataclasses import dataclass


@dataclass
class BingoCell:
    description: str
    riot_stat_to_check: str
    target_value: int
    is_checked: bool = False
