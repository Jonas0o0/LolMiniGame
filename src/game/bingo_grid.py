from dataclasses import dataclass, field
import random

from .bingo_cell import Cell
from .role import Role

@dataclass
class BingoGrid:
    player_discord_id: str
    role: Role
    available_cells: list[Cell]
    size: int = 5
    line_bonus: float = 0.2
    grid: list[list[Cell]] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self._build_grid()

    def _build_grid(self):
        total_cells = self.size ** 2
        if len(self.available_cells) < total_cells:
            raise ValueError(
                f"Not enough cells to build a {self.size}x{self.size} grid: "
                f"expected minimum {total_cells} cells, got {len(self.available_cells)}.")

        selected = random.sample(self.available_cells, total_cells)

        grid = []
        for row in range(self.size):
            start = row * self.size
            end = (row + 1) * self.size
            line = selected[start:end]
            grid.append(line)

        self.grid = grid

    def _count_completed_lines(self) -> int:
        completed = 0

        completed += self._count_completed_rows() + self._count_completed_columns() + self._count_completed_diagonals()

        return completed


    def _count_completed_rows(self) -> int:
        completed = 0
        for row in self.grid:
            if all(cell.is_checked for cell in row):
                completed += 1

        return completed

    def _count_completed_columns(self) -> int:
        completed = 0
        for col in range(self.size):
            if all(self.grid[row][col].is_checked for row in range(self.size)):
                completed += 1

        return completed

    def _count_completed_diagonals(self) -> int:
        completed = 0

        if all(self.grid[i][i].is_checked for i in range(self.size)):
            completed += 1

        if all(self.grid[i][self.size - 1 - i].is_checked for i in range(self.size)):
            completed += 1

        return completed

    def calculate_score(self) -> int:
        base_points = 0

        for row in self.grid:
            for cell in row:
                if cell.is_checked:
                    base_points += cell.points

        completed_lines = self._count_completed_lines()

        multiplier = 1.0 + completed_lines * self.line_bonus

        return round(base_points * multiplier)