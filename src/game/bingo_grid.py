from dataclasses import dataclass

from bingo_cell import Cell
from role import Role

@dataclass
class BingoGrid:
    player_discord_id: str
    role: Role
    cells: list[list[Cell]]
    size: int = 5
    line_bonus_step: float = 0.2

    def _count_completed_lines(self) -> int:
        completed = 0

        completed += self._count_completed_rows() + self._count_completed_columns() + self._count_completed_diagonals()

        return completed


    def _count_completed_rows(self) -> int:
        completed = 0
        for row in self.cells:
            if all(cell.is_checked for cell in row):
                completed += 1

        return completed

    def _count_completed_columns(self) -> int:
        completed = 0
        for col in range(self.size):
            if all(self.cells[row][col].is_checked for row in range(self.size)):
                completed += 1

        return completed

    def _count_completed_diagonals(self) -> int:
        completed = 0

        if all(self.cells[i][i].is_checked for i in range(self.size)):
            completed += 1

        if all(self.cells[i][self.size - 1 - i].is_checked for i in range(self.size)):
            completed += 1

        return completed