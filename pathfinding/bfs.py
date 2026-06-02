from collections import deque

from models.task import Position
from models.warehouse import Warehouse


def bfs_path(warehouse: Warehouse, start: Position, goal: Position) -> list[Position]:
    return bfs_path_with_blocked(warehouse, start, goal, blocked_positions=set())


def bfs_path_with_blocked(
    warehouse: Warehouse,
    start: Position,
    goal: Position,
    blocked_positions: set[Position],
) -> list[Position]:
    if start == goal:
        return [start]
    if not warehouse.is_passable(start) or not warehouse.is_passable(goal):
        return []

    queue: deque[Position] = deque([start])
    previous: dict[Position, Position | None] = {start: None}

    while queue:
        current = queue.popleft()
        for neighbor in warehouse.neighbors(current):
            if neighbor in blocked_positions and neighbor != goal:
                continue
            if neighbor in previous:
                continue
            previous[neighbor] = current
            if neighbor == goal:
                return _reconstruct_path(previous, goal)
            queue.append(neighbor)

    return []


def _reconstruct_path(previous: dict[Position, Position | None], goal: Position) -> list[Position]:
    path = [goal]
    current = goal
    while previous[current] is not None:
        current = previous[current]
        path.append(current)
    path.reverse()
    return path
