from dataclasses import dataclass
from .role import Role

@dataclass
class Cell:
    """ Represents a single cell in a bingo grid"""
    id: int
    description: str
    riot_stat_to_check: str
    target_value: int
    role: Role
    points: int
    is_checked: bool = False

    def evaluate_condition(self, stats: dict[str, int | float]) -> bool:
        """ Evaluates whether this cell is checked or unchecked"""
        current_value = stats.get(self.riot_stat_to_check, 0)
        self.is_checked = current_value >= self.target_value
        return self.is_checked