from __future__ import annotations

from models.task import Position


class Warehouse:
    PASSABLE_SYMBOLS = {0, "0", "S", "P", "D"}

    def __init__(self, grid: list[list[object]]) -> None:
        if not grid or not grid[0]:
            raise ValueError("Warehouse grid cannot be empty.")
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0])
        if any(len(row) != self.width for row in grid):
            raise ValueError("Warehouse grid rows must have equal length.")

        self.start_positions = self._find_positions("S")
        self.pickup_points = self._find_positions("P")
        self.delivery_points = self._find_positions("D")

    def _find_positions(self, symbol: str) -> list[Position]:
        positions: list[Position] = []
        for row_index, row in enumerate(self.grid):
            for col_index, value in enumerate(row):
                if value == symbol:
                    positions.append((row_index, col_index))
        return positions

    def in_bounds(self, position: Position) -> bool:
        row, col = position
        return 0 <= row < self.height and 0 <= col < self.width

    def is_passable(self, position: Position) -> bool:
        if not self.in_bounds(position):
            return False
        row, col = position
        return self.grid[row][col] in self.PASSABLE_SYMBOLS

    def neighbors(self, position: Position) -> list[Position]:
        row, col = position
        candidates = [
            (row - 1, col),
            (row + 1, col),
            (row, col - 1),
            (row, col + 1),
        ]
        return [candidate for candidate in candidates if self.is_passable(candidate)]

    @classmethod
    def create_default(cls, width: int = 20, height: int = 20) -> "Warehouse":
        if width < 10 or height < 10:
            raise ValueError("Default warehouse requires at least a 10x10 grid.")

        grid: list[list[object]] = [[0 for _ in range(width)] for _ in range(height)]

        rack_columns = [4, 8, 12, 16]
        open_rows = {0, 1, 5, 10, 15, height - 2, height - 1}
        for col in rack_columns:
            if col >= width:
                continue
            for row in range(2, height - 2):
                if row not in open_rows:
                    grid[row][col] = 1

        starts = [(1, 1), (1, 18), (18, 1), (18, 18), (10, 1), (10, 18), (5, 1), (15, 18)]
        pickups = [(3, 2), (3, 6), (3, 10), (3, 14), (7, 2), (7, 6), (7, 10), (7, 14), (13, 2), (13, 6)]
        deliveries = [(18, 9), (18, 10), (1, 9), (1, 10), (10, 9), (10, 10)]

        for row, col in starts:
            if row < height and col < width:
                grid[row][col] = "S"
        for row, col in pickups:
            if row < height and col < width:
                grid[row][col] = "P"
        for row, col in deliveries:
            if row < height and col < width:
                grid[row][col] = "D"

        return cls(grid)

