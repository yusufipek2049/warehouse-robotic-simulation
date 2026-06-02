from models.robot import Robot
from models.task import Task
from pathfinding.astar import manhattan_distance


class Scheduler:
    def assign_waiting_tasks(self, robots: list[Robot], tasks: list[Task], current_time: int) -> None:
        waiting_tasks = [task for task in tasks if task.status == "waiting"]
        if not waiting_tasks:
            return

        for robot in sorted(robots, key=lambda item: item.robot_id):
            if robot.status != "idle" or not waiting_tasks:
                continue

            task = min(
                waiting_tasks,
                key=lambda item: (
                    manhattan_distance(robot.current_position, item.pickup_location),
                    item.task_id,
                ),
            )
            robot.assign_task(task, current_time)
            waiting_tasks.remove(task)

