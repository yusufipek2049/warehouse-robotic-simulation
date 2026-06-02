from collections.abc import Callable

from models.robot import Robot
from models.task import Position, Task
from models.warehouse import Warehouse
from pathfinding.bfs import bfs_path
from simulation.collision import resolve_moves
from simulation.scheduler import Scheduler


Pathfinder = Callable[[Warehouse, Position, Position], list[Position]]


class SimulationEngine:
    def __init__(
        self,
        warehouse: Warehouse,
        robots: list[Robot],
        tasks: list[Task],
        pathfinder: Pathfinder = bfs_path,
        max_steps: int = 10_000,
    ) -> None:
        if not robots:
            raise ValueError("Simulation requires at least one robot.")
        if not tasks:
            raise ValueError("Simulation requires at least one task.")
        if max_steps <= 0:
            raise ValueError("max_steps must be greater than zero.")

        self.warehouse = warehouse
        self.robots = robots
        self.tasks = tasks
        self.pathfinder = pathfinder
        self.max_steps = max_steps
        self.scheduler = Scheduler()
        self.current_time = 0
        self.history: list[dict[str, float | int]] = []

    def run(self) -> dict[str, object]:
        while not self.all_tasks_completed() and self.current_time < self.max_steps:
            self.step()

        if not self.all_tasks_completed():
            raise RuntimeError(
                f"Simulation stopped at max_steps={self.max_steps} before all tasks completed."
            )

        return {
            "total_time": self.current_time,
            "robots": self.robots,
            "tasks": self.tasks,
            "history": self.history,
        }

    def step(self) -> None:
        for robot in self.robots:
            robot.restore_motion_status()

        self.scheduler.assign_waiting_tasks(self.robots, self.tasks, self.current_time)
        self._prepare_routes()

        desired_moves = self._get_desired_moves()
        allowed_moves, blocked_robot_ids = resolve_moves(self.robots, desired_moves)

        for robot in self.robots:
            if robot.robot_id in allowed_moves:
                robot.current_position = allowed_moves[robot.robot_id]
                if robot.route:
                    robot.route.pop(0)
                robot.total_distance += 1
                robot.active_time += 1
            elif robot.robot_id in blocked_robot_ids:
                robot.waiting_time += 1
                robot.blocked_count += 1
                robot.status = "waiting"

        event_time = self.current_time + 1
        self._update_task_states(event_time)
        self.current_time = event_time
        self._record_history()

    def all_tasks_completed(self) -> bool:
        return all(task.status == "completed" for task in self.tasks)

    def _prepare_routes(self) -> None:
        for robot in self.robots:
            if robot.status not in {"to_pickup", "to_delivery"} or robot.target_position is None:
                continue
            if robot.current_position == robot.target_position:
                robot.route = []
                continue
            if not robot.route:
                path = self.pathfinder(self.warehouse, robot.current_position, robot.target_position)
                if not path:
                    raise RuntimeError(
                        f"No route found for robot {robot.robot_id}: "
                        f"{robot.current_position} -> {robot.target_position}"
                    )
                robot.route = path[1:]

    def _get_desired_moves(self) -> dict[int, Position | None]:
        desired_moves: dict[int, Position | None] = {}
        for robot in self.robots:
            if robot.status in {"to_pickup", "to_delivery"} and robot.route:
                desired_moves[robot.robot_id] = robot.route[0]
            else:
                desired_moves[robot.robot_id] = None
        self._add_idle_yield_moves(desired_moves)
        return desired_moves

    def _add_idle_yield_moves(self, desired_moves: dict[int, Position | None]) -> None:
        requested_targets = {
            target
            for robot_id, target in desired_moves.items()
            if target is not None and self._robot_by_id(robot_id).status != "idle"
        }
        occupied_positions = {robot.current_position for robot in self.robots}

        for robot in self.robots:
            if robot.status != "idle" or robot.current_position not in requested_targets:
                continue
            for neighbor in self.warehouse.neighbors(robot.current_position):
                if neighbor in occupied_positions or neighbor in requested_targets:
                    continue
                desired_moves[robot.robot_id] = neighbor
                occupied_positions.add(neighbor)
                break

    def _robot_by_id(self, robot_id: int) -> Robot:
        for robot in self.robots:
            if robot.robot_id == robot_id:
                return robot
        raise KeyError(f"Unknown robot_id: {robot_id}")

    def _update_task_states(self, event_time: int) -> None:
        for robot in self.robots:
            task = robot.assigned_task
            if task is None:
                continue

            if task.status == "assigned" and robot.current_position == task.pickup_location:
                task.status = "picked_up"
                robot.status = "to_delivery"
                robot.target_position = task.delivery_location
                robot.route = []
            elif task.status == "picked_up" and robot.current_position == task.delivery_location:
                task.status = "completed"
                task.completed_at = event_time
                robot.clear_task()

    def _record_history(self) -> None:
        completed_tasks = sum(task.status == "completed" for task in self.tasks)
        waiting_tasks = sum(task.status == "waiting" for task in self.tasks)
        active_robots = sum(robot.status in {"to_pickup", "to_delivery"} for robot in self.robots)
        blocked_robots = sum(robot.status == "waiting" for robot in self.robots)
        self.history.append(
            {
                "time": self.current_time,
                "waiting_tasks": waiting_tasks,
                "completed_tasks": completed_tasks,
                "active_robots": active_robots,
                "blocked_robots": blocked_robots,
            }
        )
