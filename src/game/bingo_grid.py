from dataclasses import dataclass

from bingo_cell import Cell
from role import Role

@dataclass
class BingoGrid:
    player_discord_id: str
    role: Role
    cells: list[list[Cell]]
    size: int = 5
    line_bonus_step: float = 0.25

    def _count_completed_lines(self) -> int:
        completed = 0

        completed += self._count_completed_rows()



    def _count_completed_rows(self) -> int:
        completed = 0
        for row in self.cells:
            if all(cell.is_checked for cell in row):
                completed += 1

        return completed