import pytest

from src.game.bingo_cell import Cell
from src.game.bingo_grid import BingoGrid
from src.game.role import Role


def _make_cells(count: int, points: int = 10, checked: bool = False) -> list[Cell]:
    cells = []
    for index in range(count):
        cell_id = index + 1
        cell = Cell(
            id=cell_id,
            description=f"Cell {cell_id}",
            riot_stat_to_check="kills",
            target_value=1,
            role=Role.MID,
            points=points,
            is_checked=checked,
        )
        cells.append(cell)
    return cells

def test_build_grid_creates_five_rows_of_five_cells() -> None:
    available = _make_cells(count=25)
    bingo_grid = BingoGrid(
        player_discord_id="123456",
        role=Role.MID,
        available_cells=available,
    )

    #tests rows numbers
    assert len(bingo_grid.grid) == 5

    #tests cells numbers in each row
    for row in bingo_grid.grid:
        assert len(row) == 5

def test_build_grid_selects_unique_cell_ids() -> None:
    available = _make_cells(count=30)
    bingo_grid = BingoGrid(
        player_discord_id="123456",
        role=Role.MID,
        available_cells=available,
    )

    seen_ids = []
    for row in bingo_grid.grid:
        for cell in row:
            seen_ids.append(cell.id)

    assert len(seen_ids) == 25

    #creating a set to delete duplicates
    assert len(set(seen_ids)) == 25


