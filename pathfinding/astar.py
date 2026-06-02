from heapq import heappop, heappush

from models.task import Position
from models.warehouse import Warehouse


def astar_path(warehouse: Warehouse, start: Position, goal: Position) -> list[Position]:
    if start == goal:
        return [start]
    if not warehouse.is_passable(start) or not warehouse.is_passable(goal):
        return []

    open_set: list[tuple[int, Position]] = []
    heappush(open_set, (0, start))
    came_from: dict[Position, Position | None] = {start: None}
    cost_so_far: dict[Position, int] = {start: 0}

    while open_set:
        _, current = heappop(open_set)
        if current == goal:
            return _reconstruct_path(came_from, goal)

        for neighbor in warehouse.neighbors(current):
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + manhattan_distance(neighbor, goal)
                heappush(open_set, (priority, neighbor))
                came_from[neighbor] = current

    return []


def manhattan_distance(a: Position, b: Position) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _reconstruct_path(came_from: dict[Position, Position | None], goal: Position) -> list[Position]:
    path = [goal]
    current = goal
    while came_from[current] is not None:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

